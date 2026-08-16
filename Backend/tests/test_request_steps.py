"""Covers capture of reproduction steps in the user's own words."""

from langchain_core.messages import AIMessage, ToolMessage

from app.agent.tools.steps import (
    STEPS_MARKER,
    TERMINATE,
    captured_steps,
    empty_result,
    parse_steps,
    record_steps,
)


def _result(content):
    return ToolMessage(content=content, tool_call_id="1", name="request_steps")


def test_parse_steps_splits_lines_and_strips_enumerators():
    assert parse_steps("1. Open the dashboard\n2) Click yearly\n- chart blanks") == [
        "Open the dashboard",
        "Click yearly",
        "chart blanks",
    ]


def test_parse_steps_keeps_a_single_line_whole():
    assert parse_steps("open the dashboard, click yearly, it blanks") == [
        "open the dashboard, click yearly, it blanks"
    ]


def test_parse_steps_drops_blank_input():
    assert parse_steps("   \n\n ") == []
    assert parse_steps("") == []


def test_record_steps_round_trips_through_captured_steps():
    steps = ["Open the dashboard", "Click yearly"]

    recorded = record_steps(steps)

    assert recorded.startswith(STEPS_MARKER)
    assert captured_steps([_result(recorded)]) == steps


def test_captured_steps_reads_the_latest_recording():
    first = record_steps(["old"])
    second = record_steps(["new"])

    assert captured_steps([_result(first), _result(second)]) == ["new"]


def test_captured_steps_ignores_unanswered_prompts():
    assert captured_steps([_result(TERMINATE)]) == []
    assert captured_steps([AIMessage(content="anything")]) == []
    assert captured_steps([]) == []


def test_empty_result_asks_again_then_terminates():
    assert TERMINATE not in empty_result(0)
    assert empty_result(1) == TERMINATE


def test_terminate_carries_the_exact_sentence():
    assert "Sorry, we can’t proceed with raising this issue." in TERMINATE
