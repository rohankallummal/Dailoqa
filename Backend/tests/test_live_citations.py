"""End-to-end citation behaviour, against the real model and the real index.

Marked ``live``: these cost tokens and need both a model and a populated corpus, so CI runs
``pytest -m "not live"``. They are collected by default locally on purpose. This started life as
a standalone script, and a standalone script is exactly how a 16/16 citation rate quietly becomes
8/16 with nobody noticing — the middleware enforces that *a* citation exists, but only these
catch a regression in whether the answer is any good, whether the route is right, and whether an
off-corpus question is still declined.

Each case is one turn on a fresh thread. Nothing asserts on the model's prose, which varies run
to run; the assertions are on citation and retrieval behaviour, which should not.
"""

import re
from uuid import uuid4

import pytest
from langchain_core.messages import AIMessage

from app.agent.checkpointer import build_checkpointer
from app.agent.context import TurnContext
from app.agent.factory import build_agent
from app.rag.routes import route_for
from tests.conftest import corpus_page, corpus_sources

pytestmark = pytest.mark.live

_CITATION = re.compile(r"\[Doc\s*\d+", re.IGNORECASE)
# The trailing slash is captured, not discarded. An earlier version stopped before it, which
# meant a model writing "/docs/langgraph/" was silently normalised to the manifest value and the
# drift below could never be observed.
_ROUTE = re.compile(r"/docs/[a-z0-9-]+(?:/[a-z0-9-]+)*/?")


async def _answer(question: str) -> str:
    """One turn on a brand-new thread.

    The thread id must be unique per run. The checkpointer is persistent, so a fixed id makes
    every run append to the same conversation until it trips the per-thread model-call cap —
    tests that pass once and then fail forever, for a reason that looks like flakiness.
    """
    thread = f"live-test-{uuid4()}"
    context = TurnContext(
        user_sub="live-test", conversation_id=thread, surface="full", reporter_name="Live Test"
    )
    async with build_checkpointer() as saver:
        agent = build_agent(saver, lambda *_a, **_k: None)
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": question}]},
            {"configurable": {"thread_id": thread}},
            context=context,
        )
    answers = [m for m in result["messages"] if isinstance(m, AIMessage) and not m.tool_calls]
    return answers[-1].text if answers else ""


@pytest.mark.parametrize(
    "question",
    [
        # Two phrasings of a code request, because they behaved differently: the first was the
        # 0/4 case that exposed the missing code-citation rule, and the second still failed
        # after the first was fixed.
        "Show me the code to define a custom subagent.",
        "Give me a code example for creating an agent with a custom tool.",
        "What is a Skill and how does the agent load one?",
        "How do I add a guardrail to an agent?",
    ],
)
async def test_a_documentation_answer_cites_a_real_route(question):
    answer = await _answer(question)

    assert _CITATION.search(answer), f"no [Doc N] in the answer to {question!r}"
    routes = _ROUTE.findall(answer)
    assert routes, f"no /docs route in the answer to {question!r}"

    # Exact match, modulo a trailing slash. The slash is tolerated because Next 308-redirects it
    # so the link still lands, but nothing else is: SKILL.md tells the model to copy the label
    # verbatim, and a route it has edited in any other way is one that can 404. Catching the
    # difference here is the point — in the UI it looks like a broken citation, not a drift.
    known = {route_for(path) for path in corpus_sources()}
    for route in routes:
        assert route.rstrip("/") in known, (
            f"cited a route that is not in the manifest: {route!r}\n"
            f"the model is not copying the label verbatim; nearest known routes: "
            f"{sorted(k for k in known if k and k.split('/')[2] == route.split('/')[2])}"
        )


@pytest.mark.parametrize(
    "question",
    [
        "How do I configure single sign-on for Dailoqa?",
        "What does a Dailoqa Playbook cost per month?",
    ],
)
async def test_an_off_corpus_question_is_declined_without_citing(question):
    # The decline path must survive both the tightened gate and the new uncited-answer check:
    # a correct decline retrieves nothing, so it has nothing to cite and must not be bounced.
    answer = await _answer(question)
    assert not _CITATION.search(answer), f"cited documentation for an uncovered question: {answer[:160]}"


async def test_a_code_answer_carries_the_sample_and_its_source():
    # The end-to-end proof that snippet splicing reaches a user: this code exists only in
    # snippets/code-samples/subagents-compiled-subagent-py.mdx, never inline in the page.
    answer = await _answer("Show me the code to define a custom subagent.")
    assert "```" in answer, "expected a fenced code sample"
    assert "CompiledSubAgent" in answer
    assert route_for(corpus_page("subagents")) in answer
