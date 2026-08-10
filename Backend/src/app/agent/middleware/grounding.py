"""Middleware that refuses a documentation citation the agent never looked up.

What this catches is **fabricated citations**: an answer carrying ``[Doc N]`` markers when
no documentation tool ran in the thread. It is deliberately not a retrieval gate — a model
that answers a product question from its own knowledge and cites nothing passes through
here, and only the skill's instructions push back on that. The honest framing is a
citation-integrity check: it makes the citation format mean something, so a cited answer
is one the agent actually read.

Scoping falls out of the citation format. Ticket answers never carry ``[Doc N]``, so they
are never inspected, and the check needs no notion of which skill is in play.
"""

import logging
import re

from langchain.agents.middleware import after_model
from langchain_core.messages import SystemMessage

from app.agent.tools import citable_passages_retrieved

logger = logging.getLogger(__name__)

_MAX_CORRECTIONS = 1

# Matches both the tag a tool emits ("[Doc 2: Title - Heading]") and the marker a model
# writes inline ("[Doc 2]", "[Doc 1, Doc 3]").
_CITATION = re.compile(r"\[doc\s*\d+", re.IGNORECASE)

_CORRECTION = (
    "You cited the documentation but never called a documentation tool, so those "
    "citations are not backed by anything you read. Call search_documentation now and "
    "answer only from what it returns. If it returns nothing relevant, tell the user the "
    "documentation does not cover it."
)


def _text(message) -> str:
    """Flatten a message's content, which providers return as a string or as blocks."""
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    return "".join(part.get("text", "") for part in content if isinstance(part, dict))


@after_model(can_jump_to=["model"])
def require_documentation(state, runtime):
    """Send a cited-but-unsourced answer back to the model, at most once per turn."""
    messages = state["messages"]
    if not messages:
        return None

    last = messages[-1]
    if getattr(last, "tool_calls", None):
        return None  # still working; only final answers are inspected
    if not _CITATION.search(_text(last)):
        return None  # no citations claimed, nothing to verify
    if citable_passages_retrieved(messages):
        return None  # the citations are backed by passages the agent actually received

    context = runtime.context
    corrections = getattr(context, "grounding_corrections", 0)
    if corrections >= _MAX_CORRECTIONS:
        # Bounded on purpose: a model that will not comply must still terminate.
        logger.warning("rag.grounding correction limit reached; letting the answer through")
        return None

    context.grounding_corrections = corrections + 1
    logger.info("rag.grounding citations with no documentation lookup; asking for a retry")
    return {"jump_to": "model", "messages": [SystemMessage(content=_CORRECTION)]}
