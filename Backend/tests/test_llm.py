import pytest

import app.llm as llm_module
from app.config import get_settings


@pytest.fixture(autouse=True)
def _llm_env(base_env, monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("LLM_CLASSIFIER_MODEL", "cheap-model")
    monkeypatch.setenv("LLM_AGENT_MODEL", "smart-model")
    monkeypatch.setenv("LLM_BASE_URL", "https://api.example.com/v1")
    monkeypatch.setenv("LLM_API_KEY", "k")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_agent_role_uses_agent_model(monkeypatch):
    captured = {}

    def fake_init(model, **kwargs):
        captured["model"] = model
        captured.update(kwargs)
        return "MODEL"

    monkeypatch.setattr(llm_module, "init_chat_model", fake_init)
    result = llm_module.get_chat_model("agent")
    assert result == "MODEL"
    assert captured["model"] == "smart-model"
    assert captured["model_provider"] == "openai"
    assert captured["base_url"] == "https://api.example.com/v1"


def test_classifier_role_forces_zero_temperature(monkeypatch):
    captured = {}

    def fake_init(model, **kwargs):
        captured["model"] = model
        captured.update(kwargs)
        return "MODEL"

    monkeypatch.setattr(llm_module, "init_chat_model", fake_init)
    llm_module.get_chat_model("classifier")
    assert captured["model"] == "cheap-model"
    assert captured["temperature"] == 0


def test_unknown_role_rejected(monkeypatch):
    monkeypatch.setattr(llm_module, "init_chat_model", lambda *a, **k: "MODEL")
    with pytest.raises(ValueError):
        llm_module.get_chat_model("nonsense")


def test_agent_role_omits_unset_api_key_and_base_url(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    get_settings.cache_clear()
    captured = {}

    def fake_init(model, **kwargs):
        captured["model"] = model
        captured.update(kwargs)
        return "MODEL"

    monkeypatch.setattr(llm_module, "init_chat_model", fake_init)
    llm_module.get_chat_model("agent")
    assert "api_key" not in captured
    assert "base_url" not in captured


def test_agent_role_falls_back_to_base_model_when_unset(monkeypatch):
    monkeypatch.delenv("LLM_AGENT_MODEL", raising=False)
    get_settings.cache_clear()
    captured = {}

    def fake_init(model, **kwargs):
        captured["model"] = model
        captured.update(kwargs)
        return "MODEL"

    monkeypatch.setattr(llm_module, "init_chat_model", fake_init)
    llm_module.get_chat_model("agent")
    assert captured["model"] == "gpt-4o-mini"


def test_agent_role_forwards_configured_temperature(monkeypatch):
    captured = {}

    def fake_init(model, **kwargs):
        captured["model"] = model
        captured.update(kwargs)
        return "MODEL"

    monkeypatch.setattr(llm_module, "init_chat_model", fake_init)
    llm_module.get_chat_model("agent")
    assert captured["temperature"] == 0.2
