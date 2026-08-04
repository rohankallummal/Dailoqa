"""Chat model factory for the agent.

The provider is configurable so the same code can run against a different vendor without
edits — a local checkout can point at whatever key its developer holds while the team
default stays Anthropic. Only ``LLM_PROVIDER`` and the optional per-role model overrides
change; nothing that builds an agent needs to know which vendor is in play.
"""

from langchain.chat_models import init_chat_model

from app.config import get_settings

ROLES = ("classifier", "agent", "titler")

# Sensible defaults per provider, so switching vendor is one setting rather than three.
_MODELS: dict[str, dict[str, str]] = {
    "anthropic": {
        "classifier": "claude-sonnet-5",
        "agent": "claude-sonnet-5",
        "titler": "claude-haiku-4-5",
    },
    "google_genai": {
        "classifier": "gemini-2.5-flash",
        "agent": "gemini-2.5-flash",
        "titler": "gemini-2.5-flash",
    },
}

# Providers disagree on the name of the API-key argument, so LLM_KEY is mapped rather
# than passed through blindly.
_KEY_KWARG: dict[str, str] = {
    "anthropic": "api_key",
    "google_genai": "google_api_key",
}


def _model_for(provider: str, role: str) -> str:
    """Resolve a role's model id: an explicit override wins, else the provider default."""
    override = getattr(get_settings(), f"llm_model_{role}", None)
    if override:
        return override
    try:
        return _MODELS[provider][role]
    except KeyError:
        raise ValueError(
            f"no default model for role '{role}' on provider '{provider}'; "
            f"set LLM_MODEL_{role.upper()} to choose one"
        ) from None


def get_chat_model(role: str):
    """Return a configured chat model for the given role.

    role must be one of ROLES. No sampling parameters are set: claude-sonnet-5 rejects a
    non-default temperature, and schema-constrained structured output keeps behaviour
    stable without one.
    """
    if role not in ROLES:
        raise ValueError(f"unknown role: {role}")
    settings = get_settings()
    provider = settings.llm_provider
    kwargs = {"model_provider": provider}
    if settings.llm_key:
        kwargs[_KEY_KWARG.get(provider, "api_key")] = settings.llm_key
    return init_chat_model(_model_for(provider, role), **kwargs)
