"""Middleware that keeps an answer's citations honest.

Three defects. The first two are opposites; the third is about a citation that is present and
real but attached to the wrong claim:

* **Fabricated** — the answer carries ``[Doc N]`` markers but no documentation tool ever ran.
  The citation points at nothing.
* **Uncited** — a documentation tool handed back passages and the answer used them without
  a single tag. The source is real but the reader cannot see it.
* **Misattributed** — the answer credits a library its own sources do not come from: "Guardrails
  in LangGraph are…" closing with a ``/docs/langchain/guardrails`` citation. Both halves are
  individually fine and the pair is wrong, which is why neither check above sees it.

The second half exists because prompt wording alone is compliance, not enforcement: the skill
instructions reached a 16/16 citation rate in live testing, but nothing structural stopped that
silently becoming 8/16 after an unrelated edit. This makes the guarantee independent of how well
the model is behaving on any given day.

**Still not a retrieval gate.** An answer that consults nothing and cites nothing passes through
here untouched — deciding *whether* to search is the skill's job, not this middleware's. What is
guaranteed is narrower and worth stating exactly: a citation exists if and only if passages were
retrieved, and the library the answer names is one its citations actually come from. It is still
not a per-claim guarantee — an answer citing ``[Doc 3]`` for a sentence that actually came from
``[Doc 1]`` passes, since both are real sources for the same answer.

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


_UNRESOLVED = (
    "You wrote {tags} in the answer but no Sources legend explains {them}. A bare [Doc N] is not "
    "a citation — the number means nothing on its own, and the reader has no page to open.\n\n"
    "Add the legend: close the answer with `Sources:` and one line per tag you used, each giving "
    "the label exactly as the tool provided it, ending in its /docs path — for example\n"
    "[Doc 1] langgraph/LangGraph overview (/docs/langgraph)\n\n"
    "Use only the numbers the tools assigned, list every tag that appears in your prose, and do "
    "not list tags you did not cite."
)

_MISATTRIBUTED = (
    "You attributed the answer to {claimed}, but the passages you cited are from the {cited} "
    "documentation. Do not take the library name from the question — take it from the source. "
    "Rewrite the answer naming the library the passages actually document.\n\n"
    "If {claimed} genuinely is the right place to look, then the passages you cited are the wrong "
    "ones: search again for the {claimed} page on this and answer from that instead. If the "
    "documentation covers this only under {cited}, say so plainly — that these are {cited} "
    "features — rather than describing them as though {claimed} provided them. Naming the wrong "
    "library sends the reader to a page where the thing they just read about does not exist."
)


OUT_OF_SCOPE_ANSWER = (
    "This is outside the DailoQA documentation scope. Please ask something about DailoQA, "
    "LangChain, LangGraph or Deep Agents, or ask me to file a bug report or feature request."
)
"""What the user is shown instead of an answer the documentation does not support.

Edit this string to change the wording; nothing else needs to move.
"""

# A fenced block. The opener alone is enough -- an unterminated fence still reads as code.
_CODE_FENCE = re.compile(r"^\s*```", re.MULTILINE)

# Phrasings that make an uncited answer a *decline*, which is a correct answer and must survive.
_DECLINING = re.compile(
    # "appear" and "exist" are here because leaving them out is a live hazard, not an omission:
    # "the term does not appear in the documentation" is a textbook correct decline, and a gate
    # that replaces it destroys the exact behaviour the rest of this module works to produce.
    # Erring toward recognising a decline is the safe direction -- a missed fabrication is the
    # bug we already had, a replaced decline is a new one.
    r"does(?:n['’]t| not)\s+(?:\w+\s+){0,3}"
    r"(?:mention|cover|describe|discuss|include|provide|specify|define|detail|address|state|say"
    r"|contain|appear|exist|reference)"
    r"|no mention|not (?:mentioned|covered|documented|described|appear\w*)"
    r"|could(?:n['’]t| not) find|did(?:n['’]t| not) find|unable to find"
    r"|i can only (?:help|assist)|outside the .{0,30}scope|can'?t (?:help|assist) with"
    r"|i can'?t provide|is not (?:a |an )?(?:documented|mentioned)",
    re.IGNORECASE,
)

# Below this, an uncited answer is too short to be a fabricated explanation: scope refusals,
# clarifying questions and one-line declines all sit here. Measured on real turns -- the
# fabrications ran 613 and 1705 characters, the refusals and clarifications 100 to 300.
_SUBSTANTIAL = 420


def ungrounded_answer(messages, answer: str) -> bool:
    """Whether a final answer asserts things no retrieved passage backs.

    The gate the middleware's retry could not be. Bouncing an ungrounded answer back to the model
    makes it *worse*: measured twice, the retry declines a question the corpus covers rather than
    fixing the citation, because declining is the cheaper way to satisfy the correction. So this
    reports, and the runner substitutes a fixed sentence instead of asking for a rewrite.

    Deliberately narrow, because the cost of a false positive is replacing a good answer:

    * Anything carrying ``[Doc N]`` is grounded by the checks above and never reaches here.
    * A decline is the *correct* uncited answer and is recognised by its wording.
    * Short uncited replies -- scope refusals, clarifying questions -- are left alone.
    * Nothing fires unless a citing tool actually returned passages this thread, so ticket flows,
      which retrieve nothing, are untouched by construction.

    What is left is the observed failure: a long uncited explanation, or a code sample, produced
    after the documentation was consulted and not built from it. Five turns into one conversation
    that was a complete "AI chatbot in LangGraph" built on ``compiled_graph.run()``, which is not
    a LangGraph API.
    """
    if not passages_were_offered(messages) or _CITATION.search(answer):
        return False
    if _DECLINING.search(answer):
        return False
    return bool(_CODE_FENCE.search(answer)) or len(answer.strip()) >= _SUBSTANTIAL


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


# The three libraries the corpus documents, keyed by the topic that appears in a citation
# route (/docs/langgraph/...) and in the label's leading folder (langgraph/Persistence).
_PRODUCTS = {"deepagents": "Deep Agents", "langchain": "LangChain", "langgraph": "LangGraph"}
_TOPIC_ALIASES = {"deep-agents": "deepagents"}

# A tool hands passages over as "[Doc 3: langchain/Guardrails - ... (/docs/langchain/guardrails)]";
# the model writes "[Doc 3]" back. The first form carries the topic, the second is what the
# answer's attribution has to be checked against, so both are needed to connect the two.
_TAGGED_PASSAGE = re.compile(r"\[doc\s*(\d+)\s*:([^\]\n]*)", re.IGNORECASE)
_TAG_NUMBER = re.compile(r"\[doc\s*(\d+)", re.IGNORECASE)
_ROUTE_TOPIC = re.compile(r"/docs/(deepagents|langchain|langgraph)\b")
_LABEL_TOPIC = re.compile(r"\b(deep-agents|deepagents|langchain|langgraph)\s*/")

# Attributive positions only: "Guardrails **in LangGraph** are…", "**LangGraph's** checkpointer".
# Provenance is deliberately not matched -- "the subagents middleware **from** Deep Agents" is how
# the documentation itself describes a Deep Agents component used inside LangChain, and flagging
# that would bounce the one phrasing that is precisely correct.
_ATTRIBUTED = re.compile(
    r"\bin\s+(LangChain|LangGraph|Deep\s?Agents)\b"
    r"|\b(LangChain|LangGraph|Deep\s?Agents)(?:'s|’s)\b",
    re.IGNORECASE,
)

_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
_NEGATED = re.compile(r"\bn(?:o|ot|ever)\b|n['’]t\b|\binstead\b|\brather than\b", re.IGNORECASE)


# A legend line pairs the tag with a label ending in the page's route:
#   [Doc 1] langgraph/LangGraph overview (/docs/langgraph)
_LEGEND_ENTRY = re.compile(r"\[doc\s*(\d+)\][^\n]*\(/docs/[^)\n]*\)", re.IGNORECASE)
_ANY_TAG = re.compile(r"\[doc\s*(\d+)", re.IGNORECASE)


def _unresolved_citations(answer: str) -> set[str]:
    """Tag numbers used in the prose that no legend line resolves to a page.

    Seen in a real conversation: an answer carrying "[Doc 1]" and "[Doc 5]" and no legend at all.
    Every existing check passed it — a citation was present, it was backed by retrieved passages,
    and the attribution matched — because all three ask whether a tag *exists*, not whether it
    *resolves*. To the reader a bare number is worse than no citation: nothing to open, and the
    answer looks sourced anyway.
    """
    resolved = set(_LEGEND_ENTRY.findall(answer))
    return set(_ANY_TAG.findall(answer)) - resolved


def _topic_of_label(label: str) -> str | None:
    """The library a citation label points at, from its route or its leading folder."""
    route = _ROUTE_TOPIC.search(label)
    if route:
        return route.group(1)
    folder = _LABEL_TOPIC.search(label)
    if folder:
        topic = folder.group(1).lower()
        return _TOPIC_ALIASES.get(topic, topic)
    return None


def _cited_topics(answer: str, passages: str) -> set[str]:
    """The libraries the answer's own ``[Doc N]`` tags resolve to."""
    by_number = {}
    for number, label in _TAGGED_PASSAGE.findall(passages):
        topic = _topic_of_label(label)
        if topic:
            by_number[number] = topic
    return {by_number[n] for n in _TAG_NUMBER.findall(answer) if n in by_number}


def _claimed_topics(answer: str) -> set[str]:
    """The libraries the answer's prose credits, in attributive position.

    **A negated mention is not a claim, and skipping it is load-bearing.** The correct answer to
    "what are guardrails in LangGraph?" opens *"The documentation does not cover guardrails in
    LangGraph. Instead, guardrails are features provided by LangChain"* — which contains the exact
    phrase this looks for, in the exact position, while saying the opposite of the failure it
    exists to catch. Reading attribution without reading the negation around it bounced that
    answer, so the check was rejecting the behaviour it was added to produce.

    Sentence-level rather than clause-level on purpose: the denial and the topic sit in one
    sentence in every phrasing observed, and a looser window starts swallowing the next sentence's
    genuine claim.
    """
    claimed = set()
    for sentence in _SENTENCE.split(answer):
        if _NEGATED.search(sentence):
            continue
        for match in _ATTRIBUTED.finditer(sentence):
            name = (match.group(1) or match.group(2)).lower().replace(" ", "")
            if name in _PRODUCTS:
                claimed.add(name)
    return claimed


def _misattribution(answer: str, passages: str) -> tuple[str, str] | None:
    """A library the answer credits that none of its citations come from.

    The failure this catches, seen live on all four probes of its kind: the model takes the
    library name straight from the question and applies it to whatever was retrieved. "What are
    guardrails in LangGraph?" came back as "Guardrails in LangGraph are…" citing five passages
    that were, every one of them, from ``langchain/guardrails.md``.

    Retrieval was not at fault in any of them — it returned the right pages, and in one case
    ranked the genuinely correct cross-library page first. Only the prose was wrong, which is
    why this reads the answer against its own citations rather than against the search results.
    """
    cited = _cited_topics(answer, passages)
    if not cited:
        return None  # nothing resolvable to check against; the other two checks cover this
    stray = _claimed_topics(answer) - cited
    if not stray:
        return None
    claimed_names = ", ".join(sorted(_PRODUCTS[t] for t in stray))
    cited_names = ", ".join(sorted(_PRODUCTS[t] for t in cited))
    return (
        f"answer credits {claimed_names} but cites {cited_names}",
        _MISATTRIBUTED.format(claimed=claimed_names, cited=cited_names),
    )


def _problem(messages, last) -> tuple[str, str] | None:
    """The citation defect in a final answer, as (log phrase, correction), or None if clean.

    Three failures, and the checks are not symmetric:

    * **cited but nothing retrieved** — the citation is invented. Detected by whether a citing
      tool *ran*, since a tool that ran and found nothing still cannot justify a `[Doc N]`.
    * **retrieved but nothing cited** — documentation was used without credit. Detected by
      whether the answer's wording actually came from the passages, not merely by whether
      passages arrived: an agent that searched, found nothing relevant and declined owes them
      nothing, and bouncing it was how the irrelevant citations got manufactured.
    * **cited but credited to the wrong library** — checked only once the citations are known to
      be real, since an answer whose tags point at nothing has a worse problem than attribution.
    """
    answer = _text(last)
    if _CITATION.search(answer):
        if not citable_passages_retrieved(messages):
            return "citations with no documentation lookup", _FABRICATED
        unresolved = _unresolved_citations(answer)
        if unresolved:
            tags = ", ".join(f"[Doc {n}]" for n in sorted(unresolved, key=int))
            them = "it" if len(unresolved) == 1 else "them"
            return (
                f"citation tags with no legend entry: {tags}",
                _UNRESOLVED.format(tags=tags, them=them),
            )
        return _misattribution(answer, offered_passages(messages))

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
