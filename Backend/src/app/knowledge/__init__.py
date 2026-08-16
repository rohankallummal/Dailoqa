"""The documentation knowledge store the DocQA capability answers from.

``Backend/knowledge-store`` is an Open Knowledge Format bundle converted from the MDX
documentation under ``Frontend/src/features/docs/content/langdocs``. This package loads
it, splits pages into citable sections, and ranks those sections against a question.

The bundle is checked in and is now maintained by hand: the converter that produced it
has been removed, so a change to the source documentation does not reach the store on
its own.
"""

from app.knowledge.bundle import KNOWLEDGE_ROOT, Page, Section, outline, page, pages, sections
from app.knowledge.search import Hit, search

__all__ = [
    "KNOWLEDGE_ROOT",
    "Hit",
    "Page",
    "Section",
    "outline",
    "page",
    "pages",
    "search",
    "sections",
]
