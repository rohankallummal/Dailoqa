"""The tool that collects reproduction steps in the user's own words.

Steps are taken from the user directly rather than drafted by the model. Asking the model
for them makes inventing them the cheapest way to satisfy a required field; capturing them
here makes it impossible.

They are the route to the symptom, not the account of the problem -- that lives in
``investigation``, which is why this runs after the findings are recorded rather than
first. A user who cannot reproduce the problem has no steps to give, and their report is
filed on the findings alone.
"""

import re

from langchain.tools import ToolRuntime, tool
from langgraph.types import interrupt

from app.agent.tools.investigation import FINDINGS_FIRST, recorded_findings

STEPS_MARKER = "STEPS RECORDED"

ASK_AGAIN = (
    "The user gave no steps. Tell them the report cannot reach the development team "
    "without them, and ask once more by calling request_steps again."
)

TERMINATE = (
    "The user has now been asked twice and gave no steps. Stop. Do not file anything and "
    "do not ask again. Reply with exactly this and nothing more: "
    "Sorry, we can’t proceed with raising this issue."
)

NOT_REPRODUCIBLE = (
    "Not asked. You recorded that the user cannot reproduce this, so there are no steps "
    "for them to give and none are required. File the report on the findings instead."
)

_ENUMERATOR = re.compile(r"^\s*(?:\d+[.)]|[-*•])\s*")


def parse_steps(text: str) -> list[str]:
    """Split a reply into ordered steps, keeping the user's own wording.

    Only line breaks separate steps. Prose on one line is kept whole rather than split on
    punctuation, because guessing where one step ends invents structure the user did not
    write.
    """
    lines = [_ENUMERATOR.sub("", line).strip() for line in (text or "").splitlines()]
    return [line for line in lines if line]


def record_steps(steps: list[str]) -> str:
    """Render captured steps as the tool result the ticket is later built from."""
    body = "\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1))
    return f"{STEPS_MARKER}\n{body}"


def _results(messages) -> list[str]:
    """Return the content of every request_steps result already in the thread."""
    return [
        str(message.content)
        for message in messages
        if getattr(message, "name", None) == "request_steps"
    ]


def captured_steps(messages) -> list[str]:
    """Return the steps the user typed, read back from the recorded tool result.

    The thread is the record, so this survives the resume that re-executes the tool and
    needs no state schema of its own.
    """
    for content in reversed(_results(messages)):
        if content.startswith(STEPS_MARKER):
            return parse_steps(content[len(STEPS_MARKER) :])
    return []


def missing_steps(steps: list[str], reproducible: str | None) -> bool:
    """Whether a bug still needs the reproduction steps it cannot be filed without.

    A user who cannot reproduce the problem has none to give, so their report is filed on
    the investigation alone rather than discarded. Every other answer keeps the requirement.
    """
    return reproducible != "no" and not steps


@tool
async def request_steps(question: str, runtime: ToolRuntime) -> str:
    """Ask the user for the steps to reproduce and record their answer.

    Call this after record_findings, once you understand the problem and the user has said
    they can reproduce it. Their reply is captured word for word and becomes the ticket's
    steps, so you never write the steps yourself and must never guess them.

    Ask for the route to the problem, not for the problem again: they have already
    described what goes wrong, so make this about the exact clicks that get there.

    If the user does not answer, this says whether to ask once more or to stop. Follow
    what it says exactly.

    Args:
        question: The question the user reads, asking how to reproduce the problem.
    """
    messages = (runtime.state or {}).get("messages") or []
    findings = recorded_findings(messages)
    if not findings:
        return FINDINGS_FIRST
    if findings.get("reproducible") == "no":
        return NOT_REPRODUCIBLE
    asked_before = ASK_AGAIN in _results(messages)
    provided = interrupt({"steps_request": True, "question": question})
    steps = parse_steps(provided if isinstance(provided, str) else "")
    if not steps:
        return TERMINATE if asked_before else ASK_AGAIN
    return record_steps(steps)
