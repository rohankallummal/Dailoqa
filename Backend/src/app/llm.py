"""Chat model factory for the agent.

The project runs on the Dailoqa LiteLLM gateway, which fronts Azure GPT-4o-mini and speaks
the OpenAI-compatible API. The provider stays configurable so a checkout can point
elsewhere without code edits — set ``LLM_PROVIDER`` and, for OpenAI-compatible gateways,
``LLM_BASE_URL``. Nothing that builds an agent needs to know which vendor is in play.
"""

from langchain.chat_models import init_chat_model

from app.config import get_settings

ROLES = ("classifier", "agent", "titler")

# Sensible defaults per provider, so switching vendor is one setting rather than three.
_MODELS: dict[str, dict[str, str]] = {
    # The gateway exposes one deployed model, reused for every role.
    "litellm": {
        "classifier": "azure-gpt-4o-mini",
        "agent": "azure-gpt-4o-mini",
        "titler": "azure-gpt-4o-mini",
    },
    "anthropic": {
        "classifier": "claude-sonnet-5",
        "agent": "claude-sonnet-5",
        "titler": "claude-haiku-4-5",
    },
}

# Providers disagree on the name of the API-key argument, so LLM_KEY is mapped rather
# than passed through blindly.
_KEY_KWARG: dict[str, str] = {
    "litellm": "api_key",
    "anthropic": "api_key",
}

# init_chat_model dispatches on this string to pick the integration package. A LiteLLM
# gateway speaks the OpenAI-compatible API, so it rides langchain-openai's ChatOpenAI —
# "litellm" is only our config-facing label; LLM_BASE_URL is what actually points it at
# the gateway instead of api.openai.com.
_INIT_PROVIDER: dict[str, str] = {
    "litellm": "openai",
}

# Providers that reach an OpenAI-compatible endpoint rather than a vendor's own API, and
# are therefore meaningless without a base URL.
_REQUIRES_BASE_URL = frozenset({"litellm"})


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

    role must be one of ROLES. No sampling parameters are set: schema-constrained
    structured output keeps behaviour stable without one.
    """
    if role not in ROLES:
        raise ValueError(f"unknown role: {role}")
    settings = get_settings()
    provider = settings.llm_provider

    if provider in _REQUIRES_BASE_URL and not settings.llm_base_url:
        # Without this the OpenAI client silently falls back to api.openai.com and fails
        # with a confusing auth error rather than naming the missing setting.
        raise ValueError(f"LLM_PROVIDER='{provider}' requires LLM_BASE_URL to be set")
    if not settings.llm_key:
        # The underlying clients raise for their own env var (OPENAI_API_KEY etc.), which
        # is not the name anyone configures here.
        raise ValueError(f"LLM_KEY is not set; LLM_PROVIDER='{provider}' needs an API key")

    kwargs = {
        "model_provider": _INIT_PROVIDER.get(provider, provider),
        _KEY_KWARG.get(provider, "api_key"): settings.llm_key,
    }
    if settings.llm_base_url:
        kwargs["base_url"] = settings.llm_base_url
    return init_chat_model(_model_for(provider, role), **kwargs)
