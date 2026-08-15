"""Middleware that keeps an answer's citations honest in both directions.

Two defects, and they are opposites:

* **Fabricated** — the answer carries ``[Doc N]`` markers but no documentation tool ever ran.
  The citation points at nothing.
* **Uncited** — a documentation tool handed back passages and the answer used them without
  a single tag. The source is real but the reader cannot see it.

The second half exists because prompt wording alone is compliance, not enforcement: the skill
instructions reached a 16/16 citation rate in live testing, but nothing structural stopped that
silently becoming 8/16 after an unrelated edit. This makes the guarantee independent of how well
the model is behaving on any given day.

**Still not a retrieval gate.** An answer that consults nothing and cites nothing passes through
here untouched — deciding *whether* to search is the skill's job, not this middleware's. What is
guaranteed is narrower and worth stating exactly: a citation exists if and only if passages were
retrieved. It is not a claim-level guarantee, so an answer citing ``[Doc 3]`` for a sentence that
actually came from ``[Doc 1]`` still passes; catching that needs per-claim attribution.

Scoping falls out of the same rule. Ticket answers neither cite nor retrieve documentation, so
they satisfy both directions trivially and the check needs no notion of which skill is running.
"""

import logging
import re

from langchain.agents.middleware import after_model
from langchain_core.messages import SystemMessage

from app.agent.tools import citable_passages_retrieved, passages_were_offered

logger = logging.getLogger(__name__)

_MAX_CORRECTIONS = 1

# Matches both the tag a tool emits ("[Doc 2: Title - Heading]") and the marker a model
# writes inline ("[Doc 2]", "[Doc 1, Doc 3]").
_CITATION = re.compile(r"\[doc\s*\d+", re.IGNORECASE)

_FABRICATED = (
    "You cited the documentation but never called a documentation tool, so those "
    "citations are not backed by anything you read. Call search_documentation now and "
    "answer only from what it returns. If it returns nothing relevant, tell the user the "
    "documentation does not cover it."
)

_UNCITED = (
    "You answered from documentation passages but cited none of them. Rewrite the answer with "
    "the [Doc N] tag on every claim it came from, including any code sample, and close with a "
    "Sources: legend listing each tag and its label exactly as the tool gave it. Use only the "
    "numbers the tools assigned; do not invent or renumber them."
)


def _text(message) -> str:
    """Flatten a message's content, which providers return as a string or as blocks."""
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    return "".join(part.get("text", "") for part in content if isinstance(part, dict))


def _problem(messages, last) -> tuple[str, str] | None:
    """The citation defect in a final answer, as (log phrase, correction), or None if clean.

    Two failures, opposite directions, and the checks are not symmetric:

    * **cited but nothing retrieved** — the citation is invented. Detected by whether a citing
      tool *ran*, since a tool that ran and found nothing still cannot justify a `[Doc N]`.
    * **retrieved but nothing cited** — documentation was used without credit. Detected by
      whether a citing tool actually *returned a passage*, because an agent that searched, got
      nothing, and correctly declined has no passages to cite and must not be bounced for it.
    """
    if _CITATION.search(_text(last)):
        if citable_passages_retrieved(messages):
            return None  # citations are backed by passages the agent actually received
        return "citations with no documentation lookup", _FABRICATED

    if passages_were_offered(messages):
        return "documentation passages used without citation", _UNCITED
    return None  # nothing cited and nothing to cite: a decline, or a non-documentation turn


@after_model(can_jump_to=["model"])
def require_documentation(state, runtime):
    """Send an answer whose citations do not match what was retrieved back to the model.

    At most once per turn, in either direction.
    """
    messages = state["messages"]
    if not messages:
        return None

    last = messages[-1]
    if getattr(last, "tool_calls", None):
        return None  # still working; only final answers are inspected

    problem = _problem(messages, last)
    if problem is None:
        return None
    phrase, correction = problem

    context = runtime.context
    corrections = getattr(context, "grounding_corrections", 0)
    if corrections >= _MAX_CORRECTIONS:
        # Bounded on purpose: a model that will not comply must still terminate.
        logger.warning("rag.grounding correction limit reached; letting the answer through")
        return None

    context.grounding_corrections = corrections + 1
    logger.info("rag.grounding %s; asking for a retry", phrase)
    return {"jump_to": "model", "messages": [SystemMessage(content=correction)]}
