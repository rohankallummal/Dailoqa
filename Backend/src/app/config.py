"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings for the backend."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    service_jwt_secret: str

    llm_key: str | None = None

    jira_site_url: str
    jira_email: str | None = None
    jira_api_token: str | None = None
    jira_project_key: str = "KAN"
    jira_issue_type_bug: str = "Bug"
    jira_issue_type_feature: str = "Request"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
