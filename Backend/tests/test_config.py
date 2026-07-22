import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_load_from_env(base_env):
    settings = Settings()
    assert settings.database_url.endswith("/db")
    assert settings.service_jwt_secret == "test-secret"
    assert settings.llm_provider == "openai"
    assert settings.jira_issue_type_bug == "Bug"
    assert settings.jira_issue_type_feature == "Request"


def test_settings_missing_required_raises(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SERVICE_JWT_SECRET", raising=False)
    with pytest.raises(ValidationError):
        Settings()
