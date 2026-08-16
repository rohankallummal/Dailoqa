"""BM25 ranking over the documentation bundle's sections.

Retrieval is lexical and local. The bundle is small and fixed, the gateway offers no
embedding deployment, and a documentation question almost always carries the vocabulary
of the page that answers it -- ``checkpointer``, ``interrupt``, ``create_agent``. Ranking
in-process also means a search never leaves the container, so it cannot fail the way a
model call behind the VPN can.

Identifiers are indexed whole and in parts, so ``create_agent`` is found by "create agent"
and ``InMemoryStore`` by "in memory store".
"""

import math
import re
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache

from app.knowledge.bundle import Section, sections

_K1 = 1.5
_B = 0.75
_TITLE_WEIGHT = 3
_PAGE_TITLE_WEIGHT = 2

_WORD = re.compile(r"[a-z0-9_]+")
_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")

_STOPWORDS = frozenset(
    """a an the and or but if then than that this these those is are was were be been being
    do does did doing have has had having i you he she it we they what which who whom how
    when where why can could should would may might must will just about into over under
    to of in on at by for with as from up down out so no not only own same too very s t
    me my your his her its our their there here does doing use using used get gets""".split()
)


@dataclass(frozen=True)
class Hit:
    """One ranked section, with the relevance and the term overlap that ranked it."""

    section: Section
    score: float
    matched: tuple[str, ...]
    missing: tuple[str, ...]


def tokenize(text: str) -> list[str]:
    """Split text into search terms, keeping identifiers whole and adding their parts."""
    spaced = _CAMEL.sub(" ", text)
    terms: list[str] = []
    for word in _WORD.findall(spaced.lower()):
        if word in _STOPWORDS:
            continue
        terms.append(word)
        parts = [part for part in word.split("_") if part and part not in _STOPWORDS]
        terms.extend(parts if len(parts) > 1 else [])
    return terms


def _indexed_text(section: Section) -> str:
    """Weight a section's own heading and its page title above its body."""
    return " ".join(
        [
            *([section.title] * _TITLE_WEIGHT),
            *([section.page_title] * _PAGE_TITLE_WEIGHT),
            section.product,
            section.text,
        ]
    )


@dataclass(frozen=True)
class Index:
    """A BM25 index over every section in the bundle."""

    documents: tuple[Counter, ...]
    lengths: tuple[int, ...]
    average_length: float
    frequencies: dict[str, int]
    entries: tuple[Section, ...]

    def score(self, terms: list[str], position: int) -> float:
        """Score one section against the query terms."""
        counts = self.documents[position]
        length = self.lengths[position] or 1
        total = 0.0
        for term in set(terms):
            occurrences = counts.get(term, 0)
            if not occurrences:
                continue
            saturation = occurrences * (_K1 + 1)
            normaliser = occurrences + _K1 * (1 - _B + _B * length / self.average_length)
            total += self._inverse_frequency(term) * saturation / normaliser
        return total

    def _inverse_frequency(self, term: str) -> float:
        """Weight a term by how rare it is across the bundle."""
        total = len(self.entries)
        containing = self.frequencies.get(term, 0)
        return math.log(1 + (total - containing + 0.5) / (containing + 0.5))


@lru_cache
def index() -> Index:
    """Build the BM25 index once per process."""
    entries = sections()
    documents = tuple(Counter(tokenize(_indexed_text(section))) for section in entries)
    lengths = tuple(sum(counts.values()) for counts in documents)
    frequencies: Counter = Counter()
    for counts in documents:
        frequencies.update(counts.keys())
    average = sum(lengths) / len(lengths) if lengths else 1.0
    return Index(documents, lengths, average or 1.0, dict(frequencies), entries)


def search(query: str, limit: int = 5, product: str | None = None) -> list[Hit]:
    """Return the sections that best match a query, best first.

    A section is returned only when it shares at least one term with the query, so an
    empty result means genuinely no lexical overlap and is a reliable signal that the
    bundle does not cover the question.

    There is deliberately no score threshold above that. BM25 scores a common word like
    "agent" near zero because it appears nearly everywhere, and a threshold tuned to
    reject an off-topic question would also reject "what is an agent" -- a question the
    documentation answers on its first page. Judging whether an overlapping section
    actually answers the question is the caller's job, which is why every hit carries the
    query terms it does and does not contain.
    """
    terms = tokenize(query)
    if not terms:
        return []
    built = index()
    wanted = product.strip().lower() if product else None
    distinct = sorted(set(terms))
    hits = [
        _hit(built, section, position, terms, distinct)
        for position, section in enumerate(built.entries)
        if wanted is None or section.product == wanted
    ]
    relevant = [hit for hit in hits if hit.matched]
    relevant.sort(key=lambda hit: hit.score, reverse=True)
    return relevant[:limit]


def _hit(built: Index, section: Section, position: int, terms: list[str], distinct: list[str]) -> Hit:
    """Score one section and record which of the query's terms it actually contains."""
    counts = built.documents[position]
    matched = tuple(term for term in distinct if counts.get(term))
    missing = tuple(term for term in distinct if not counts.get(term))
    return Hit(section, built.score(terms, position), matched, missing)
