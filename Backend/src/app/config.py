"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings for the backend."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    service_jwt_secret: str

    llm_key: str | None = None
    llm_base_url: str = "https://dev4-broccoli-apillmgov.dailoqa.com/apillmgov/v1"
    llm_model: str = "azure-gpt-4o-mini"

    jira_site_url: str
    jira_email: str | None = None
    jira_api_token: str | None = None
    jira_project_key: str = "KAN"
    jira_webhook_secret: str | None = None
    jira_issue_type_bug: str = "Bug"
    jira_issue_type_feature: str = "Request"

    evidence_root: str = "/evidence"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
