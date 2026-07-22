import pytest


@pytest.fixture
def base_env(monkeypatch):
    """Set the minimum required env vars for constructing Settings."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost:5432/db")
    monkeypatch.setenv("SERVICE_JWT_SECRET", "unit-test-service-jwt-secret-0123456789ab")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("JIRA_SITE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_PROJECT_KEY", "KAN")
