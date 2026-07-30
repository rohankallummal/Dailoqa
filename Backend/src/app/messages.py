"""Fixed-wording messages shown verbatim to the user by the ticket flow.

Every other message in a conversation is authored by the LLM. These are the only
strings the product specifies word for word, so they live in one place to keep the
chat surface and the worker from drifting apart.
"""

CONFIRM_BUG = (
    "I've gathered all the information needed to report this issue to the "
    "DailoQA development team. Would you like me to proceed?"
)

CONFIRM_FEATURE = (
    "I've gathered all the information needed to submit this feature request to the "
    "DailoQA development team. Would you like me to proceed?"
)

EVIDENCE_REQUEST = (
    "Before I continue, could you attach any screenshots or a screen recording that "
    "show the problem?"
)

DECLINED = "Understood. This won't be submitted."

BUG_CREATED = (
    "Your bug report has been successfully submitted to the DailoQA development team. "
    "Thank you for helping us make Broccoli better."
)

BUG_LINKED = (
    "This issue has been reported previously and is currently under review. We've added "
    "your feedback to the existing ticket, and the DailoQA development team will review it. "
    "Thank you for bringing it to our attention."
)

FEATURE_SUBMITTED = (
    "Your feature request has been successfully submitted to the DailoQA development team. "
    "Thank you for sharing your ideas with us."
)

TICKET_FAILED = "We couldn't create your ticket. Please contact support."

_CONFIRMATIONS = {"bug": CONFIRM_BUG, "feature": CONFIRM_FEATURE}

_OUTCOMES = {
    ("bug", "create"): BUG_CREATED,
    ("bug", "link"): BUG_LINKED,
    ("feature", "create"): FEATURE_SUBMITTED,
    ("feature", "link"): FEATURE_SUBMITTED,
}


def confirmation_for(kind: str) -> str:
    """Return the confirmation question shown before a ticket of this kind is filed."""
    return _CONFIRMATIONS[kind]


def outcome_for(kind: str, action: str) -> str:
    """Return the terminal message for a finished job, by kind and create/link action."""
    return _OUTCOMES[(kind, action)]
