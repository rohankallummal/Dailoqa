"""Local sentence-transformers embeddings for the RAG corpus.

Uses ``BAAI/bge-small-en-v1.5`` (384-dim), a free model that runs in-process with no
API key. bge is **asymmetric**: queries must carry an instruction prefix, passages must
not. This version of ``langchain-huggingface`` ships only ``HuggingFaceEmbeddings`` (no
``query_instruction`` parameter), so we prepend the prefix ourselves in the query path
only — ``embed_documents`` (ingestion) stays unprefixed.

The model is synchronous and CPU-bound, so the async helpers offload the encode to a
worker thread to keep the event loop free. Retrieval and ingestion call the ``a*`` variants.
"""

import asyncio
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from app.config import get_settings

# bge query-side instruction. Passages are embedded without it.
_QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


@lru_cache(maxsize=1)
def get_embedder() -> HuggingFaceEmbeddings:
    """Return the process-wide embedder, loading the model on first use."""
    return HuggingFaceEmbeddings(
        model_name=get_settings().embedding_model,
        encode_kwargs={"normalize_embeddings": True},
    )


@lru_cache(maxsize=1)
def get_tokenizer():
    """Return the model's tokenizer, for measuring chunk token length during ingestion.

    Used to bound chunks under the model's 512-token limit *without* decoding text
    (which an uncased WordPiece tokenizer would corrupt).
    """
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(get_settings().embedding_model)


def embed_query_sync(text: str) -> list[float]:
    """Embed a search query, prepending the bge query instruction."""
    return get_embedder().embed_query(_QUERY_INSTRUCTION + text)


def embed_documents_sync(texts: list[str]) -> list[list[float]]:
    """Embed passages (no instruction prefix)."""
    return get_embedder().embed_documents(texts)


async def aembed_query(text: str) -> list[float]:
    """Async wrapper around :func:`embed_query_sync` (offloaded to a worker thread)."""
    return await asyncio.to_thread(embed_query_sync, text)


async def aembed_documents(texts: list[str]) -> list[list[float]]:
    """Async wrapper around :func:`embed_documents_sync` (offloaded to a worker thread)."""
    return await asyncio.to_thread(embed_documents_sync, texts)
