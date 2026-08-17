"""The tool that asks the user for screenshots or a screen recording."""

from langchain.tools import ToolRuntime, tool
from langgraph.types import interrupt

from app.agent.tools.investigation import FINDINGS_FIRST, recorded_findings

EVIDENCE_MARKER = "EVIDENCE REQUEST CLOSED"

_ALREADY_ANSWERED = (
    "Evidence was already requested for this report and the user has answered. The picker "
    "was not reopened, and it will not be. Move on to filing the report."
)


def evidence_requested(messages) -> bool:
    """Report whether the user has actually been through the file picker.

    A request that reached the user and closed leaves its marker in the thread, so the
    message history is the record and it survives the resume that re-executes this tool.
    A call refused before the picker opened leaves a result too, which is why the marker
    is checked rather than the tool's name: the write tools let a user decline evidence
    but not go unasked, and a refusal is not an asking.
    """
    return any(
        getattr(message, "name", None) == "request_evidence"
        and str(message.content).startswith(EVIDENCE_MARKER)
        for message in messages
    )


@tool
async def request_evidence(reason: str, runtime: ToolRuntime) -> str:
    """Ask the user to attach screenshots or a screen recording.

    Call this after record_findings, once you understand the problem. Evidence supplements
    the report for a human triager; it is not something you can read, and it cannot stand
    in for knowing what went wrong.

    This opens the file picker in their chat. Use it when visual evidence would let a
    triager see the problem themselves, which is most visual or hard-to-describe bugs. Do
    not use it for feature requests. Ask once per report: the user has answered either way
    once this returns, so a second call is refused rather than reopening the picker on
    someone who already declined.

    Args:
        reason: One short sentence on why the evidence helps, shown to the user.
    """
    messages = (runtime.state or {}).get("messages") or []
    if not recorded_findings(messages):
        return FINDINGS_FIRST
    if evidence_requested(messages):
        return _ALREADY_ANSWERED
    provided = interrupt({"evidence_request": True, "reason": reason})
    files = provided or []
    if not files:
        return (
            f"{EVIDENCE_MARKER}. The user was asked and attached nothing. That is their "
            "choice and the report is filed without it. Do not ask again."
        )
    names = ", ".join(item.get("name", "file") for item in files)
    return (
        f"{EVIDENCE_MARKER}. The user attached: {names}. These go to the team with the "
        "ticket automatically. You cannot open them, so do not describe what they show."
    )
