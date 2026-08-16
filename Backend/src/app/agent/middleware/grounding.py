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

from app.agent.tools import citable_passages_retrieved, offered_passages, passages_were_offered

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
    "Your answer used documentation passages but cited none of them. There are two correct "
    "outcomes here and you must pick the one that is true.\n\n"
    "If the passages do answer the question: rewrite the answer with the [Doc N] tag on every "
    "claim they support, including any code sample, and close with a Sources: legend listing "
    "each tag and its label exactly as the tool gave it. Use only the numbers the tools "
    "assigned; do not invent or renumber them.\n\n"
    "If the passages do NOT answer the question — they are about the same product but not the "
    "thing that was asked about — then say exactly that and stop, with no citations at all. Do "
    "not manufacture a connection between the question and a passage that merely shares its "
    "topic, and do not add a sentence surveying what the documentation happens to contain just "
    "to have something to cite. An invented explanation with a real citation attached is the "
    "worst answer you can give, because the citation is what makes it look verified."
)


def _text(message) -> str:
    """Flatten a message's content, which providers return as a string or as blocks."""
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    return "".join(part.get("text", "") for part in content if isinstance(part, dict))


# Words too common to say anything about where a sentence came from.
_NOISE = frozenset(
    "the a an and or of to in for is are was be been with that this these those it as on by "
    "from can could you your we our they them their if when how what which not no do does did "
    "have has had will would should may might must there here about into over under more most "
    "some any each other than then so such but at up out only own same too very".split()
)
_WORD = re.compile(r"[a-z][a-z0-9_-]{2,}")

# Measured on real turns: declines scored 0.17 and 0.36, answers built on passages 0.78 and
# 0.80. The threshold sits in that gap with room either side.
_DERIVED_FROM_PASSAGES = 0.55


def _overlap_with(answer: str, passages: str) -> float:
    """How much of an answer's vocabulary comes from the passages it was given."""
    words = {w for w in _WORD.findall(answer.lower()) if w not in _NOISE}
    if not words:
        return 0.0
    source = {w for w in _WORD.findall(passages.lower()) if w not in _NOISE}
    return len(words & source) / len(words)


def _problem(messages, last) -> tuple[str, str] | None:
    """The citation defect in a final answer, as (log phrase, correction), or None if clean.

    Two failures, opposite directions, and the checks are not symmetric:

    * **cited but nothing retrieved** — the citation is invented. Detected by whether a citing
      tool *ran*, since a tool that ran and found nothing still cannot justify a `[Doc N]`.
    * **retrieved but nothing cited** — documentation was used without credit. Detected by
      whether the answer's wording actually came from the passages, not merely by whether
      passages arrived: an agent that searched, found nothing relevant and declined owes them
      nothing, and bouncing it was how the irrelevant citations got manufactured.
    """
    if _CITATION.search(_text(last)):
        if citable_passages_retrieved(messages):
            return None  # citations are backed by passages the agent actually received
        return "citations with no documentation lookup", _FABRICATED

    if passages_were_offered(messages):
        # Only an answer actually built on the passages owes them a citation. A decline is not,
        # and demanding one was making things worse rather than better: with nothing relevant
        # retrieved, the only way to satisfy the check was to write a sentence about whatever
        # came back and cite that — "it discusses subgraph communication [Doc 1][Doc 2][Doc 5]"
        # under an answer about shortest paths. The enforcement was manufacturing the irrelevant
        # sources it was supposed to prevent.
        if _overlap_with(_text(last), offered_passages(messages)) >= _DERIVED_FROM_PASSAGES:
            return "documentation passages used without citation", _UNCITED
    return None  # nothing cited and nothing drawn from the passages: a decline, or a ticket reply


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
