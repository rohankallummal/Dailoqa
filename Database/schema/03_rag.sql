CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE app.doc_chunks (
    id varchar PRIMARY KEY,
    source_path varchar NOT NULL,
    title varchar,
    heading varchar,
    chunk_index integer NOT NULL,
    content text NOT NULL,
    embedding vector(384) NOT NULL,
    content_tsv tsvector GENERATED ALWAYS AS (
        to_tsvector(
            'english',
            coalesce(title, '') || ' ' || coalesce(heading, '') || ' ' || content
        )
    ) STORED,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT uq_doc_chunks_source_path UNIQUE (source_path, chunk_index)
);

-- Semantic arm: approximate nearest-neighbour over the embedding (cosine).
CREATE INDEX ix_doc_chunks_embedding ON app.doc_chunks USING hnsw (embedding vector_cosine_ops);

-- Lexical arm: full-text search over title + heading + content.
CREATE INDEX ix_doc_chunks_content_tsv ON app.doc_chunks USING gin (content_tsv);

-- Ingestion delete-then-insert per source file.
CREATE INDEX ix_doc_chunks_source_path ON app.doc_chunks (source_path);
