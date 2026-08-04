"""Calibrate retrieval thresholds against the golden set.

Run from the Backend directory:

    python -m app.rag.evaluate

Sweeps ``semantic_max_distance``, ``lexical_min_rank``, and ``rag_top_k`` over
``eval/golden_set.json`` and reports, per configuration:

- hit@k  — fraction of positive questions whose expected source/section is retrieved,
- MRR    — mean reciprocal rank of that first correct chunk,
- decline — fraction of negative (absent-topic) questions that correctly retrieve nothing.

Embeddings are computed once per question; only the SQL gates/k change per combo, so the
sweep is fast. Nothing is written back — pick a config from the table and set it in config.py.
"""

import asyncio
import json
import sys
from itertools import product
from pathlib import Path

from app.config import get_settings
from app.db.base import async_session
from app.rag.embeddings import aembed_query
from app.rag.store import search

_DISTANCES = [0.35, 0.40, 0.42, 0.45, 0.50]
_MIN_RANKS = [0.01, 0.05, 0.10]
_TOP_KS = [3, 5, 8]


def _golden_path() -> Path:
    return Path(__file__).resolve().parents[3] / "eval" / "golden_set.json"


def _is_hit(chunks, expected_source: str, expected_section) -> int:
    """Rank (1-based) of the first chunk matching the expected source/section, else 0."""
    for rank, chunk in enumerate(chunks, start=1):
        if chunk.source_path != expected_source:
            continue
        if expected_section and expected_section.lower() not in (chunk.heading or "").lower():
            continue
        return rank
    return 0


async def _embed_all(items) -> list[list[float]]:
    return [await aembed_query(item["q"]) for item in items]


async def evaluate() -> None:
    golden = json.loads(_golden_path().read_text(encoding="utf-8"))
    positives, negatives = golden["positives"], golden["negatives"]

    pos_vecs = await _embed_all(positives)
    neg_vecs = await _embed_all(negatives)

    settings = get_settings()
    saved = (settings.semantic_max_distance, settings.lexical_min_rank)
    rows = []

    async with async_session() as session:
        for distance, min_rank, k in product(_DISTANCES, _MIN_RANKS, _TOP_KS):
            settings.semantic_max_distance = distance
            settings.lexical_min_rank = min_rank

            hits, rr = 0, 0.0
            for item, vec in zip(positives, pos_vecs):
                chunks = await search(session, item["q"], vec, k)
                rank = _is_hit(chunks, item["source"], item.get("section"))
                if rank:
                    hits += 1
                    rr += 1.0 / rank

            declined = 0
            for item, vec in zip(negatives, neg_vecs):
                chunks = await search(session, item["q"], vec, k)
                if not chunks:
                    declined += 1

            hit_rate = hits / len(positives)
            mrr = rr / len(positives)
            decline_rate = declined / len(negatives)
            composite = hit_rate + decline_rate  # reward recall AND correct declines
            rows.append((composite, hit_rate, mrr, decline_rate, distance, min_rank, k))

    settings.semantic_max_distance, settings.lexical_min_rank = saved

    rows.sort(key=lambda r: (r[0], r[2]), reverse=True)
    print(f"positives={len(positives)}  negatives={len(negatives)}  combos={len(rows)}\n")
    print(f"{'score':>6} {'hit@k':>6} {'MRR':>6} {'declin':>7} {'dist':>5} {'minrank':>8} {'k':>3}")
    for composite, hit_rate, mrr, decline_rate, distance, min_rank, k in rows[:15]:
        print(f"{composite:6.3f} {hit_rate:6.3f} {mrr:6.3f} {decline_rate:7.3f} {distance:5.2f} {min_rank:8.2f} {k:3d}")

    best = rows[0]
    print(
        "\nBEST -> semantic_max_distance=%.2f  lexical_min_rank=%.2f  rag_top_k=%d"
        "  (hit@k=%.3f  MRR=%.3f  decline=%.3f)"
        % (best[4], best[5], best[6], best[1], best[2], best[3])
    )


def main() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(evaluate())


if __name__ == "__main__":
    main()
