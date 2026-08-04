"""Hybrid retrieval behaviour. Requires an ingested corpus (`python -m app.rag.ingest`)."""

from app.config import get_settings
from app.db.base import async_session
from app.rag.embeddings import aembed_query
from app.rag.store import INTRO_HEADING, fetch_section, list_sources, search


async def _search(query: str):
    async with async_session() as session:
        return await search(session, query, await aembed_query(query), get_settings().rag_top_k)


async def test_question_retrieves_the_right_section():
    results = await _search("What is a Skill?")
    assert results
    assert any(
        chunk.source_path == "deepagents-overview.mdx" and "Skills" in (chunk.heading or "")
        for chunk in results
    )


async def test_exact_term_is_ranked_first_by_the_lexical_arm():
    # A bare product noun is where semantic similarity is weakest and full-text is
    # strongest; fusion should still put the right section on top.
    results = await _search("MCP")
    assert results
    assert results[0].source_path == "deepagents-overview.mdx"
    assert "MCP" in (results[0].heading or "")


async def test_nonsense_matches_nothing():
    assert await _search("asdf qwerty zzz") == []


async def test_absent_topic_matches_nothing():
    # Plausible and on-topic, but genuinely not in the corpus: the gates must still
    # reject it, because this is what turns into a decline rather than an invention.
    assert await _search("How do I create a Playbook?") == []


async def test_list_sources_exposes_every_document_and_its_headings():
    async with async_session() as session:
        outlines = await list_sources(session)
    assert {outline.source_path for outline in outlines} == {
        "deepagents-overview.mdx",
        "langchain-overview.mdx",
        "langgraph-overview.mdx",
    }
    # A page's lead-in has no heading of its own and must still be nameable.
    assert all(INTRO_HEADING in outline.headings for outline in outlines)


async def test_fetch_section_reassembles_without_repeating_the_heading():
    async with async_session() as session:
        section = await fetch_section(session, "langchain-overview.mdx", "Create an agent")
    assert section is not None
    assert len(section.chunk_ids) > 1, "expected a section that spans several chunks"
    # Ingestion prefixes every chunk with its heading trail; reassembly must not repeat it.
    assert section.content.count("LangChain overview > Create an agent") == 0


async def test_fetch_section_reads_a_document_intro():
    async with async_session() as session:
        section = await fetch_section(session, "langgraph-overview.mdx", INTRO_HEADING)
    assert section is not None
    assert section.heading is None
    assert section.content


async def test_fetch_section_returns_none_for_an_unknown_heading():
    async with async_session() as session:
        assert await fetch_section(session, "langgraph-overview.mdx", "No Such Heading") is None
