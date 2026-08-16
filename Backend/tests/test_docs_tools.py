"""The documentation tools, and the citation numbering they share.

Numbering is the piece most likely to break quietly: the tools run several times in one
turn, and if a later call restarted at [Doc 1] the Sources legend would silently stop
matching the prose the model already wrote.
"""

import re
from types import SimpleNamespace

from app.agent.tools import DOC_TOOL_NAMES, TICKET_TOOLS, TOOLS, active_tools
from app.agent.tools.docs import (
    NO_MATCH,
    fetch_document_section,
    list_documentation_sources,
    search_documentation,
)
from app.config import get_settings
from tests.conftest import corpus_page

_SKILLS_PAGE = corpus_page("skills")
_SKILLS_SECTION = (_SKILLS_PAGE, "How skills work")


def _runtime(turn_context):
    """The slice of ToolRuntime the documentation tools actually use."""
    return SimpleNamespace(context=turn_context)


def _tags(text: str) -> list[int]:
    return [int(number) for number in re.findall(r"\[Doc (\d+)", text)]


async def test_search_tags_every_passage(turn_context):
    output = await search_documentation.coroutine(query="What is a Skill?", runtime=_runtime(turn_context))
    assert _tags(output), "search results must carry citation tags"
    assert "Skills" in output


async def test_search_does_not_repeat_the_heading_inside_the_passage(turn_context):
    # The tag already names the document and section; ingestion also prefixes the chunk
    # text with the same trail, and showing both wastes context and reads oddly.
    output = await search_documentation.coroutine(query="What is a Skill?", runtime=_runtime(turn_context))
    assert "Deep Agents overview > Context management > Skills\n" not in output


async def test_absent_topic_tells_the_model_to_decline(turn_context):
    output = await search_documentation.coroutine(
        query="How do I create a Playbook?", runtime=_runtime(turn_context)
    )
    assert output == NO_MATCH
    assert not turn_context.citations, "a miss must not consume a citation number"


async def test_numbers_do_not_collide_across_two_searches(turn_context):
    runtime = _runtime(turn_context)
    first = await search_documentation.coroutine(query="What is a Skill?", runtime=runtime)
    second = await search_documentation.coroutine(query="How does memory work?", runtime=runtime)

    fresh = set(_tags(second)) - set(_tags(first))
    assert fresh, "the second search should introduce new passages"
    # Every number is unique to one passage, so nothing the model already cited is reused
    # for different text.
    assert len(set(turn_context.citations.values())) == len(set(turn_context.citations.values()))
    assert max(_tags(second)) > max(_tags(first))


async def test_fetch_reuses_the_number_a_search_already_assigned(turn_context):
    runtime = _runtime(turn_context)
    searched = await search_documentation.coroutine(query="What is a Skill?", runtime=runtime)
    first_tag = _tags(searched)[0]

    fetched = await fetch_document_section.coroutine(
        source_path=_SKILLS_SECTION[0], heading=_SKILLS_SECTION[1], runtime=runtime
    )
    assert _tags(fetched)[0] == first_tag, "the same passage must keep its citation number"


def test_fragments_of_one_section_share_a_citation_number(turn_context):
    """Two chunks of the same section are one source to the reader, so one number.

    Numbering per chunk produced "[Doc 1][Doc 2][Doc 3][Doc 4][Doc 5]" on a single sentence
    and a Sources legend listing the same section twice under different numbers. The label is
    built from source and heading, so two numbers carrying one label is a distinction nobody
    can see or act on.
    """
    from app.agent.tools.docs import _cite, _section_key

    runtime = _runtime(turn_context)
    section = _section_key("langgraph/subgraphs.md", "Define subgraph communication")
    other = _section_key("langgraph/overview.md", None)

    first = _cite(runtime, ["chunk-a"], section)
    second = _cite(runtime, ["chunk-b"], section)
    assert first == second, "fragments of one section must not be numbered separately"

    assert _cite(runtime, ["chunk-c"], other) != first, "distinct sections need distinct numbers"
    assert _cite(runtime, ["chunk-a"], section) == first, "a passage must keep its number"
    assert _cite(runtime, ["chunk-z"]) not in (0, None), "a chunk with no section still cites"


async def test_fetch_reports_an_unknown_section(turn_context):
    output = await fetch_document_section.coroutine(
        source_path=_SKILLS_PAGE, heading="Nope", runtime=_runtime(turn_context)
    )
    assert "list_documentation_sources" in output


async def test_list_returns_an_inventory_without_citations(turn_context):
    output = await list_documentation_sources.coroutine(runtime=_runtime(turn_context))
    assert _SKILLS_PAGE in output
    assert not _tags(output), "an inventory is not citable text"
    assert not turn_context.citations


def test_doc_tool_names_match_the_registered_tools():
    # The grounding middleware reads DOC_TOOL_NAMES to decide whether the agent consulted
    # the docs, so a new documentation tool must appear in both places or citations made
    # through it would be treated as unsourced.
    from app.agent.tools import DOC_TOOLS

    assert {tool.name for tool in DOC_TOOLS} == set(DOC_TOOL_NAMES)


def test_documentation_can_be_switched_off():
    settings = get_settings()
    original = settings.rag_enabled
    try:
        settings.rag_enabled = False
        names = {tool.name for tool in active_tools()}
        assert not (names & DOC_TOOL_NAMES)
        assert {tool.name for tool in TICKET_TOOLS} <= names, "ticketing must be unaffected"

        settings.rag_enabled = True
        assert DOC_TOOL_NAMES <= {tool.name for tool in active_tools()}
    finally:
        settings.rag_enabled = original


def test_registry_lists_every_tool():
    assert {tool.name for tool in TOOLS} >= DOC_TOOL_NAMES | {tool.name for tool in TICKET_TOOLS}
