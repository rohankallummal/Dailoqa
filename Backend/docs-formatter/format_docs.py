"""Format Mintlify MDX pages into plain Markdown notes.

Run from the Backend directory:

    python docs-formatter/format_docs.py
    python docs-formatter/format_docs.py --in docs-corpus/raw --out docs-corpus/formatted
    python docs-formatter/format_docs.py --language js --dry-run

Reads every ``.md``/``.mdx`` under the input directory, reduces Mintlify MDX to plain
Markdown, and writes the result as ``.md`` under the output directory, preserving the folder
structure. Input files are never modified.

**This script is deliberately self-contained** — stdlib only, no ``app.*`` imports. The
normalizer rules below are a *copy* of the ones in ``src/app/rag/ingest.py`` rather than an
import, so that formatting notes on disk stays independent of the ingest pipeline and neither
can break the other. The cost of that choice is real: the two copies can drift. If you change
a rule in one, change it in the other.

The two rules worth knowing before reading the code:

* **Code is masked first and restored last.** Every prose substitution runs against text whose
  fenced and inline code has been swapped out for placeholders, because otherwise a rule
  written for prose reaches into a code sample — ``<[^>]+>`` turns ``#include <vector>`` into
  ``#include``, silently.
* **Only one language survives.** LangChain documents most concepts twice, in ``:::python``
  and ``:::js`` blocks. Keeping both restates every idea and lets a Python question be
  answered in TypeScript, so the unwanted language is dropped whole rather than unmarked.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# --- normalizer rules (mirror of src/app/rag/ingest.py) --------------------------------

_FRONTMATTER_RE = re.compile(r"^﻿?---\s*\n(.*?)\n---\s*\n", re.DOTALL)
# Leading whitespace allowed, for the same reason as the ::: rules: MDX imports can sit inside an
# indented component block. Also narrowed to require a quoted module path -- every one of the 160
# in the corpus is `import X from '...'` -- so an indented line of prose merely beginning with the
# word "import" is not deleted wholesale.
_IMPORT_EXPORT_RE = re.compile(r"^[ \t]*(?:import|export)\s[^\n]*['\"][^\n]*$", re.MULTILINE)
_MDX_COMMENT_RE = re.compile(r"\{/\*.*?\*/\}", re.DOTALL)

# Only JSX *components* — Mintlify's are capitalised (<CodeGroup>, <Tip>, <Accordion>) — plus
# the handful of lowercase HTML tags these pages actually use. A blanket `<[^>]+>` would also
# eat CommonMark autolinks such as <https://x.com> and <a@b.com>.
_JSX_TAG_RE = re.compile(r"</?[A-Z][\w.]*(?:\s[^>]*)?/?>|</?(?:br|hr|img|a|p|div|span)(?:\s[^>]*)?/?>")

# LangChain's own language switches. The trailing newline is deliberately NOT consumed by the
# fence rule below, so a ":::" closing a block stays at the start of its line for this to match.
# Leading whitespace is allowed on purpose. These directives are frequently nested inside a
# <Steps> or <Tabs> component and therefore indented, and anchoring hard at "^:::" skipped every
# one of those -- leaving 25 :::js blocks, 24KB of TypeScript, in a Python-only corpus.
_DIRECTIVE_BLOCK_RE = re.compile(
    r"^[ \t]*:::(\w+)[ \t]*\n(.*?)^[ \t]*:::[ \t]*$\n?", re.DOTALL | re.MULTILINE
)
_STRAY_DIRECTIVE_RE = re.compile(r"^[ \t]*:::.*$", re.MULTILINE)

# `[Text](/oss/langchain/agents)` would otherwise push the URL's path segments into the note
# as though they were prose. Images are dropped outright.
_MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")

# `@[`create_deep_agent`]` is Mintlify's API-reference link. The brackets carry no meaning once
# the page is plain text, and they would enter the tsvector as punctuation noise around the one
# token a reader actually searches for, so keep the symbol and drop the wrapper.
_API_REF_RE = re.compile(r"@\[(`[^`\]]+`|[^\]]+)\]")

_BLANK_LINES_RE = re.compile(r"\n{3,}")

# Snippet plumbing. `import Foo from '/snippets/x-py.mdx';` pairs with a `<Foo />` in the body;
# the suffix on the filename is what decides which language arm a snippet belongs to.
# Leading whitespace allowed. This is the highest-stakes of the anchored rules: an unparsed
# import leaves its <Name /> unresolved, the JSX rule then strips the tag, and the code sample
# disappears with nothing to show it was ever referenced -- the same silent-loss failure the
# whole splicing step exists to prevent.
_SNIPPET_IMPORT_RE = re.compile(r"^[ \t]*import\s+(\w+)\s+from\s+'(/snippets/[^']+)'", re.MULTILINE)
_COMPONENT_TAG_RE = re.compile(r"<([A-Z][A-Za-z0-9]*)\s*/>")
_MAX_SNIPPET_DEPTH = 5
_SNIPPET_DIR = "_snippets"

_FENCE_RE = re.compile(r"^([ \t]*)(`{3,}|~{3,})[^\n]*\n.*?^\1?\2[ \t]*$", re.DOTALL | re.MULTILINE)
# Deliberately NOT re.DOTALL: an inline code span must stay on one line. With DOTALL a single
# unbalanced backtick -- `](https://...) in a link, say -- matches across paragraphs and swallows
# whatever lies between, including already-masked fences, which then never get restored.
_INLINE_CODE_RE = re.compile(r"(?<!`)(`+)(?!`)([^\n]+?)(?<!`)\1(?!`)")
_MASK = "\x00MASK{}\x00"
_MASK_RE = re.compile(r"\x00MASK(\d+)\x00")
_MAX_UNMASK_PASSES = 10


def parse_frontmatter(text: str) -> tuple[str, str]:
    """Split a leading YAML frontmatter block; return (frontmatter-with-fences, body).

    The frontmatter is returned intact rather than parsed: ingestion reads `title` out of it,
    so it is worth carrying through to the formatted page unchanged.
    """
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return "", text
    return match.group(0), text[match.end():]


def mask_code(text: str) -> tuple[str, list[str]]:
    """Replace fenced and inline code with placeholders; return the text and the originals.

    Fences are masked before inline code, or a lone backtick inside a fence would pair with
    another one and corrupt the block.
    """
    saved: list[str] = []

    def keep(match: re.Match) -> str:
        saved.append(match.group(0))
        return _MASK.format(len(saved) - 1)

    return _INLINE_CODE_RE.sub(keep, _FENCE_RE.sub(keep, text)), saved


def unmask_code(text: str, saved: list[str]) -> str:
    """Restore masked code verbatim.

    Loops rather than substituting once: ``re.sub`` does not rescan what it inserts, so a saved
    span that itself contains a placeholder would leave a raw ``\\x00MASK7\\x00`` in the output.
    That is a corrupt file rather than a cosmetic problem, so it is worth being defensive even
    though the inline-code rule above should no longer produce nesting.
    """
    for _ in range(_MAX_UNMASK_PASSES):
        text, changed = _MASK_RE.subn(lambda m: saved[int(m.group(1))], text)
        if not changed:
            return text
    raise RuntimeError("unmasking did not converge; masked code is nested more deeply than expected")


def select_language(text: str, keep: str) -> str:
    """Unwrap ``:::<keep>`` blocks and drop every other language block entirely."""

    def resolve(match: re.Match) -> str:
        language, body = match.group(1), match.group(2)
        return body if language == keep else ""

    return _DIRECTIVE_BLOCK_RE.sub(resolve, text)


def flatten_mdx(text: str, language: str) -> str:
    """Reduce Mintlify MDX to plain Markdown, leaving code samples untouched.

    Masking comes first and unmasking last; everything between operates only on prose.
    """
    text, saved = mask_code(text)
    text = select_language(text, language)
    text = _IMPORT_EXPORT_RE.sub("", text)
    text = _MDX_COMMENT_RE.sub("", text)
    text = _JSX_TAG_RE.sub("", text)
    text = _STRAY_DIRECTIVE_RE.sub("", text)  # unpaired markers the block rule could not match
    text = _API_REF_RE.sub(r"\1", text)  # before the link rule: @[x] has no (target) to match on
    text = _MD_IMAGE_RE.sub("", text)
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _BLANK_LINES_RE.sub("\n\n", text).strip()
    return unmask_code(text, saved)


def _snippet_language(path: str) -> str | None:
    """The language arm a snippet path belongs to, or None when it serves every language."""
    stem = path.rsplit("/", 1)[-1].removesuffix(".mdx")
    if stem.endswith("-py"):
        return "python"
    if stem.endswith("-js"):
        return "js"
    return None


def splice_snippets(text: str, snippet_root: Path | None, language: str, _depth: int = 0) -> str:
    """Inline `<Name />` placeholders with the snippet file their import points at.

    Mintlify keeps most code samples out of the page: the page imports a snippet and drops a
    `<Name />` where it should render. Both the import and the tag are markup, so without this
    step ``flatten_mdx`` strips them and the code silently disappears -- 148 samples across the
    18 pages, leaving one page with no code at all.

    Runs *before* ``flatten_mdx`` so spliced content goes through the same masking and stripping
    as the rest of the page. Snippets may import further snippets, so this recurses.

    Language selection happens here, by filename, mirroring the ``:::python``/``:::js`` rule:
    a ``-js`` snippet is dropped whole. Nothing is lost by that -- the four ``-js`` snippets with
    no ``-py`` sibling are all covered by a differently-named Python variant.
    """
    if snippet_root is None or _depth > _MAX_SNIPPET_DEPTH:
        return text

    imports = dict(_SNIPPET_IMPORT_RE.findall(text))
    if not imports:
        return text

    def resolve(match: re.Match) -> str:
        name = match.group(1)
        path = imports.get(name)
        if path is None:
            return match.group(0)  # a real component, not a snippet -- leave it for flatten_mdx
        if _snippet_language(path) not in (language, None):
            return ""
        source = snippet_root / path.lstrip("/")
        if not source.exists():
            raise FileNotFoundError(f"snippet not found: {path} (looked in {source})")
        nested = splice_snippets(source.read_text(encoding="utf-8"), snippet_root, language, _depth + 1)
        return f"\n{nested.strip()}\n"

    return _COMPONENT_TAG_RE.sub(resolve, text)


def format_document(text: str, language: str, snippet_root: Path | None = None) -> str:
    """Format one document, preserving its frontmatter and formatting only the body.

    Raises if a snippet placeholder survives splicing. Silence is the dangerous outcome here:
    an unresolved ``<Name />`` is stripped by the JSX rule a moment later, so the code sample it
    stood for would vanish leaving no trace that it had ever been referenced.
    """
    frontmatter, body = parse_frontmatter(text)
    if snippet_root is not None:
        imported = {name for name, _ in _SNIPPET_IMPORT_RE.findall(body)}
        body = splice_snippets(body, snippet_root, language)
        unresolved = {m.group(1) for m in _COMPONENT_TAG_RE.finditer(body)} & imported
        if unresolved:
            raise ValueError(f"snippet placeholders left unspliced: {sorted(unresolved)}")
    return f"{frontmatter}{flatten_mdx(body, language)}\n"


# --- CLI -------------------------------------------------------------------------------

_BACKEND_ROOT = Path(__file__).resolve().parent.parent


def _resolve(value: str) -> Path:
    """Interpret a path relative to the Backend root unless it is already absolute."""
    path = Path(value)
    return path if path.is_absolute() else _BACKEND_ROOT / path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--in", dest="source", default="docs-corpus/raw", help="input directory (default: %(default)s)")
    parser.add_argument("--out", dest="dest", default="docs-corpus/formatted", help="output directory (default: %(default)s)")
    parser.add_argument("--language", default="python", help="the ::: language arm to keep (default: %(default)s)")
    parser.add_argument("--dry-run", action="store_true", help="report what would be written without writing it")
    args = parser.parse_args(argv)

    source, dest = _resolve(args.source), _resolve(args.dest)
    if not source.is_dir():
        print(f"input directory does not exist: {source}", file=sys.stderr)
        return 1

    # _snippets/ holds the fragments pages pull in, not pages in their own right. They are
    # spliced into their referencing page and must never be formatted as standalone notes,
    # or the corpus gains ~150 contextless code stubs.
    snippet_root = source / _SNIPPET_DIR
    files = sorted(p for p in source.rglob("*")
                   if p.suffix.lower() in (".md", ".mdx") and snippet_root not in p.parents)
    if not files:
        print(f"no .md/.mdx files found under {source}", file=sys.stderr)
        return 1

    verb = "would format" if args.dry_run else "formatting"
    print(f"{verb} {len(files)} file(s): {source} -> {dest}  (language={args.language})")
    if not snippet_root.is_dir():
        print(f"  note: no {_SNIPPET_DIR}/ beside the pages - snippet code will not be inlined")
        snippet_root = None

    for path in files:
        formatted = format_document(path.read_text(encoding="utf-8"), args.language, snippet_root)
        target = (dest / path.relative_to(source)).with_suffix(".md")
        before, after = len(path.read_bytes()), len(formatted.encode("utf-8"))
        shrink = (1 - after / before) * 100 if before else 0.0
        print(f"  {target.relative_to(dest).as_posix():<40} {before:>7} -> {after:>7} bytes  ({shrink:4.1f}% smaller)")
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(formatted, encoding="utf-8")

    if args.dry_run:
        print("\ndry run - nothing written")
    else:
        print(f"\nwrote {len(files)} note(s) to {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
