"""Classification of a user message into bug / feature / other."""

from app.agent.state import Classification
from app.llm import get_chat_model


async def classify_message(text: str, model=None) -> Classification:
    """Classify a message as a bug report, feature request, or other."""
    model = model or get_chat_model("classifier")
    structured = model.with_structured_output(Classification)
    return await structured.ainvoke(text)
