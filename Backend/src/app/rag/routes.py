"""Maps an indexed chunk back to the documentation page a reader can actually open.

A chunk knows its ``source_path`` (``deep-agents/subagents.md``) but a citation has to name
something clickable (``/docs/deepagents/subagents``), and the two are not derivable from one
another. Five of the eighteen pages differ by more than the topic folder's spelling —
``multimodal`` renders at ``/multimodality``, ``middleware/built-in`` at
``/prebuilt-middleware``, ``use-subgraphs`` at ``/subgraphs``, ``checkpointers`` at
``/checkpoints``, and each ``overview`` at a bare topic route. Guessing the route from the
filename would therefore misdirect roughly a quarter of all citations.

``docs-corpus/manifest.json`` is the join table that records the mapping, and it is found
relative to ``DOCS_PATH`` rather than by its own setting, so pointing the corpus somewhere else
moves the manifest with it instead of silently leaving a stale one behind.

**A missing entry is not fatal.** Retrieval keeps working and the citation falls back to the
filename label; see ``citation_label`` in ``store.py``. An answer carrying a slightly stale-looking
source beats no answer at all, and ``docs-formatter/check_mapping.py`` is what is relied on to
catch the drift before a reader ever sees it.
"""

import json
import logging
import re
from functools import lru_cache
from pathlib import Path

from app.config import get_settings

logger = logging.getLogger(__name__)

__all__ = ["route_for", "anchor_for", "cited_url", "reset_route_cache"]

_MANIFEST_NAME = "manifest.json"

# The docs site gives every h2 and h3 an id from `github-slugger`. Its order matters and is
# reproduced exactly: lowercase, drop punctuation, then map each remaining space to one hyphen.
# Runs are deliberately NOT collapsed -- dropping the slash in "Row key / index design" leaves
# two adjacent spaces, and the real anchor on the page is "row-key--index-design". Collapsing
# them produced a single hyphen and a fragment that scrolled nowhere.
_NON_SLUG = re.compile(r"[^\w\s-]")
_SPACE = re.compile(r"\s")

# Mirrors store.INTRO_HEADING. Duplicated rather than imported because store imports this
# module, and a page's lead-in is not a heading on the page, so it has no anchor to link to.
# `test_the_intro_sentinel_matches_store` fails if the two ever drift apart.
_INTRO_HEADING = "(intro)"


def _manifest_path() -> Path:
    """``manifest.json`` beside the corpus directory that ``DOCS_PATH`` names."""
    configured = Path(get_settings().docs_path)
    if not configured.is_absolute():
        configured = Path(__file__).resolve().parents[3] / configured  # .../Backend
    return configured.parent / _MANIFEST_NAME


@lru_cache(maxsize=1)
def _routes() -> dict[str, str]:
    """``{vault_path: frontend_route}``, empty if the manifest is missing or unreadable.

    Degrading to empty rather than raising is deliberate: a malformed manifest should cost
    clickable citations, not the ability to answer at all.
    """
    path = _manifest_path()
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.warning("rag.routes no manifest at %s; citations will name files", path)
        return {}
    except (OSError, json.JSONDecodeError):
        logger.exception("rag.routes could not read %s; citations will name files", path)
        return {}
    return {
        page["vault_path"]: page["frontend_route"]
        for page in manifest.get("pages", [])
        if page.get("vault_path") and page.get("frontend_route")
    }


def route_for(source_path: str) -> str | None:
    """The documentation route for an indexed page, or None when it is not mapped."""
    return _routes().get(source_path)


def anchor_for(heading: str | None) -> str | None:
    """The page anchor for a chunk's heading, or None when there is nothing to link to.

    Headings arrive as a trail — ``"Context management > Summarization"`` — and only the leaf
    names the section actually rendered, so the trail is discarded first.

    **Right for 253 of the 256 headings in the corpus, measured against the live pages.** All
    three misses are one page and one cause: the docs site renders both the ``:::python`` and
    ``:::js`` arm, so a heading appearing in both is disambiguated into ``working-with-files``
    and ``working-with-files-1`` while only one arm is ever visible. The corpus keeps a single
    arm and cannot know which suffix survived. Getting those wrong costs a link that lands on
    the right page without scrolling, which is exactly what citing the bare page did anyway —
    a lost improvement rather than a new defect, and not worth scraping the rendered frontend
    at build time to avoid.
    """
    if not heading or heading == _INTRO_HEADING:
        return None
    leaf = heading.split(" > ")[-1].strip()
    slug = _SPACE.sub("-", _NON_SLUG.sub("", leaf.lower()))
    return slug or None


def cited_url(source_path: str, heading: str | None) -> str | None:
    """The documentation URL for a passage: the page, and the section within it."""
    route = route_for(source_path)
    if route is None:
        return None
    anchor = anchor_for(heading)
    return f"{route}#{anchor}" if anchor else route


def reset_route_cache() -> None:
    """Drop the cached manifest. For tests that point ``DOCS_PATH`` somewhere else."""
    _routes.cache_clear()
