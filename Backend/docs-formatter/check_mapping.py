"""Check that the corpus, the manifest, and the frontend's docs routes still agree.

Run from the Backend directory:

    python docs-formatter/check_mapping.py

Exits non-zero, listing every problem, if any of them have drifted apart.

**Why this exists.** A citation has to name a page the user can actually open. The chunk the
model quotes is identified by its vault path (``deep-agents/subagents.md``), but what a reader
needs is the route (``/docs/deepagents/subagents``), and the two are not derivable from one
another -- 5 of the 18 pages differ by more than the topic folder's spelling
(``multimodal`` -> ``multimodality``, ``middleware/built-in`` -> ``prebuilt-middleware``,
``use-subgraphs`` -> ``subgraphs``, ``checkpointers`` -> ``checkpoints``). ``manifest.json`` is
the join table that carries that mapping, and a join table is only trustworthy while every row
still points at something real on both sides.

Nothing else notices when it stops being true. A page renamed in the frontend, or a vault
refreshed to a newer upstream commit, leaves the manifest quietly stale, and the first symptom is
a user clicking a citation that 404s. This check turns that into a failure you get on demand
instead of one a reader finds for you.

Deliberately standalone -- stdlib only, no ``app.*`` imports -- so it runs without the backend's
dependencies, database, or settings.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_REPO_ROOT = _BACKEND_ROOT.parent

_MANIFEST = _BACKEND_ROOT / "docs-corpus" / "manifest.json"
_FORMATTED = _BACKEND_ROOT / "docs-corpus" / "formatted"
_DOCS_ROUTES = _REPO_ROOT / "Frontend" / "src" / "app" / "docs"

_REL_PATH_RE = re.compile(r'relPath="([^"]+)"')


def _frontend_routes() -> dict[str, str]:
    """Every docs route that renders a page, mapped to the content file it declares.

    A route without a ``relPath`` prop (the ``/docs`` index) renders no single document and is
    not something a chunk can cite, so it is skipped rather than reported as unmapped.
    """
    routes: dict[str, str] = {}
    for page in sorted(_DOCS_ROUTES.rglob("page.tsx")):
        match = _REL_PATH_RE.search(page.read_text(encoding="utf-8"))
        if match:
            route = "/" + page.relative_to(_DOCS_ROUTES.parent).parent.as_posix()
            routes[route] = match.group(1)
    return routes


def check() -> list[str]:
    """Return a list of problems; empty means the three sides agree."""
    problems: list[str] = []

    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    pages = manifest["pages"]
    routes = _frontend_routes()

    for page in pages:
        vault_path, route = page["vault_path"], page["frontend_route"]

        if not (_FORMATTED / vault_path).is_file():
            problems.append(f"manifest names a missing corpus file: {vault_path}")

        if route not in routes:
            problems.append(f"manifest names a route with no page.tsx: {route} (for {vault_path})")
        elif routes[route] != page["frontend_rel_path"]:
            problems.append(
                f"route {route} renders {routes[route]!r} but the manifest claims "
                f"{page['frontend_rel_path']!r}"
            )

    mapped_vault = {p["vault_path"] for p in pages}
    for found in sorted(_FORMATTED.rglob("*.md")):
        rel = found.relative_to(_FORMATTED).as_posix()
        if rel not in mapped_vault:
            problems.append(f"corpus file has no manifest entry, so it can never cite a page: {rel}")

    mapped_routes = {p["frontend_route"] for p in pages}
    for route in sorted(routes):
        if route not in mapped_routes:
            problems.append(f"docs route has no manifest entry, so nothing can ever cite it: {route}")

    return problems


def main() -> int:
    problems = check()
    if problems:
        print(f"{len(problems)} problem(s):", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    print(
        f"OK: {len(manifest['pages'])} pages agree across corpus, manifest and frontend routes "
        f"(upstream {manifest['upstream_sha'][:7]})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
