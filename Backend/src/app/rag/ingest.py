"""Ingest the documentation corpus into ``app.doc_chunks``.

Run from the Backend directory:

    python -m app.rag.ingest

Walks ``DOCS_PATH`` for Markdown/MDX, strips frontmatter and MDX/JSX, splits by heading
then by token count (so no chunk exceeds bge's 512-token limit), re-prepends the heading
trail to each sub-chunk for context, embeds the passages locally, and replaces each file's
chunks transactionally. A pre-flight sweep removes chunks whose source file no longer exists,
so the table never accumulates ghosts. Idempotent: safe to re-run after doc edits.
"""

import asyncio
import re
import sys
from pathlib import Path

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from app.config import get_settings
from app.db.base import async_session
from app.rag.embeddings import aembed_documents, get_tokenizer
from app.rag.store import ChunkRow, context_prefix, delete_missing_sources, upsert_chunks

# Leave headroom under bge's 512-token limit for the prepended "<title> > <heading>" line.
_TOKENS_PER_CHUNK = 400
_CHUNK_OVERLAP = 40

_HEADERS_TO_SPLIT_ON = [("#", "h1"), ("##", "h2"), ("###", "h3")]

_FRONTMATTER_RE = re.compile(r"^﻿?---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_TITLE_RE = re.compile(r"^title:\s*(.+?)\s*$", re.MULTILINE)
_IMPORT_EXPORT_RE = re.compile(r"^(import|export)\s.+$", re.MULTILINE)
_MDX_COMMENT_RE = re.compile(r"\{/\*.*?\*/\}", re.DOTALL)

# Only JSX *components* — Mintlify's are capitalised (<CodeGroup>, <Tip>, <Accordion>) —
# plus the handful of lowercase HTML tags these pages actually use. The old blanket
# `<[^>]+>` also ate CommonMark autolinks such as <https://x.com> and <a@b.com>.
_JSX_TAG_RE = re.compile(r"</?[A-Z][\w.]*(?:\s[^>]*)?/?>|</?(?:br|hr|img|a|p|div|span)(?:\s[^>]*)?/?>")

# LangChain's own language switches. A :::python/:::js pair states the same concept twice,
# so the unwanted language is dropped whole rather than merely unmarked.
_DIRECTIVE_BLOCK_RE = re.compile(r"^:::(\w+)[ \t]*\n(.*?)^:::[ \t]*$\n?", re.DOTALL | re.MULTILINE)
_STRAY_DIRECTIVE_RE = re.compile(r"^:::.*$", re.MULTILINE)

# `[Text](/oss/langchain/agents)` otherwise pushes the URL's path segments into the
# english tsvector as though they were prose. Images are dropped outright.
_MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")

_BLANK_LINES_RE = re.compile(r"\n{3,}")

# Fenced and inline code are masked before any substitution runs and restored after, so a
# rule written for prose cannot reach into a code sample. Without this, `<[^>]+>` silently
# turned `std::vector<int>` into `std::vector` and `#include <vector>` into `#include`.
# The trailing newline is deliberately left in place: swallowing it would put the next
# line (often a closing ":::") at the end of the mask instead of at a line start, and the
# line-anchored rules would then miss it.
_FENCE_RE = re.compile(r"^([ \t]*)(`{3,}|~{3,})[^\n]*\n.*?^\1?\2[ \t]*$", re.DOTALL | re.MULTILINE)
# Deliberately NOT re.DOTALL: an inline code span must stay on one line. With DOTALL a single
# unbalanced backtick -- `](https://...) inside a link, say -- matches across paragraphs and
# swallows whatever lies between it and the next backtick, including already-masked fences. Those
# then never get restored, so the chunk keeps a raw \x00MASK7\x00 and loses the code outright.
_INLINE_CODE_RE = re.compile(r"(?<!`)(`+)(?!`)([^\n]+?)(?<!`)\1(?!`)")
_MASK = "\x00MASK{}\x00"
_MASK_RE = re.compile(r"\x00MASK(\d+)\x00")
_MAX_UNMASK_PASSES = 10


def _docs_dir() -> Path:
    """Resolve the docs directory (``DOCS_PATH``), relative to the Backend root if not absolute."""
    configured = Path(get_settings().docs_path)
    if configured.is_absolute():
        return configured
    backend_root = Path(__file__).resolve().parents[3]  # .../Backend
    return backend_root / configured


def _parse_frontmatter(text: str) -> tuple[str, str | None]:
    """Strip a leading YAML frontmatter block; return (body, title-or-None)."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return text, None
    title_match = _TITLE_RE.search(match.group(1))
    title = title_match.group(1).strip().strip("\"'") if title_match else None
    return text[match.end():], title


def _mask_code(text: str) -> tuple[str, list[str]]:
    """Replace fenced and inline code with placeholders; return the text and the originals.

    Every prose rule runs against the masked text, so no substitution can reach inside a
    code sample. Fences are masked before inline code, or a lone backtick inside a fence
    would pair with another and corrupt the block.
    """
    saved: list[str] = []

    def keep(match: re.Match) -> str:
        saved.append(match.group(0))
        return _MASK.format(len(saved) - 1)

    return _INLINE_CODE_RE.sub(keep, _FENCE_RE.sub(keep, text)), saved


def _unmask_code(text: str, saved: list[str]) -> str:
    """Restore masked code verbatim.

    Loops rather than substituting once: ``re.sub`` does not rescan what it inserts, so a saved
    span containing a placeholder would leave a raw ``\\x00MASK7\\x00`` in an embedded chunk.
    Worth being defensive about even now that the inline-code rule cannot produce that nesting,
    because the failure is silent and lands in the index rather than in a traceback.
    """
    for _ in range(_MAX_UNMASK_PASSES):
        text, changed = _MASK_RE.subn(lambda m: saved[int(m.group(1))], text)
        if not changed:
            return text
    raise RuntimeError("unmasking did not converge; masked code is nested more deeply than expected")


def _select_language(text: str, keep: str) -> str:
    """Unwrap ``:::<keep>`` blocks and drop every other language block entirely.

    LangChain documents most concepts twice, once per language. Keeping both would spend a
    quarter of the corpus restating the same idea and let a Python question be answered in
    TypeScript, so only the configured language survives.
    """

    def resolve(match: re.Match) -> str:
        language, body = match.group(1), match.group(2)
        return body if language == keep else ""

    return _DIRECTIVE_BLOCK_RE.sub(resolve, text)


def _flatten_mdx(text: str) -> str:
    """Reduce Mintlify MDX to plain Markdown, leaving code samples untouched.

    Masking comes first and unmasking last; everything between operates only on prose.
    """
    text, saved = _mask_code(text)
    text = _select_language(text, get_settings().docs_language)
    text = _IMPORT_EXPORT_RE.sub("", text)
    text = _MDX_COMMENT_RE.sub("", text)
    text = _JSX_TAG_RE.sub("", text)
    text = _STRAY_DIRECTIVE_RE.sub("", text)  # unpaired markers the block rule could not match
    text = _MD_IMAGE_RE.sub("", text)
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _BLANK_LINES_RE.sub("\n\n", text).strip()
    return _unmask_code(text, saved)


def _heading_trail(metadata: dict) -> str | None:
    """Join the present header levels into a single trail, e.g. 'Core capabilities > Skills'."""
    parts = [metadata[key] for key in ("h1", "h2", "h3") if metadata.get(key)]
    return " > ".join(parts) if parts else None


def _chunk_file(path: Path, docs_dir: Path) -> list[dict]:
    """Split one doc into ordered chunk dicts (source_path, title, heading, text)."""
    raw = path.read_text(encoding="utf-8")
    body, title = _parse_frontmatter(raw)
    title = title or path.stem
    cleaned = _flatten_mdx(body)

    header_splitter = MarkdownHeaderTextSplitter(_HEADERS_TO_SPLIT_ON, strip_headers=True)
    # Measure length with the model tokenizer but split on the ORIGINAL text, so the
    # stored/embedded content is never round-tripped (and corrupted) through WordPiece.
    token_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        get_tokenizer(),
        chunk_size=_TOKENS_PER_CHUNK,
        chunk_overlap=_CHUNK_OVERLAP,
    )

    source_path = path.relative_to(docs_dir).as_posix()
    chunks: list[dict] = []
    for section in header_splitter.split_text(cleaned):
        heading = _heading_trail(section.metadata)
        section_text = section.page_content.strip()
        if not section_text:
            continue
        for piece in token_splitter.split_text(section_text):
            piece = piece.strip()
            if piece:
                chunks.append({"source_path": source_path, "title": title, "heading": heading, "text": piece})
    return chunks


def _context_prefixed(source_path: str, title: str, heading: str | None, text: str) -> str:
    """Prepend the context line so a mid-section chunk keeps its context when embedded.

    The line itself is defined by ``store.context_prefix`` — the same function retrieval
    strips with, so the writer and the stripper cannot drift apart.
    """
    return f"{context_prefix(source_path, title, heading)}\n\n{text}"


async def ingest() -> int:
    """Ingest every Markdown/MDX doc under ``DOCS_PATH``; return total chunks written."""
    docs_dir = _docs_dir()
    if not docs_dir.is_dir():
        raise SystemExit(f"DOCS_PATH does not exist: {docs_dir}")

    files = sorted(p for p in docs_dir.rglob("*") if p.suffix.lower() in (".md", ".mdx"))
    if not files:
        raise SystemExit(f"No .md/.mdx files found under {docs_dir}")

    print(f"Ingesting {len(files)} file(s) from {docs_dir}")
    valid_paths = [f.relative_to(docs_dir).as_posix() for f in files]

    total = 0
    async with async_session() as session:
        removed = await delete_missing_sources(session, valid_paths)
        if removed:
            print(f"  stale sweep: removed {removed} orphan chunk(s)")

        for path in files:
            chunks = _chunk_file(path, docs_dir)
            if not chunks:
                print(f"  {path.name}: no content, skipped")
                continue
            texts = [
                _context_prefixed(c["source_path"], c["title"], c["heading"], c["text"])
                for c in chunks
            ]
            embeddings = await aembed_documents(texts)
            rows = [
                ChunkRow(
                    source_path=chunk["source_path"],
                    title=chunk["title"],
                    heading=chunk["heading"],
                    chunk_index=index,
                    content=text,
                    embedding=embedding,
                )
                for index, (chunk, text, embedding) in enumerate(zip(chunks, texts, embeddings))
            ]
            await upsert_chunks(session, rows[0].source_path, rows)
            total += len(rows)
            print(f"  {path.name}: {len(rows)} chunk(s)")

        await session.commit()

    print(f"Done. {total} chunk(s) across {len(files)} file(s).")
    return total


def main() -> None:
    """CLI entry point. Pins a SelectorEventLoop on Windows for psycopg async."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(ingest())


if __name__ == "__main__":
    main()
