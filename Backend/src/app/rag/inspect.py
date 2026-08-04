"""Inspect what hybrid retrieval returns for an ad-hoc query.

Run from the Backend directory:

    python -m app.rag.inspect "How do MCP servers connect?"
    python -m app.rag.inspect -k 8 "What is a Skill?"

Prints the top chunks with their fused score, which arm(s) matched, source, heading,
and a content preview — so you can see exactly what the answer would be grounded in.
"""

import argparse
import asyncio
import sys

from sqlalchemy import text

from app.config import get_settings
from app.db.base import async_session
from app.rag.embeddings import aembed_query
from app.rag.store import _to_vector_literal

_ARM_SQL = text(
    """
    WITH semantic AS (
        SELECT id, (embedding <=> CAST(:qv AS vector)) AS dist,
               row_number() OVER (ORDER BY embedding <=> CAST(:qv AS vector)) AS rank
        FROM app.doc_chunks
        WHERE embedding <=> CAST(:qv AS vector) < :max_distance
        ORDER BY dist LIMIT :candidates
    ),
    lexical AS (
        SELECT id, ts_rank_cd(content_tsv, q) AS rank_score,
               row_number() OVER (ORDER BY ts_rank_cd(content_tsv, q) DESC) AS rank
        FROM app.doc_chunks, websearch_to_tsquery('english', :q_text) AS q
        WHERE content_tsv @@ q AND ts_rank_cd(content_tsv, q) > :min_rank
        ORDER BY rank_score DESC LIMIT :candidates
    )
    SELECT d.source_path, d.heading, left(d.content, 140) AS preview,
           s.dist AS sem_dist, s.rank AS sem_rank, l.rank_score AS lex_rank, l.rank AS lex_pos,
           COALESCE(1.0/(:rrf_k + s.rank), 0) + COALESCE(1.0/(:rrf_k + l.rank), 0) AS score
    FROM semantic s
    FULL OUTER JOIN lexical l ON s.id = l.id
    JOIN app.doc_chunks d ON d.id = COALESCE(s.id, l.id)
    ORDER BY score DESC
    LIMIT :k
    """
)


async def inspect(query: str, k: int) -> None:
    settings = get_settings()
    qv = _to_vector_literal(await aembed_query(query))
    async with async_session() as session:
        rows = (
            await session.execute(
                _ARM_SQL,
                {
                    "qv": qv,
                    "q_text": query,
                    "max_distance": settings.semantic_max_distance,
                    "min_rank": settings.lexical_min_rank,
                    "candidates": settings.rag_candidates,
                    "rrf_k": settings.rrf_k,
                    "k": k,
                },
            )
        ).mappings().all()

    print(f'\nquery: "{query}"')
    print(f"gates: semantic_max_distance={settings.semantic_max_distance}  lexical_min_rank={settings.lexical_min_rank}  k={k}")
    if not rows:
        print("\n-> NO CHUNKS pass the gates. The answer node would DECLINE (not in the docs).\n")
        return
    print(f"\n{'#':>2} {'score':>7} {'arms':<9} {'semdist':>7} {'source / heading'}")
    for i, r in enumerate(rows, 1):
        arms = "+".join(a for a, on in (("sem", r["sem_rank"]), ("lex", r["lex_pos"])) if on)
        sem = f"{r['sem_dist']:.3f}" if r["sem_dist"] is not None else "  -  "
        head = r["heading"] or "(intro)"
        print(f"{i:>2} {float(r['score']):7.4f} {arms:<9} {sem:>7} {r['source_path']} | {head}")
        print(f"      | {r['preview'].strip()[:120]}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect hybrid retrieval for a query.")
    parser.add_argument("query", help="the question to retrieve for")
    parser.add_argument("-k", type=int, default=None, help="number of chunks (default: rag_top_k)")
    args = parser.parse_args()

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(inspect(args.query, args.k or get_settings().rag_top_k))


if __name__ == "__main__":
    main()
