"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings for the backend."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    service_jwt_secret: str

    llm_key: str | None = None

    # The Dailoqa LiteLLM gateway (Azure GPT-4o-mini) is the default; a checkout can
    # point at another vendor without code changes. Per-role overrides are optional and
    # fall back to the provider's defaults in llm.py.
    llm_provider: str = "litellm"
    llm_model_classifier: str | None = None
    llm_model_agent: str | None = None
    llm_model_titler: str | None = None
    # Required for OpenAI-compatible gateways (llm_provider="litellm"); unused otherwise.
    llm_base_url: str | None = None

    jira_site_url: str
    jira_email: str | None = None
    jira_api_token: str | None = None
    jira_project_key: str = "KAN"
    jira_webhook_secret: str | None = None
    jira_issue_type_bug: str = "Bug"
    jira_issue_type_feature: str = "Request"

    evidence_root: str = "/evidence"

    # Documentation Q&A corpus and retrieval.
    # The gates were calibrated against eval/golden_set.json (hit@k = 1.0, all
    # absent-topic negatives decline); re-run `python -m app.rag.evaluate` after any
    # change to the corpus to re-tune them.
    rag_enabled: bool = True
    # Only the formatted tree. Its sibling docs-corpus/raw/ holds the upstream .mdx and the
    # snippet library, and must stay outside this path -- ingestion globs recursively, so a
    # raw/ underneath it would index every page a second time plus ~154 contextless snippet
    # fragments as if they were pages.
    docs_path: str = "docs-corpus/formatted"
    # Which ":::<lang>" arm of the upstream docs to keep. LangChain writes most concepts
    # twice (python and js); indexing both wastes a quarter of the corpus and lets a
    # Python question be answered in TypeScript.
    docs_language: str = "python"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    rag_top_k: int = 5
    rag_candidates: int = 20
    rrf_k: int = 60
    # Tightened from 0.40 when the corpus went from 44 chunks to 613. An absolute cosine gate
    # weakens as a corpus grows -- more content means a better chance something sits within the
    # threshold of an off-topic query -- and that is exactly what happened: at 0.40 an off-topic
    # question ("how do I configure SSO for Dailoqa") pulled back four LangChain chunks, taking
    # the decline rate to 0.857. At 0.35 decline returns to 1.000 with hit@k unchanged at 1.000,
    # so this costs no recall. Re-run `python -m app.rag.evaluate` after any corpus change.
    semantic_max_distance: float = 0.35
    lexical_min_rank: float = 0.05


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
