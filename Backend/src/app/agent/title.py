"""Async LLM helper that generates a short conversation title."""

import logging

from app.llm import get_chat_model

logger = logging.getLogger(__name__)

_MAX_WORDS = 6
_PROMPT = (
    "Write a title of 4 to 6 words that clearly describes the topic of the "
    "message below. Use Title Case. Return only the title with no surrounding "
    "quotes, no trailing punctuation, and no preamble.\n\nMessage:\n{message}"
)


def _clean_title(raw: str) -> str | None:
    """Normalize a model-produced title; return None if nothing usable remains."""
    text = " ".join(raw.strip().strip("\"'").split()).rstrip(".!?,;:")
    if not text:
        return None
    return " ".join(text.split()[:_MAX_WORDS])


async def generate_title(first_message: str) -> str | None:
    """Generate a 3-6 word title for a conversation from its first message.

    Returns None on empty input, an empty model response, or any LLM error so a
    failure never propagates into the chat request path.
    """
    if not first_message.strip():
        return None
    try:
        model = get_chat_model("titler")
        response = await model.ainvoke(_PROMPT.format(message=first_message))
    except Exception as error:
        logger.warning("title LLM call failed: %s", error)
        return None
    return _clean_title(str(response.content))
