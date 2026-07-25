"""Chat model factory for the ticket agent (Anthropic Claude)."""

from langchain.chat_models import init_chat_model

from app.config import get_settings

_MODEL_PROVIDER = "anthropic"
_MODEL = "claude-sonnet-5"
_ROLES = ("classifier", "agent")


def get_chat_model(role: str):
    """Return a configured chat model for the given role.

    role must be "classifier" or "agent". The provider and model are fixed; only the
    API key is configurable via LLM_KEY. No sampling parameters are set: claude-sonnet-5
    rejects a non-default temperature, and schema-constrained structured output keeps
    classification stable without one.
    """
    if role not in _ROLES:
        raise ValueError(f"unknown role: {role}")
    settings = get_settings()
    kwargs = {"model_provider": _MODEL_PROVIDER}
    if settings.llm_key:
        kwargs["api_key"] = settings.llm_key
    return init_chat_model(_MODEL, **kwargs)
