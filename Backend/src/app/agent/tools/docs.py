"""Tools that let the agent read the product documentation.

Retrieval is hybrid — semantic (pgvector) and lexical (Postgres full-text) arms fused by
reciprocal rank, each gated on an absolute relevance threshold before fusion — so a query
about something the documentation does not cover comes back empty rather than with the
nearest unrelated passage. See ``app.rag.store``.

Every passage handed to the model carries a ``[Doc N]`` tag. The numbering is assigned
here rather than by the model so that citations stay stable across several tool calls in
one turn; see ``_cite``.
"""

from langchain.tools import ToolRuntime, tool

from app.config import get_settings
from app.db.base import async_session
from app.rag.embeddings import aembed_query
from app.rag.store import (
    INTRO_HEADING,
    citation_label,
    fetch_section,
    list_sources,
    search,
    strip_context_prefix,
)

DOC_SKILL_NAME = "documentation-qa"
"""The skill whose instructions drive these tools; hidden when the capability is off."""

CITING_DOC_TOOLS = frozenset({"search_documentation", "fetch_document_section"})
"""The tools that hand the model passages it can legitimately cite.

The grounding middleware counts **only** these. ``list_documentation_sources`` returns an
inventory of titles and headings — no passages — so an answer citing `[Doc 1]` after an
inventory call alone is citing something it never read. Counting the inventory tool as
evidence would let exactly that through.
"""

DOC_TOOL_NAMES = frozenset(CITING_DOC_TOOLS | {"list_documentation_sources"})
"""Every tool that reads the documentation, citing or not.

Used to decide whether the documentation skill's instructions should be auto-loaded: any
documentation activity implies the agent needs the procedure, even a bare inventory call.
"""

NO_MATCH = (
    "Nothing in the documentation matches that. Tell the user the documentation does not "
    "cover it rather than answering from your own knowledge."
)

_LOAD_SKILL = "load_skill"


def _tool_calls(messages):
    """Every tool call across a thread's messages."""
    for message in messages:
        yield from getattr(message, "tool_calls", None) or []


def documentation_tool_used(messages) -> bool:
    """Whether any documentation tool has been called in this thread.

    The whole thread counts rather than the current turn: passages retrieved earlier are
    still in the conversation, so a later answer built on them is properly grounded.
    """
    return any(call.get("name") in DOC_TOOL_NAMES for call in _tool_calls(messages))


def citable_passages_retrieved(messages) -> bool:
    """Whether the thread ever received passages the model could legitimately cite.

    Deliberately narrower than :func:`documentation_tool_used`: browsing the inventory is
    documentation activity, but it hands over no passages, so it cannot justify a `[Doc N]`.
    """
    return any(call.get("name") in CITING_DOC_TOOLS for call in _tool_calls(messages))


def documentation_skill_loaded(messages) -> bool:
    """Whether the documentation skill's instructions are already in the transcript."""
    return any(
        call.get("name") == _LOAD_SKILL and (call.get("args") or {}).get("name") == DOC_SKILL_NAME
        for call in _tool_calls(messages)
    )


def _cite(runtime: ToolRuntime, chunk_ids: list[str]) -> int:
    """Return the ``[Doc N]`` number for a passage, assigning one on first sight.

    Numbers are per turn and monotonic, and every chunk of a passage maps to the same
    number. Because the turn context is shared across tool calls, a section fetched after
    it was searched — or searched again with different wording — keeps the number the
    model has already written into its prose.
    """
    citations = runtime.context.citations
    for chunk_id in chunk_ids:
        existing = citations.get(chunk_id)
        if existing is not None:
            for other in chunk_ids:
                citations.setdefault(other, existing)
            return existing
    number = max(citations.values(), default=0) + 1
    for chunk_id in chunk_ids:
        citations[chunk_id] = number
    return number


@tool
async def search_documentation(query: str, runtime: ToolRuntime) -> str:
    """Search the product documentation and return the passages that match.

    This is the usual way in. Search before answering any question about the product,
    and search again with different wording if the first results look thin — the query
    is matched on both meaning and exact terms, so precise product nouns work well.

    Args:
        query: A standalone question or phrase. Resolve pronouns from the conversation
            first: search "how does Deep Agents memory work", never "how does it work".
    """
    settings = get_settings()
    async with async_session() as session:
        vector = await aembed_query(query)
        chunks = await search(session, query, vector, settings.rag_top_k)

    if not chunks:
        return NO_MATCH

    blocks = []
    for chunk in chunks:
        number = _cite(runtime, [chunk.id])
        body = strip_context_prefix(chunk.content, chunk.source_path, chunk.title, chunk.heading)
        label = citation_label(chunk.source_path, chunk.title, chunk.heading)
        blocks.append(f"[Doc {number}: {label}]\n{body}")
    return "\n\n".join(blocks)


@tool
async def list_documentation_sources(runtime: ToolRuntime) -> str:
    """List every documentation page and the sections inside it.

    Use this when you are unsure what the documentation covers, or to find the exact
    section name to pass to `fetch_document_section`. It returns an inventory only —
    no passages to cite, so follow it with a search or a fetch.
    """
    async with async_session() as session:
        outlines = await list_sources(session)

    if not outlines:
        return "The documentation corpus is empty."

    lines = []
    for outline in outlines:
        lines.append(f"{outline.source_path} - {outline.title or 'untitled'}")
        lines.extend(f"  - {heading}" for heading in outline.headings)
    return "\n".join(lines)


@tool
async def fetch_document_section(source_path: str, heading: str, runtime: ToolRuntime) -> str:
    """Read one whole section of a documentation page.

    Search returns the most relevant fragments; fetch returns the entire section they
    came from. Reach for it when an answer needs a full procedure or table rather than
    the snippet a search surfaced.

    Args:
        source_path: The page's file name, exactly as `list_documentation_sources` or a
            search result gives it, e.g. "deepagents-overview.mdx".
        heading: The section name, copied exactly from the same place. Pass "(intro)"
            for the text before a page's first heading.
    """
    async with async_session() as session:
        section = await fetch_section(session, source_path, heading)

    if section is None:
        return (
            f"No section '{heading}' in {source_path}. "
            "Call list_documentation_sources to see the sections that exist."
        )

    number = _cite(runtime, section.chunk_ids)
    label = citation_label(section.source_path, section.title, section.heading or INTRO_HEADING)
    return f"[Doc {number}: {label}]\n{section.content}"
