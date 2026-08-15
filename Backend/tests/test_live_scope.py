"""The scope boundary: what the assistant answers, and what it declines.

Marked ``live`` — these need a real model, since the boundary is enforced by the prompt rather
than by code. That is exactly why they exist: a prompt has no type checker, and the failure it
guards against is silent. The assistant answers a general question well, sounds authoritative,
and nothing anywhere reports a problem.

Both sides are pinned deliberately. A boundary that only rejects is easy to reach by making the
assistant refuse everything, and that version is worse than no boundary at all: greetings get
deflected, on-topic questions get hedged, and the product feels broken rather than careful.
"""

import re
from uuid import uuid4

import pytest
from langchain_core.messages import AIMessage

from app.agent.checkpointer import build_checkpointer
from app.agent.context import TurnContext
from app.agent.factory import build_agent

pytestmark = pytest.mark.live

_CITATION = re.compile(r"\[Doc\s*\d+", re.IGNORECASE)

# Phrases that only appear if the assistant actually started teaching the off-topic subject.
# Deliberately about *substance*, not politeness: naming a topic while declining is fine, and an
# assertion on refusal wording would fail every time the model rephrases.
_INSTRUCTIONAL = re.compile(
    r"\b(sign up|create an account|choose a theme|add products?|step 1|first,? (go|open|nav)"
    r"|navigate to|click on|install|npm install|pip install)\b",
    re.IGNORECASE,
)


async def _turn(messages: list[str]) -> tuple[str, list[str]]:
    """Run a conversation on one thread; return the last answer and every tool called.

    Multi-turn on purpose for the drift case. The single-turn behaviour was already close to
    right — what actually failed was a conversation that wandered off-topic gradually, each
    exchange making the next feel more ordinary.
    """
    thread = f"live-scope-{uuid4()}"
    context = TurnContext(
        user_sub="live-scope", conversation_id=thread, surface="full", reporter_name="Live Scope"
    )
    calls: list[str] = []
    answer = ""
    async with build_checkpointer() as saver:
        agent = build_agent(saver, lambda *_a, **_k: None)
        config = {"configurable": {"thread_id": thread}}
        for message in messages:
            result = await agent.ainvoke({"messages": [{"role": "user", "content": message}]}, config, context=context)
            calls = [c.get("name") for m in result["messages"] for c in (getattr(m, "tool_calls", None) or [])]
            answers = [m for m in result["messages"] if isinstance(m, AIMessage) and not m.tool_calls]
            answer = answers[-1].text if answers else ""
    return answer, calls


# --- out of scope ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "question, giveaway",
    [
        # Chosen because each has an unmistakable right answer, so "did it answer?" is decidable
        # without judging prose. The vaguer probes -- "how do I make a website" -- turned out to
        # be useless as tests: the old prompt already declined those most of the time, so they
        # passed either way and proved nothing.
        ("What is the capital of France?", re.compile(r"\bParis\b", re.I)),
        ("What is 17 * 23?", re.compile(r"\b391\b")),
        ("Translate 'good morning' into Spanish.", re.compile(r"buenos d[ií]as", re.I)),
        # Creative work is the case the first version of this boundary missed. The out-of-scope
        # list named knowledge, products and programming, and the model reasonably concluded a
        # poem was none of those and wrote one.
        ("Write a haiku about the sea.", re.compile(r"\n.*\n")),
    ],
)
async def test_an_off_topic_request_is_declined_not_answered(question, giveaway):
    answer, _calls = await _turn([question])
    assert not giveaway.search(answer), f"answered an out-of-scope question:\n{answer[:300]}"
    assert len(answer) < 600, f"an out-of-scope reply should be short, got {len(answer)} chars"


@pytest.mark.parametrize(
    "conversation",
    [
        ["Tell me how to make a website."],
        # The drift case from a real transcript: innocuous turns ending in a Shopify tutorial.
        # Kept even though it does not discriminate -- across 6 runs the old prompt declined here
        # every time, so it guards the behaviour without evidencing the change.
        ["how are you", "tell me how to make a website", "i want to create an ecommerce website", "shopify"],
    ],
)
async def test_a_conversation_does_not_drift_into_a_tutorial(conversation):
    answer, _calls = await _turn(conversation)
    assert not _INSTRUCTIONAL.search(answer), (
        f"started teaching an out-of-scope subject:\n{answer[:400]}"
    )
    assert len(answer) < 900, f"an out-of-scope reply should be short, got {len(answer)} chars"


# --- in scope, and must stay so --------------------------------------------------------

@pytest.mark.parametrize("greeting", ["how are you", "hi", "what can you do?"])
async def test_a_greeting_gets_a_short_scope_statement_not_small_talk(greeting):
    # The boundary is hard: a greeting is answered only so a first message does not hit a wall,
    # and the reply states what the assistant is for rather than chatting. It still has to
    # *reply* -- refusing "hi" outright would read as broken, which is the opposite failure.
    answer, _calls = await _turn([greeting])
    assert answer.strip(), "a greeting should still get a reply"
    assert len(answer) < 400, f"a greeting reply should be one short sentence, got {len(answer)}"
    assert re.search(r"dailoqa|langchain|langgraph|deep\s*agents|bug|feature", answer, re.I), (
        f"the reply should name what it helps with:\n{answer[:200]}"
    )


@pytest.mark.parametrize(
    "question",
    [
        "Show me the code to define a custom subagent.",
        "Give me a code example for creating an agent with a custom tool.",
    ],
)
async def test_asking_for_documented_code_is_not_mistaken_for_out_of_scope(question):
    # The regression this exists for, caught only because the citation suite went red: an earlier
    # wording drew the boundary around the *shape* of the reply rather than its subject, and the
    # assistant started answering "I can't provide code examples" -- then offering to explain the
    # very thing it had just refused. Refusing documented code is refusing the product's job.
    answer, calls = await _turn([question])
    assert "search_documentation" in calls or "fetch_document_section" in calls, (
        f"refused a documented code question without looking:\n{answer[:250]}"
    )
    assert "```" in answer, f"expected a code sample:\n{answer[:250]}"


async def test_a_documentation_question_still_answers_and_cites():
    # The regression guard that matters most: a boundary is easy to satisfy by refusing
    # everything, and this is what stops that being a passing test run.
    answer, calls = await _turn(["How do subagents work in Deep Agents?"])
    assert "search_documentation" in calls or "fetch_document_section" in calls
    assert _CITATION.search(answer), f"documentation answer lost its citation:\n{answer[:300]}"


async def test_an_off_topic_turn_does_not_poison_the_next_one():
    # Scope is per-request, not per-conversation: being told no should not leave the assistant
    # unwilling to answer the documentation question that follows it.
    answer, calls = await _turn(
        ["How do I build a Shopify store?", "How do subagents work in Deep Agents?"]
    )
    assert "search_documentation" in calls or "fetch_document_section" in calls
    assert _CITATION.search(answer), f"refused an in-scope question after an off-topic one:\n{answer[:300]}"
