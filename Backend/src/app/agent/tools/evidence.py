"""The tool that asks the user for screenshots or a screen recording."""

from langchain.tools import ToolRuntime, tool
from langgraph.types import interrupt

from app.agent.tools.steps import captured_steps

_STEPS_FIRST = (
    "The picker was not opened. Ask for the steps to reproduce first, by calling "
    "request_steps. Evidence is optional and only supplements them."
)

_ALREADY_ANSWERED = (
    "Evidence was already requested for this report and the user has answered. The picker "
    "was not reopened. Move on: collect steps to reproduce if you still need them."
)


def evidence_requested(messages) -> bool:
    """Report whether this conversation has already been through the file picker.

    A completed request leaves its own ToolMessage in the thread, so the message history
    is the record of whether the user has been asked, and it survives the resume that
    re-executes this tool. The write tools read it too: the user may decline evidence, but
    they have to have been offered it.
    """
    return any(getattr(message, "name", None) == "request_evidence" for message in messages)


@tool
async def request_evidence(reason: str, runtime: ToolRuntime) -> str:
    """Ask the user to attach screenshots or a screen recording.

    Call this only once the user has given you the steps to reproduce. Evidence is
    optional and supplements those steps; the steps are the account you reason about,
    and asking for a screenshot first buries the one thing the report cannot be filed
    without.

    This opens the file picker in their chat. Use it when visual evidence would let a
    triager see the problem themselves — which is most visual or hard-to-describe
    bugs. Do not use it for feature requests. Ask once per report: the user has
    answered either way once this returns, so a second call is refused rather than
    reopening the picker on someone who already declined.

    Args:
        reason: One short sentence on why the evidence helps, shown to the user.
    """
    messages = (runtime.state or {}).get("messages") or []
    if not captured_steps(messages):
        return _STEPS_FIRST
    if evidence_requested(messages):
        return _ALREADY_ANSWERED
    provided = interrupt({"evidence_request": True, "reason": reason})
    files = provided or []
    if not files:
        return (
            "The user was asked and attached nothing. This request is closed and further "
            "calls are refused. Steps to reproduce are now required, so ask for those."
        )
    names = ", ".join(item.get("name", "file") for item in files)
    return f"The user attached: {names}. Steps to reproduce are now optional."
