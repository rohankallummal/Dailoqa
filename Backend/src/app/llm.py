"""Provider-agnostic chat model factory driven by env configuration."""

from langchain.chat_models import init_chat_model

from app.config import get_settings

_ROLES = ("classifier", "agent")


def get_chat_model(role: str):
    """Return a configured chat model for the given role.

    role must be "classifier" or "agent". The classifier runs at temperature 0
    for stable structured output; the agent uses the configured temperature.
    Model selection falls back to LLM_MODEL when a per-role model is unset.
    """
    if role not in _ROLES:
        raise ValueError(f"unknown role: {role}")
    settings = get_settings()
    per_role = settings.llm_agent_model if role == "agent" else settings.llm_classifier_model
    model = per_role or settings.llm_model
    temperature = 0 if role == "classifier" else settings.llm_temperature
    kwargs = {
        "model_provider": settings.llm_provider,
        "temperature": temperature,
    }
    if settings.llm_api_key:
        kwargs["api_key"] = settings.llm_api_key
    if settings.llm_base_url:
        kwargs["base_url"] = settings.llm_base_url
    return init_chat_model(model, **kwargs)
