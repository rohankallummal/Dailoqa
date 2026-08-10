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
    docs_path: str = "docs"
    # Which ":::<lang>" arm of the upstream docs to keep. LangChain writes most concepts
    # twice (python and js); indexing both wastes a quarter of the corpus and lets a
    # Python question be answered in TypeScript.
    docs_language: str = "python"
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
