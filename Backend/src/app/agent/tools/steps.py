"""The tool that collects reproduction steps in the user's own words.

The steps are the only account of a bug the agent can reason about, so they are taken
from the user directly rather than drafted by the model. Asking the model for them makes
inventing them the cheapest way to satisfy a required field; capturing them here makes it
impossible.
"""

import re

from langchain.tools import ToolRuntime, tool
from langgraph.types import interrupt

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


@tool
async def request_steps(question: str, runtime: ToolRuntime) -> str:
    """Ask the user for the steps to reproduce and record their answer.

    Call this for every bug, before asking for evidence. Their reply is captured word for
    word and becomes the ticket's steps, so you never write the steps yourself and must
    never guess them.

    If the user does not answer, this says whether to ask once more or to stop. Follow
    what it says exactly.

    Args:
        question: The question the user reads, asking how to reproduce the problem.
    """
    prior = len(_results((runtime.state or {}).get("messages") or []))
    provided = interrupt({"steps_request": True, "question": question})
    steps = parse_steps(provided if isinstance(provided, str) else "")
    if not steps:
        return TERMINATE if prior else ASK_AGAIN
    return record_steps(steps)
