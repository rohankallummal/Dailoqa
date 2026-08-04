"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings for the backend."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    service_jwt_secret: str

    llm_key: str | None = None

    # Anthropic is the team default; a local checkout can point at another vendor
    # (e.g. google_genai) without code changes. Per-role overrides are optional and
    # fall back to the provider's defaults in llm.py.
    llm_provider: str = "anthropic"
    llm_model_classifier: str | None = None
    llm_model_agent: str | None = None
    llm_model_titler: str | None = None

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
    docs_path: str = "docs"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    rag_top_k: int = 5
    rag_candidates: int = 20
    rrf_k: int = 60
    semantic_max_distance: float = 0.40
    lexical_min_rank: float = 0.05


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
