"""What the user sees when the agent is asked to rewrite an answer.

Grounding can send an answer back to the model. The tokens of the first attempt have already
been streamed by then, so unless they are withdrawn the user reads the same paragraph twice --
once uncited, once cited -- and the persisted message keeps both. That is what these pin.
"""

import pytest
from langchain_core.messages import AIMessage, ToolMessage

from app.agent.runner import _TurnStream, _is_preamble, _is_retry

_A_TOOL_CALL = [{"name": "search_documentation", "args": {"query": "x"}, "id": "a"}]


@pytest.mark.parametrize(
    "chunk, retry",
    [
        ({"require_documentation.after_model": {"jump_to": "model", "messages": []}}, True),
        # Read from jump_to rather than the node name, so a future middleware that reroutes
        # the graph is covered without anyone remembering to add it here.
        ({"some_future_middleware.after_model": {"jump_to": "model"}}, True),
        ({"model": {"messages": []}}, False),
        ({"require_documentation.after_model": None}, False),
        ({"tools": {"messages": []}}, False),
        (None, False),
    ],
)
def test_a_retry_is_recognised_from_the_updates_stream(chunk, retry):
    assert _is_retry(chunk) is retry


@pytest.mark.parametrize(
    "chunk, preamble",
    [
        # "Let me search the documentation, one moment." arriving *with* the tool call. The
        # answer lands straight after it -- "One moment.The documentation doesn't cover..." --
        # so the narration has to be withdrawn once the real answer starts.
        ({"model": {"messages": [AIMessage(content="Let me search. One moment.", tool_calls=_A_TOOL_CALL)]}}, True),
        # A silent tool call has nothing to withdraw, and restarting on it would be noise.
        ({"model": {"messages": [AIMessage(content="", tool_calls=_A_TOOL_CALL)]}}, False),
        ({"model": {"messages": [AIMessage(content="   \n", tool_calls=_A_TOOL_CALL)]}}, False),
        # The final answer must never be mistaken for narration; that would blank the answer.
        ({"model": {"messages": [AIMessage(content="The documentation does not cover that.")]}}, False),
        ({"tools": {"messages": [ToolMessage(content="[Doc 1: x]", name="search_documentation", tool_call_id="a")]}}, False),
        ({"middleware.after_model": None}, False),
        (None, False),
    ],
)
def test_narration_before_a_tool_call_is_recognised(chunk, preamble):
    assert _is_preamble(chunk) is preamble


def test_the_two_supersede_conditions_stay_independent():
    # A retry is not narration and narration is not a retry; conflating them would make one
    # of the two fire on the wrong thing.
    retry = {"require_documentation.after_model": {"jump_to": "model"}}
    assert _is_retry(retry) and not _is_preamble(retry)


async def test_a_rewrite_replaces_the_draft_rather_than_appending_to_it():
    published: list[dict] = []

    stream = _TurnStream("user", "conversation", "turn")
    stream.publish = lambda event: published.append(event) or _noop()  # type: ignore[assignment]

    await stream.token("First attempt, uncited.")
    await stream.restart()
    await stream.token("Second attempt, cited [Doc 1].")

    # The persisted message is built from stream.text; without the reset it would carry both
    # answers concatenated, which is exactly what reached the user.
    assert stream.text == "Second attempt, cited [Doc 1]."
    assert "First attempt" not in stream.text
    assert any(event.get("stage") == "restart" for event in published), (
        "the client is never told to discard the draft it has already rendered"
    )


async def _noop():
    return None
