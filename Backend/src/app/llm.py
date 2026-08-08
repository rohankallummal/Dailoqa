"""Chat model factory for the ticket agent (Anthropic Claude)."""

from langchain.chat_models import init_chat_model

from app.config import get_settings

_MODEL_PROVIDER = "anthropic"
_MODELS = {
    "agent": "claude-sonnet-5",
    "titler": "claude-haiku-4-5",
}


def get_chat_model(role: str):
    """Return a configured chat model for the given role.

    role must be one of "agent" or "titler". The provider is fixed to Anthropic;
    the model is selected per role and only the API key is configurable via
    LLM_KEY. No sampling parameters are set: claude-sonnet-5 rejects a
    non-default temperature, and schema-constrained structured output keeps
    classification stable without one.
    """
    if role not in _MODELS:
        raise ValueError(f"unknown role: {role}")
    settings = get_settings()
    kwargs = {"model_provider": _MODEL_PROVIDER}
    if settings.llm_key:
        kwargs["api_key"] = settings.llm_key
    return init_chat_model(_MODELS[role], **kwargs)
