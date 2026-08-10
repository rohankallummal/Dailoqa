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


_GATEWAY = "https://gateway.example.com/apillmgov"


@pytest.fixture
def settings(monkeypatch):
    """Settings restored after each test; get_settings is cached and process-wide."""
    current = get_settings()
    monkeypatch.setattr(current, "llm_provider", current.llm_provider, raising=False)
    monkeypatch.setattr(current, "llm_key", "test-key", raising=False)
    monkeypatch.setattr(current, "llm_base_url", _GATEWAY, raising=False)
    return current


def test_the_gateway_is_the_default_provider(captured, settings):
    # The default must reach the gateway through langchain-openai: "litellm" is only our
    # config-facing label, and the OpenAI integration is what speaks its API.
    llm.get_chat_model("agent")
    assert captured["model"] == "azure-gpt-4o-mini"
    assert captured["model_provider"] == "openai"
    assert captured["api_key"] == "test-key"
    assert captured["base_url"] == _GATEWAY


def test_every_role_shares_the_one_deployed_model(captured, settings):
    for role in llm.ROLES:
        llm.get_chat_model(role)
        assert captured["model"] == "azure-gpt-4o-mini"


def test_the_gateway_refuses_to_run_without_a_base_url(settings, monkeypatch):
    # Without base_url the OpenAI client silently falls back to api.openai.com, so the
    # failure must name the missing setting instead of surfacing as an auth error.
    monkeypatch.setattr(settings, "llm_base_url", None, raising=False)
    with pytest.raises(ValueError, match="LLM_BASE_URL"):
        llm.get_chat_model("agent")


def test_a_missing_key_names_the_setting_to_fix(settings, monkeypatch):
    # The OpenAI client's own error tells you to set OPENAI_API_KEY, which is not the
    # variable anyone configures in this project.
    monkeypatch.setattr(settings, "llm_key", None, raising=False)
    with pytest.raises(ValueError, match="LLM_KEY"):
        llm.get_chat_model("agent")


def test_anthropic_remains_available_as_an_alternative(captured, settings, monkeypatch):
    settings.llm_provider = "anthropic"
    monkeypatch.setattr(settings, "llm_base_url", None, raising=False)
    llm.get_chat_model("agent")
    assert captured["model"] == "claude-sonnet-5"
    assert captured["model_provider"] == "anthropic"
    assert "base_url" not in captured


def test_an_explicit_model_overrides_the_provider_default(captured, settings, monkeypatch):
    monkeypatch.setattr(settings, "llm_model_agent", "azure-gpt-4o", raising=False)
    llm.get_chat_model("agent")
    assert captured["model"] == "azure-gpt-4o"


def test_an_unknown_role_is_rejected(settings):
    with pytest.raises(ValueError, match="unknown role"):
        llm.get_chat_model("nope")


def test_an_unknown_provider_names_the_setting_to_fix(captured, settings):
    settings.llm_provider = "some-vendor"
    with pytest.raises(ValueError, match="LLM_MODEL_AGENT"):
        llm.get_chat_model("agent")
