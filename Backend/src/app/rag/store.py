"""Data access for the RAG corpus (``app.doc_chunks``).

This module is the shared boundary between ingestion and retrieval:

- ``upsert_chunks`` (write path) is implemented in Phase 1 — used by ``ingest.py``.
- ``search`` (read path) is implemented in Phase 2 — the hybrid semantic + lexical
  retrieval the answer node calls.

Both are independent functions in this one file, so the two phases can be built in
parallel and merge cleanly. Phase 0 ships only the skeleton (types + signatures).
"""

import logging
import time
from dataclasses import dataclass

from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import DocChunk

logger = logging.getLogger(__name__)

__all__ = [
    "ChunkRow",
    "RetrievedChunk",
    "SourceOutline",
    "DocSection",
    "INTRO_HEADING",
    "strip_context_prefix",
    "upsert_chunks",
    "delete_missing_sources",
    "list_sources",
    "fetch_section",
    "search",
]


@dataclass(frozen=True)
class ChunkRow:
    """A chunk ready to be written to ``app.doc_chunks`` by ingestion."""

    source_path: str
    title: str | None
    heading: str | None
    chunk_index: int
    content: str
    embedding: list[float]


@dataclass(frozen=True)
class RetrievedChunk:
    """A chunk returned by hybrid retrieval, with its fused relevance score."""

    id: str
    source_path: str
    title: str | None
    heading: str | None
    content: str
    score: float


@dataclass(frozen=True)
class SourceOutline:
    """One document and the headings it contains, for the agent to browse."""

    source_path: str
    title: str | None
    headings: list[str]


@dataclass(frozen=True)
class DocSection:
    """A whole section reassembled from its consecutive chunks."""

    source_path: str
    title: str | None
    heading: str | None
    content: str
    chunk_ids: list[str]
    truncated: bool


# Ingestion prepends a context line to every chunk ("<title> > <heading>" or just
# "<title>" for a document intro). Reassembling a section verbatim would repeat that
# line once per chunk, so it is stripped from each and re-emitted once by the caller.
def strip_context_prefix(content: str, title: str | None, heading: str | None) -> str:
    """Remove the ingestion-added "<title> > <heading>" line from one chunk's text.

    Also used when presenting search hits, where the tools render the same information
    in the citation tag and would otherwise show it twice.
    """
    prefix = f"{title} > {heading}" if heading else (title or "")
    body = content
    if prefix and body.startswith(prefix):
        body = body[len(prefix):]
    return body.lstrip("\n")


async def upsert_chunks(session: AsyncSession, source_path: str, rows: list[ChunkRow]) -> int:
    """Replace all chunks for ``source_path`` with ``rows`` (delete-then-insert).

    Idempotent per source file: re-ingesting a document fully replaces its prior chunks,
    so edits and re-orderings never leave stale rows behind. The caller commits.
    """
    await session.execute(delete(DocChunk).where(DocChunk.source_path == source_path))
    session.add_all(
        DocChunk(
            source_path=row.source_path,
            title=row.title,
            heading=row.heading,
            chunk_index=row.chunk_index,
            content=row.content,
            embedding=row.embedding,
        )
        for row in rows
    )
    await session.flush()
    return len(rows)


INTRO_HEADING = "(intro)"

_MAX_SECTION_CHARS = 8000


async def list_sources(session: AsyncSession) -> list[SourceOutline]:
    """Return every document with its headings, in document order.

    Headings are returned **verbatim** because ``fetch_section`` matches on the exact
    trail string. A document's lead-in chunks carry no heading; they are surfaced as
    ``INTRO_HEADING`` so the agent has a name it can pass back.
    """
    rows = (
        await session.execute(
            select(DocChunk.source_path, DocChunk.title, DocChunk.heading, func.min(DocChunk.chunk_index))
            .group_by(DocChunk.source_path, DocChunk.title, DocChunk.heading)
            .order_by(DocChunk.source_path, func.min(DocChunk.chunk_index))
        )
    ).all()

    outlines: dict[str, SourceOutline] = {}
    for source_path, title, heading, _ in rows:
        outline = outlines.get(source_path)
        if outline is None:
            outline = SourceOutline(source_path=source_path, title=title, headings=[])
            outlines[source_path] = outline
        outline.headings.append(heading or INTRO_HEADING)
    return list(outlines.values())


async def fetch_section(session: AsyncSession, source_path: str, heading: str | None) -> DocSection | None:
    """Reassemble one section from its consecutive chunks, or None if it does not exist.

    A section's chunks share a heading and hold contiguous ``chunk_index`` values, so
    ordering by index restores the original prose. Each chunk's repeated context line is
    stripped and the output is capped, since a long section (code-sample heavy pages run
    to a dozen chunks) would otherwise swamp the model's context.
    """
    is_intro = heading is None or heading == INTRO_HEADING
    condition = DocChunk.heading.is_(None) if is_intro else DocChunk.heading == heading
    rows = (
        await session.execute(
            select(DocChunk)
            .where(DocChunk.source_path == source_path, condition)
            .order_by(DocChunk.chunk_index)
        )
    ).scalars().all()
    if not rows:
        return None

    body = "\n\n".join(strip_context_prefix(row.content, row.title, row.heading) for row in rows)
    truncated = len(body) > _MAX_SECTION_CHARS
    if truncated:
        body = body[:_MAX_SECTION_CHARS].rstrip() + "\n\n[section truncated]"
    return DocSection(
        source_path=source_path,
        title=rows[0].title,
        heading=rows[0].heading,
        content=body,
        chunk_ids=[row.id for row in rows],
        truncated=truncated,
    )


async def delete_missing_sources(session: AsyncSession, valid_paths: list[str]) -> int:
    """Delete chunks whose ``source_path`` is not in ``valid_paths`` (ghost-chunk sweep).

    Run before per-file upsert so renamed or removed documents leave no orphan rows.
    Returns the number of rows deleted. The caller commits.
    """
    result = await session.execute(
        delete(DocChunk).where(DocChunk.source_path.not_in(valid_paths))
    )
    return result.rowcount or 0


# Hybrid retrieval in one round-trip. Each arm is gated on an absolute relevance
# threshold *before* fusion (RRF scores are rank-based and cannot themselves gate
# relevance), then fused with Reciprocal Rank Fusion: score = Σ 1/(rrf_k + rank).
_HYBRID_SQL = text(
    """
    WITH semantic AS (
        SELECT id, source_path, title, heading, content,
               row_number() OVER (ORDER BY embedding <=> CAST(:qv AS vector)) AS rank
        FROM app.doc_chunks
        WHERE embedding <=> CAST(:qv AS vector) < :max_distance
        ORDER BY embedding <=> CAST(:qv AS vector)
        LIMIT :candidates
    ),
    lexical AS (
        SELECT id, source_path, title, heading, content,
               row_number() OVER (ORDER BY ts_rank_cd(content_tsv, q) DESC) AS rank
        FROM app.doc_chunks, websearch_to_tsquery('english', :q_text) AS q
        WHERE content_tsv @@ q
          AND ts_rank_cd(content_tsv, q) > :min_rank
        ORDER BY ts_rank_cd(content_tsv, q) DESC
        LIMIT :candidates
    )
    SELECT
        COALESCE(s.id, l.id)                     AS id,
        COALESCE(s.source_path, l.source_path)   AS source_path,
        COALESCE(s.title, l.title)               AS title,
        COALESCE(s.heading, l.heading)           AS heading,
        COALESCE(s.content, l.content)           AS content,
        COALESCE(1.0 / (:rrf_k + s.rank), 0)
          + COALESCE(1.0 / (:rrf_k + l.rank), 0) AS score,
        (s.id IS NOT NULL)                       AS in_semantic,
        (l.id IS NOT NULL)                       AS in_lexical
    FROM semantic s
    FULL OUTER JOIN lexical l ON s.id = l.id
    ORDER BY score DESC
    LIMIT :k
    """
)


def _to_vector_literal(vector: list[float]) -> str:
    """Render an embedding as a pgvector text literal, e.g. '[0.1,0.2,...]'."""
    return "[" + ",".join(repr(float(x)) for x in vector) + "]"


async def search(
    session: AsyncSession,
    query_text: str,
    query_vector: list[float],
    k: int,
) -> list[RetrievedChunk]:
    """Hybrid retrieval: semantic + lexical arms, per-arm gated, fused via RRF.

    Returns the top-``k`` chunks, or ``[]`` when both arms are empty after gating —
    that empty result is the signal the answer node's guardrail keys off (never a
    fused-score cutoff).
    """
    settings = get_settings()
    started = time.perf_counter()
    result = await session.execute(
        _HYBRID_SQL,
        {
            "qv": _to_vector_literal(query_vector),
            "q_text": query_text,
            "max_distance": settings.semantic_max_distance,
            "min_rank": settings.lexical_min_rank,
            "candidates": settings.rag_candidates,
            "rrf_k": settings.rrf_k,
            "k": k,
        },
    )
    rows = result.mappings().all()
    elapsed_ms = (time.perf_counter() - started) * 1000

    chunks = [
        RetrievedChunk(
            id=row["id"],
            source_path=row["source_path"],
            title=row["title"],
            heading=row["heading"],
            content=row["content"],
            score=float(row["score"]),
        )
        for row in rows
    ]

    semantic_hits = sum(1 for row in rows if row["in_semantic"])
    lexical_hits = sum(1 for row in rows if row["in_lexical"])
    logger.info(
        "rag.search query=%r k=%d returned=%d semantic=%d lexical=%d latency_ms=%.1f",
        query_text[:120], k, len(chunks), semantic_hits, lexical_hits, elapsed_ms,
    )
    for chunk in chunks:
        logger.debug("rag.search hit id=%s source=%s score=%.5f", chunk.id, chunk.source_path, chunk.score)
    return chunks
