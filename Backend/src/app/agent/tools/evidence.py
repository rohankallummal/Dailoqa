"""The tool that asks the user for screenshots or a screen recording."""

from langchain.tools import tool
from langgraph.types import interrupt


@tool
async def request_evidence(reason: str) -> str:
    """Ask the user to attach screenshots or a screen recording.

    This opens the file picker in their chat. Use it when visual evidence would let a
    triager see the problem themselves — which is most visual or hard-to-describe
    bugs. Do not use it for feature requests. If the user attaches nothing, carry on
    and collect reproduction steps instead.

    Args:
        reason: One short sentence on why the evidence helps, shown to the user.
    """
    provided = interrupt({"evidence_request": True, "reason": reason})
    files = provided or []
    if not files:
        return "The user attached nothing. Ask for steps to reproduce instead."
    names = ", ".join(item.get("name", "file") for item in files)
    return f"The user attached: {names}. Steps to reproduce are now optional."
