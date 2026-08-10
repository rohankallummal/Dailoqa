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

_SKILLS_SECTION = {
    "source_path": "deepagents-overview.mdx",
    "heading": "Context management > Skills",
}


async def _run(model, responses: list[AIMessage], context: TurnContext):
    agent = create_agent(
        model=model(responses),
        tools=TOOLS,
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
            AIMessage(content="Skills package workflows [Doc 1]."),
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
