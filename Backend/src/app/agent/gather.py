"""Required-field tracking and follow-up question generation."""

from app.llm import get_chat_model

REQUIRED_FIELDS: dict[str, list[str]] = {
    "bug": ["summary", "expected", "actual", "environment"],
    "feature": ["summary", "business_justification", "additional_requirements"],
}


def missing_fields(kind: str, fields: dict) -> list[str]:
    """Return required field names that are absent or blank for the given kind.

    A bug report needs steps to reproduce only when no evidence was attached; supplied
    images or video stand in for the walkthrough.
    """
    required = list(REQUIRED_FIELDS.get(kind, []))
    if kind == "bug" and not fields.get("evidence"):
        required.append("steps_to_reproduce")
    return [name for name in required if not str(fields.get(name, "")).strip()]


async def next_follow_up(kind: str, fields: dict, model=None) -> str:
    """Author a concise follow-up question for the first missing field(s)."""
    model = model or get_chat_model("agent")
    missing = missing_fields(kind, fields)
    prompt = (
        f"You are collecting a {kind} ticket. Known so far: {fields}. "
        f"Missing: {missing}. Ask one concise, friendly question for the most important missing item."
    )
    response = await model.ainvoke(prompt)
    return response.content
