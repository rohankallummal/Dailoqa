"""Notification text for a finished ticket job.

The worker has no conversation to draw on, so it writes this line with a single
cheap model call rather than emitting a canned string. The fallback exists because a
notification must still be delivered when the model is unavailable.
"""

import logging

from app.llm import get_chat_model

logger = logging.getLogger(__name__)

TICKET_FAILED = "We couldn't create your ticket. Please contact support."

_FALLBACK = {
    "create": "Your report has been submitted to the DailoQA development team.",
    "link": "Your report was added to an existing ticket the team is already reviewing.",
}


async def outcome_body(kind: str, action: str, jira_key: str) -> str:
    """Write one short sentence telling the user what happened to their report."""
    verb = "filed as a new ticket" if action == "create" else "added to an existing ticket"
    prompt = (
        f"A user's {kind} report was {verb} ({jira_key}). "
        "Write one short, warm sentence telling them so. No greeting, no sign-off, "
        "no ticket key, no markdown. Plain sentence only."
    )
    try:
        response = await get_chat_model("titler").ainvoke(prompt)
        body = response.text().strip() if hasattr(response, "text") else str(response.content).strip()
        return body or _FALLBACK[action]
    except Exception as error:
        logger.warning("outcome text generation failed for %s: %s", jira_key, error)
        return _FALLBACK[action]
