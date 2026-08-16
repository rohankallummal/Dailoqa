"""The tool that asks the user for screenshots or a screen recording."""

from langchain.tools import ToolRuntime, tool
from langgraph.types import interrupt

_ALREADY_ANSWERED = (
    "Evidence was already requested for this report and the user has answered. The picker "
    "was not reopened. Move on: collect steps to reproduce if you still need them."
)


def _already_asked(runtime: ToolRuntime) -> bool:
    """Report whether this conversation has already been through the file picker.

    A completed request leaves its own ToolMessage in the thread, so the message history
    is the record of whether the user has been asked, and it survives the resume that
    re-executes this tool.
    """
    messages = (runtime.state or {}).get("messages") or []
    return any(getattr(message, "name", None) == "request_evidence" for message in messages)


@tool
async def request_evidence(reason: str, runtime: ToolRuntime) -> str:
    """Ask the user to attach screenshots or a screen recording.

    This opens the file picker in their chat. Use it when visual evidence would let a
    triager see the problem themselves — which is most visual or hard-to-describe
    bugs. Do not use it for feature requests. Ask once per report: the user has
    answered either way once this returns, so a second call is refused rather than
    reopening the picker on someone who already declined.

    Args:
        reason: One short sentence on why the evidence helps, shown to the user.
    """
    if _already_asked(runtime):
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
