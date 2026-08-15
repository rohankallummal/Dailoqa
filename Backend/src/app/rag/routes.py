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
from functools import lru_cache
from pathlib import Path

from app.config import get_settings

logger = logging.getLogger(__name__)

__all__ = ["route_for", "reset_route_cache"]

_MANIFEST_NAME = "manifest.json"


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


def reset_route_cache() -> None:
    """Drop the cached manifest. For tests that point ``DOCS_PATH`` somewhere else."""
    _routes.cache_clear()
