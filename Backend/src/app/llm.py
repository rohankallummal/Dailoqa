"""Chat model factory for the ticket agent (LiteLLM gateway)."""

import httpx
from langchain.chat_models import init_chat_model
from openai import APIConnectionError

from app.config import get_settings

_MODEL_PROVIDER = "openai"
_MAX_RETRIES = 2
_TIMEOUT = httpx.Timeout(connect=5.0, read=120.0, write=30.0, pool=5.0)


def get_chat_model():
    """Return the chat model every LLM call in this backend runs through.

    The gateway speaks the OpenAI wire protocol, so the provider is fixed while the
    deployment, endpoint, and key are configurable via LLM_MODEL, LLM_BASE_URL, and
    LLM_KEY. No sampling parameters are set: schema-constrained structured output
    keeps classification stable without one.

    The timeout is split rather than flat because the two limits guard different
    things. The gateway resolves to a private address behind the VPN, so with the
    tunnel down the connection is blackholed rather than refused: without an explicit
    connect timeout the client waits out the operating system's TCP timeout and each
    call takes minutes to fail. A generous read timeout is still needed after that,
    because a legitimate agent turn takes far longer to answer than to connect.
    """
    settings = get_settings()
    kwargs = {
        "model_provider": _MODEL_PROVIDER,
        "base_url": settings.llm_base_url,
        "timeout": _TIMEOUT,
        "max_retries": _MAX_RETRIES,
    }
    if settings.llm_key:
        kwargs["api_key"] = settings.llm_key
    return init_chat_model(settings.llm_model, **kwargs)


def is_unavailable(error: BaseException) -> bool:
    """Report whether a failure means the gateway could not be reached at all.

    Covers a blackholed, refused, or timed-out request, all of which mean the model
    never answered -- as opposed to a rejected request, which is a bug in the call.
    Callers use this to tell the user to retry instead of blaming the request.
    """
    return isinstance(error, APIConnectionError)
