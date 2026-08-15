"""What the user sees when the agent is asked to rewrite an answer.

Grounding can send an answer back to the model. The tokens of the first attempt have already
been streamed by then, so unless they are withdrawn the user reads the same paragraph twice --
once uncited, once cited -- and the persisted message keeps both. That is what these pin.
"""

import pytest

from app.agent.runner import _TurnStream, _is_retry


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
