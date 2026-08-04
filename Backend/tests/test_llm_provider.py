"""Provider selection and key mapping.

The model is never constructed for real here: these assert which model id and which
API-key argument ``get_chat_model`` resolves to, so the suite needs no key and makes no
paid call.
"""

import pytest

import app.llm as llm
from app.config import get_settings


@pytest.fixture
def captured(monkeypatch):
    """Intercept init_chat_model and record what it was asked to build."""
    calls: dict = {}

    def fake_init_chat_model(model, **kwargs):
        calls.clear()
        calls.update({"model": model, **kwargs})
        return "CHAT_MODEL"

    monkeypatch.setattr(llm, "init_chat_model", fake_init_chat_model)
    return calls


@pytest.fixture
def settings(monkeypatch):
    """Settings restored after each test; get_settings is cached and process-wide."""
    current = get_settings()
    monkeypatch.setattr(current, "llm_provider", current.llm_provider, raising=False)
    monkeypatch.setattr(current, "llm_key", "test-key", raising=False)
    return current


def test_anthropic_is_the_default_for_the_team(captured, settings):
    settings.llm_provider = "anthropic"
    llm.get_chat_model("agent")
    assert captured["model"] == "claude-sonnet-5"
    assert captured["model_provider"] == "anthropic"
    assert captured["api_key"] == "test-key"


def test_titler_uses_the_cheaper_model(captured, settings):
    settings.llm_provider = "anthropic"
    llm.get_chat_model("titler")
    assert captured["model"] == "claude-haiku-4-5"


def test_google_maps_the_key_to_its_own_argument(captured, settings):
    # The providers disagree on the kwarg name, which is the whole reason LLM_KEY is
    # mapped rather than forwarded.
    settings.llm_provider = "google_genai"
    llm.get_chat_model("agent")
    assert captured["model"] == "gemini-2.5-flash"
    assert captured["google_api_key"] == "test-key"
    assert "api_key" not in captured


def test_an_explicit_model_overrides_the_provider_default(captured, settings, monkeypatch):
    settings.llm_provider = "google_genai"
    monkeypatch.setattr(settings, "llm_model_agent", "gemini-2.0-flash", raising=False)
    llm.get_chat_model("agent")
    assert captured["model"] == "gemini-2.0-flash"


def test_an_unknown_role_is_rejected(settings):
    with pytest.raises(ValueError, match="unknown role"):
        llm.get_chat_model("nope")


def test_an_unknown_provider_names_the_setting_to_fix(captured, settings):
    settings.llm_provider = "some-vendor"
    with pytest.raises(ValueError, match="LLM_MODEL_AGENT"):
        llm.get_chat_model("agent")
