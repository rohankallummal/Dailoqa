"""The last gate: an answer the documentation does not support is replaced, not retried.

From a five-turn conversation that began on documentation and drifted off it. By the final turn
the agent produced a complete "AI chatbot in LangGraph" built on ``compiled_graph.run(...)`` --
not a LangGraph API, ``invoke`` is -- with no citation, and every existing check passed it.

**Why the existing uncited check cannot catch this.** It bounces an answer only when its
vocabulary overlaps the retrieved passages, which is what lets a correct decline through. A
fabrication has *low* overlap for the same reason a decline does: it was not built from the
passages. Invention and honesty take the same path, and invention passes.

**And why this replaces rather than retries.** Bouncing was tried and measurably makes things
worse: asked to fix an uncited code sample, the model declined a question the corpus covers,
because declining satisfies the correction more cheaply than citing does. That regression was
reproducible 3/3 and reverted. A substitution has no second attempt to go wrong.

The passing cases below are the ones that matter. Replacing a good answer is a worse failure than
the one being fixed, so every shape of legitimate uncited reply is pinned here.
"""

import pytest

from app.agent.middleware.grounding import OUT_OF_SCOPE_ANSWER, ungrounded_answer


class _Msg:
    """Minimal stand-in for a tool message carrying returned passages."""

    def __init__(self, name, content):
        self.name = name
        self.content = content


def _thread_with_passages():
    return [_Msg("search_documentation", "[Doc 1: langgraph/Subgraphs]\nPass the subgraph to add_node.")]


def _thread_without_passages():
    return [_Msg("search_documentation", "Nothing in the documentation matches that.")]


_FABRICATED_CODE = """Here's a chatbot:

```python
graph = StateGraph()
compiled = graph.compile()
compiled.run(state)
```
"""

# The turn-4 shape: a confident essay from the model's own knowledge, no code, no citation.
_FABRICATED_PROSE = (
    "Using subgraphs in LangGraph can be helpful in developing an AI chatbot for a website by "
    "providing a structured way to manage conversation flow. Modular design lets each component "
    "handle a specific aspect of the conversation. State management keeps user information "
    "separate from FAQs. Custom logic can be triggered for complex questions. Data processing "
    "can extract key information from user inputs or integrate with APIs. Scalability improves "
    "because new features become new subgraphs rather than clutter in the main flow."
)


@pytest.mark.parametrize("answer", [_FABRICATED_CODE, _FABRICATED_PROSE])
def test_an_ungrounded_answer_is_flagged(answer):
    assert ungrounded_answer(_thread_with_passages(), answer) is True


def test_a_cited_answer_is_never_flagged():
    answer = "Pass the compiled subgraph to add_node [Doc 1].\n\nSources:\n[Doc 1] langgraph/Subgraphs (/docs/langgraph/subgraphs)"
    assert ungrounded_answer(_thread_with_passages(), answer) is False


@pytest.mark.parametrize(
    "answer",
    [
        # A decline is the correct uncited answer and must survive untouched.
        "The documentation does not cover how to calculate shortest paths in LangGraph.",
        "The documentation doesn't mention that Skills are deprecated in Deep Agents.",
        "I couldn't find any reference to that in the documentation.",
        # Caught live: this phrasing was missing from the decline list, so the gate would have
        # replaced a textbook-correct decline with the out-of-scope sentence.
        'The term "Apache flow" does not appear in the documentation for Deep Agents.',
        "That concept does not exist in the LangGraph documentation.",
        "The documentation does not contain a specific code sample for this.",
        # Scope refusals and clarifying questions are short and uncited by nature.
        "I can only help with questions about DailoQA, LangChain, LangGraph and Deep Agents.",
        "I can help with documentation or with filing a ticket. Which do you need?",
    ],
)
def test_a_legitimate_uncited_reply_is_left_alone(answer):
    assert ungrounded_answer(_thread_with_passages(), answer) is False


def test_a_thread_that_retrieved_nothing_is_left_alone():
    # Ticket flows retrieve no documentation, so they can never be rewritten by this. Scoping
    # falls out of the same rule rather than needing to know which skill is running.
    assert ungrounded_answer(_thread_without_passages(), _FABRICATED_PROSE) is False


def test_a_long_decline_is_still_a_decline():
    # Length alone must not condemn an answer: a decline that names nearby topics runs long and
    # is still correct.
    answer = (
        "The documentation does not cover shortest-path algorithms in LangGraph. " + "x" * 500
    )
    assert ungrounded_answer(_thread_with_passages(), answer) is False


def test_the_replacement_names_the_products_in_scope():
    # It is the only thing the user sees when this fires, so it has to say what to ask instead.
    for product in ("DailoQA", "LangChain", "LangGraph", "Deep Agents"):
        assert product in OUT_OF_SCOPE_ANSWER
