"""Catching an answer that credits a library its own citations do not come from.

Every failing case below is a real answer, produced live while probing for false positives. The
shape is always the same: the question names a library, the search returns the right passages from
a *different* library, and the model keeps the questioner's word. "What are guardrails in
LangGraph?" came back as "Guardrails in LangGraph are…" over five citations that were, all five,
``langchain/guardrails.md``.

Retrieval was correct in every one of them — in the LangChain-subagents case it even ranked the
genuinely right cross-library page first — so these check the prose against the answer's own
citations, never against the search results.

The passing cases carry the weight here. The obvious over-correction is to flag any answer that
names two libraries, and that would break the documentation's own most precise sentences: these
three products are layered, and "the subagents middleware from Deep Agents" is exactly how the
LangChain page describes a Deep Agents component used inside LangChain.
"""

import pytest

from app.agent.middleware.grounding import _misattribution

# The tool's own tag format. The label is what carries the topic, via its route.
_GUARDRAILS = "[Doc 1: langchain/Guardrails - Custom guardrails (/docs/langchain/guardrails)]"
_PERSISTENCE = "[Doc 1: langgraph/Persistence (/docs/langgraph/persistence)]"
_SUBAGENTS = "[Doc 1: deep-agents/Subagents - Using CompiledSubAgent (/docs/deepagents/subagents)]"


def _flagged(answer: str, passages: str) -> str | None:
    problem = _misattribution(answer, passages)
    return problem[0] if problem else None


@pytest.mark.parametrize(
    "answer, passages",
    [
        # All four observed live, verbatim openings.
        ("Guardrails in LangGraph are mechanisms for safety [Doc 1].", _GUARDRAILS),
        ("Persistence in LangChain is implemented through checkpointers [Doc 1].", _PERSISTENCE),
        ("Subagents in LangChain provide a way to delegate tasks [Doc 1].", _SUBAGENTS),
        # The possessive is the same claim in a different grammatical dress.
        ("LangGraph's guardrails validate content [Doc 1].", _GUARDRAILS),
    ],
)
def test_crediting_a_library_the_citations_do_not_come_from_is_caught(answer, passages):
    assert _flagged(answer, passages) is not None


@pytest.mark.parametrize(
    "answer, passages",
    [
        # The ordinary correct answer.
        ("Guardrails in LangChain validate content [Doc 1].", _GUARDRAILS),
        ("Persistence in LangGraph uses checkpointers [Doc 1].", _PERSISTENCE),
        ("Subagents in Deep Agents isolate context [Doc 1].", _SUBAGENTS),
        # Provenance, not attribution -- and the phrasing the corpus itself uses. Flagging this
        # would punish the one sentence that gets a layered product exactly right.
        (
            "The subagents middleware from Deep Agents supplies subagents via a task tool "
            "[Doc 1].",
            "[Doc 1: langchain/Prebuilt middleware - Subagent (/docs/langchain/prebuilt-middleware)]",
        ),
        # Cites both libraries and names both: neither is stray.
        (
            "Guardrails in LangChain are middleware, and persistence in LangGraph is separate "
            "[Doc 1][Doc 2].",
            f"{_GUARDRAILS}\n[Doc 2: langgraph/Persistence (/docs/langgraph/persistence)]",
        ),
        # A decline cites nothing resolvable, so there is nothing to attribute against. The
        # uncited/fabricated checks own this case; duplicating it here would double-bounce it.
        ("The documentation does not cover that.", _GUARDRAILS),
    ],
)
def test_a_correctly_attributed_answer_is_left_alone(answer, passages):
    assert _flagged(answer, passages) is None


@pytest.mark.parametrize(
    "answer",
    [
        # The exact answer this whole check exists to produce, observed live once it worked.
        "The documentation does not cover guardrails in LangGraph. Instead, guardrails are "
        "features provided by LangChain, which validate and filter content [Doc 1].",
        # The same correction in the other phrasing the model reaches for.
        "The documentation for persistence refers specifically to LangGraph, not LangChain "
        "[Doc 1].",
        "Guardrails are not a LangGraph feature; they are documented under LangChain [Doc 1].",
    ],
)
def test_denying_a_library_is_not_crediting_it(answer):
    """The negation has to be read, or the check rejects the behaviour it was added to produce.

    Caught by the live test rather than by review: "does not cover guardrails **in LangGraph**"
    contains the attributive phrase verbatim, in the attributive position, while asserting its
    opposite. The first version of this check bounced that answer -- the single best answer in
    the whole probe -- and the middleware log was what gave it away.
    """
    assert _flagged(answer, _GUARDRAILS) is None


def test_the_correction_names_both_libraries():
    # The model has to be told which way round it got them, or it cannot act on the bounce.
    problem = _misattribution("Guardrails in LangGraph are safety checks [Doc 1].", _GUARDRAILS)
    assert problem is not None
    _phrase, correction = problem
    assert "LangGraph" in correction and "LangChain" in correction


def test_a_tag_with_no_matching_passage_is_ignored():
    # [Doc 9] was never handed over, so its topic is unknown and cannot contradict anything.
    # Inventing a topic for it would make this check fire on the fabricated-citation case,
    # which has its own correction and a more useful message.
    assert _flagged("Guardrails in LangGraph are safety checks [Doc 9].", _GUARDRAILS) is None


def test_the_label_topic_is_read_when_a_route_is_missing():
    # The manifest-drift fallback drops the route and keeps the "topic/Title" form. Attribution
    # still has to work there, since that label is exactly when the corpus has moved on.
    assert _flagged("Guardrails in LangGraph are checks [Doc 1].", "[Doc 1: langchain/Guardrails]")
