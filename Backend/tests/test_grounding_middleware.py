"""The citation-integrity check, driven through the real agent graph.

The middleware's job is narrow and worth stating: it catches an answer that *claims*
documentation it never read. It is not a retrieval gate — an answer that cites nothing is
never inspected — so the tests below pin the boundary in both directions.
"""

from langchain.agents import create_agent
from langchain_core.messages import AIMessage

from app.agent.context import TurnContext
from app.agent.middleware.grounding import require_documentation
from app.agent.tools import TOOLS
from app.agent.tools.docs import NO_MATCH
from tests.conftest import corpus_page

_SKILLS_SECTION = {
    "source_path": corpus_page("skills"),
    "heading": "How skills work",
}

# A real answer closes with a legend resolving each tag to a page, and the middleware now bounces
# one that does not (see test_citation_legend.py). These fixtures predate that rule and carried a
# bare "[Doc 1]", which is no longer a shape the model is allowed to emit -- so the sample answers
# are brought up to date rather than the rule being relaxed for them. What each test asserts is
# unchanged: that the turn passes without a correction.
_SOURCES = "\n\nSources:\n[Doc 1] deep-agents/Skills - How skills work (/docs/deepagents/skills#how-skills-work)"


def _stub_tools(results: dict[str, str]):
    """Stand-ins for the documentation tools that return fixed text.

    The uncited-answer checks turn on *what a tool returned* — a tagged passage versus
    ``NO_MATCH`` — so the result has to be the fixture. Driving them through real retrieval
    would make them depend on which passage currently wins a search, which is a different
    test's job and would make these fail for unrelated reasons.
    """
    from langchain_core.tools import StructuredTool

    def build(name: str, text: str):
        return StructuredTool.from_function(
            func=lambda **_kwargs: text, name=name, description=f"stub {name}"
        )

    known = {tool.name for tool in TOOLS}
    unknown = set(results) - known
    if unknown:  # a typo here would silently fall through to the real tools
        raise KeyError(f"no such tool to stub: {sorted(unknown)}")
    stubs = {name: build(name, text) for name, text in results.items()}
    return [stubs.get(t.name, t) for t in TOOLS]


async def _run(
    model,
    responses: list[AIMessage],
    context: TurnContext,
    tool_results: dict[str, str] | None = None,
):
    agent = create_agent(
        model=model(responses),
        tools=_stub_tools(tool_results) if tool_results else TOOLS,
        context_schema=TurnContext,
        middleware=[require_documentation],
    )
    result = await agent.ainvoke({"messages": [{"role": "user", "content": "q"}]}, context=context)
    answers = [m for m in result["messages"] if isinstance(m, AIMessage) and not m.tool_calls]
    return answers[-1]


async def test_citations_without_a_lookup_are_sent_back(turn_context, scripted_model):
    final = await _run(
        scripted_model,
        [
            AIMessage(content="Skills package workflows [Doc 1]."),
            AIMessage(content="Corrected answer after searching [Doc 1]."),
        ],
        turn_context,
    )
    assert turn_context.grounding_corrections == 1
    assert "Corrected" in final.content


async def test_an_answer_without_citations_is_never_inspected(turn_context, scripted_model):
    # Ticket replies carry no [Doc N], which is what keeps this middleware scoped to
    # documentation without it needing to know which skill is running.
    final = await _run(scripted_model, [AIMessage(content="Filed your bug as KAN-12.")], turn_context)
    assert turn_context.grounding_corrections == 0
    assert "KAN-12" in final.content


async def test_fetching_without_searching_still_counts_as_consulting(turn_context, scripted_model):
    # list -> fetch is a legitimate route to a cited answer. Counting only
    # search_documentation would bounce it and tell the model to redo work it did.
    final = await _run(
        scripted_model,
        [
            AIMessage(content="", tool_calls=[{"name": "list_documentation_sources", "args": {}, "id": "a"}]),
            AIMessage(content="", tool_calls=[{"name": "fetch_document_section", "args": _SKILLS_SECTION, "id": "b"}]),
            AIMessage(content=f"Skills package workflows [Doc 1].{_SOURCES}"),
        ],
        turn_context,
    )
    assert turn_context.grounding_corrections == 0
    assert "[Doc 1]" in final.content


async def test_browsing_the_inventory_alone_does_not_justify_a_citation(turn_context, scripted_model):
    # The hole this closes: list_documentation_sources returns titles and headings, never
    # passages. Counting it as evidence let a model read a title, invent `[Doc 1]`, and
    # pass the citation-integrity check.
    final = await _run(
        scripted_model,
        [
            AIMessage(content="", tool_calls=[{"name": "list_documentation_sources", "args": {}, "id": "a"}]),
            AIMessage(content="Skills package workflows [Doc 1]."),
            AIMessage(content="Corrected after actually searching [Doc 1]."),
        ],
        turn_context,
    )
    assert turn_context.grounding_corrections == 1
    assert "Corrected" in final.content


async def test_an_answer_built_on_passages_must_cite_them(turn_context, scripted_model):
    # The enforcement half. Prompt wording got the live citation rate to 16/16, but wording is
    # compliance: without this, an unrelated SKILL.md edit could take it back to 8/16 silently.
    final = await _run(
        scripted_model,
        [
            AIMessage(content="", tool_calls=[{"name": "search_documentation", "args": {"query": "skills"}, "id": "a"}]),
            AIMessage(content="Skills package workflows into a directory."),
            AIMessage(content="Skills package workflows into a directory [Doc 1]."),
        ],
        turn_context,
        tool_results={
            "search_documentation": "[Doc 1: deep-agents/Skills - How skills work]\nSkills package workflows."
        },
    )
    assert turn_context.grounding_corrections == 1
    assert "[Doc 1]" in final.content


async def test_a_decline_after_an_empty_search_is_not_bounced(turn_context, scripted_model):
    # The exemption that makes the rule safe. Searching and finding nothing then declining is
    # *correct*; a naive "tool ran but no [Doc N]" check would bounce it and push the model into
    # inventing an answer -- turning the best behaviour into the worst.
    final = await _run(
        scripted_model,
        [
            AIMessage(content="", tool_calls=[{"name": "search_documentation", "args": {"query": "sso"}, "id": "a"}]),
            AIMessage(content="The documentation does not cover single sign-on."),
        ],
        turn_context,
        tool_results={"search_documentation": NO_MATCH},
    )
    assert turn_context.grounding_corrections == 0
    assert "does not cover" in final.content


async def test_a_cited_answer_backed_by_passages_passes_untouched(turn_context, scripted_model):
    final = await _run(
        scripted_model,
        [
            AIMessage(content="", tool_calls=[{"name": "search_documentation", "args": {"query": "skills"}, "id": "a"}]),
            AIMessage(content=f"Skills package workflows [Doc 1].{_SOURCES}"),
        ],
        turn_context,
        tool_results={
            "search_documentation": "[Doc 1: deep-agents/Skills - How skills work]\nSkills package workflows."
        },
    )
    assert turn_context.grounding_corrections == 0
    assert "[Doc 1]" in final.content


async def test_a_decline_is_not_forced_to_cite_irrelevant_passages(turn_context, scripted_model):
    """The check that stopped the irrelevant citations, by removing what caused them.

    Retrieval cannot tell "about LangGraph" from "answers this LangGraph question", so a search
    for something absent still returns five confident passages. Requiring a citation whenever
    passages arrived left one way to comply: write a sentence about whatever came back and cite
    that — "it discusses subgraph communication [Doc 1][Doc 2][Doc 5]" beneath an answer about
    shortest paths. The enforcement was producing the noise it existed to prevent.

    What is required now is narrower and truer: an answer whose *wording came from* the
    passages must credit them. A decline shares almost nothing with them and owes nothing.
    """
    final = await _run(
        scripted_model,
        [
            AIMessage(content="", tool_calls=[{"name": "search_documentation", "args": {"query": "shortest path"}, "id": "a"}]),
            AIMessage(content="The documentation does not cover calculating shortest paths between nodes."),
        ],
        turn_context,
        tool_results={
            "search_documentation": (
                "[Doc 1: langgraph/Subgraphs - Call a subgraph inside a node]\n"
                "When adding subgraphs you define how the parent graph and the subgraph "
                "communicate through shared state keys and wrapper functions."
            )
        },
    )
    assert turn_context.grounding_corrections == 0, "a decline must not be sent back to add sources"
    assert "does not cover" in final.content
    assert "[Doc" not in final.content, "the decline should carry no citation at all"


def test_the_uncited_correction_offers_declining_as_well_as_citing():
    """The correction must not have exactly one exit, because it fires on correct answers too.

    A search that returns on-topic but irrelevant passages -- "explain Apache flow in Deep
    Agents" -- makes a *correct* decline look like an uncited answer, so this bounces it. When
    the only instruction was "add the citations", the way out was to invent a connection to a
    passage and cite it, which is how enforcement started producing the confabulation it exists
    to prevent. Both outcomes have to be on offer, with the honest one named explicitly.
    """
    from app.agent.middleware.grounding import _UNCITED

    assert "do answer the question" in _UNCITED, "the cite-it path must be stated"
    assert "do NOT answer the question" in _UNCITED, "the decline path must be stated"
    assert "manufacture" in _UNCITED, "inventing a connection must be named as the failure"


async def test_a_model_that_will_not_comply_still_terminates(turn_context, scripted_model):
    # One correction, then the answer is allowed through: a persistent offender must not
    # be able to loop the turn forever.
    final = await _run(
        scripted_model,
        [
            AIMessage(content="Unsourced [Doc 1]."),
            AIMessage(content="Still unsourced [Doc 1]."),
            AIMessage(content="never reached"),
        ],
        turn_context,
    )
    assert turn_context.grounding_corrections == 1
    assert "Still unsourced" in final.content
