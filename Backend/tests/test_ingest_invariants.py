"""Invariants the ingested corpus must hold for retrieval to mean anything."""

from sqlalchemy import func, select

from app.db.base import async_session
from app.db.models import DocChunk
from app.rag.embeddings import get_tokenizer
from tests.conftest import corpus_sources

_MODEL_TOKEN_LIMIT = 512


async def test_every_document_in_the_manifest_is_present():
    # Both directions. A missing page means answers silently lose a topic; an extra one means
    # something is indexed that no citation can map back to a documentation route.
    async with async_session() as session:
        sources = set((await session.execute(select(DocChunk.source_path).distinct())).scalars().all())
    assert sources == corpus_sources()


async def test_no_chunk_is_empty():
    async with async_session() as session:
        empty = (
            await session.execute(
                select(func.count())
                .select_from(DocChunk)
                .where(
                    (DocChunk.content == "")
                    | (DocChunk.content.is_(None))
                    | (DocChunk.embedding.is_(None))
                )
            )
        ).scalar()
    assert empty == 0


async def test_no_chunk_exceeds_the_embedding_model_limit():
    # Over the limit the encoder truncates silently, so the stored vector would describe
    # only part of the text it claims to represent.
    tokenizer = get_tokenizer()
    async with async_session() as session:
        contents = (await session.execute(select(DocChunk.content))).scalars().all()
    assert contents
    longest = max(len(tokenizer.encode(content, add_special_tokens=True)) for content in contents)
    assert longest <= _MODEL_TOKEN_LIMIT, f"a chunk is {longest} tokens"


async def test_chunk_indices_are_contiguous_within_a_section():
    # fetch_section reassembles a section by ordering on chunk_index, which only restores
    # the original prose if a heading's chunks are consecutive.
    async with async_session() as session:
        rows = (
            await session.execute(
                select(DocChunk.source_path, DocChunk.heading, DocChunk.chunk_index).order_by(
                    DocChunk.source_path, DocChunk.chunk_index
                )
            )
        ).all()
    sections: dict[tuple[str, str | None], list[int]] = {}
    for source_path, heading, index in rows:
        sections.setdefault((source_path, heading), []).append(index)
    for key, indices in sections.items():
        assert indices == list(range(indices[0], indices[0] + len(indices))), f"gap in {key}"
