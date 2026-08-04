"""Assembly of the DailoQA agent from its model, tools, and middleware."""

import json

from langchain.agents import create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    InterruptOnConfig,
    ModelCallLimitMiddleware,
    SummarizationMiddleware,
    ToolRetryMiddleware,
)

from app.agent.context import TurnContext
from app.agent.middleware.grounding import require_documentation
from app.agent.middleware.skills import skills_middleware
from app.agent.middleware.streaming import StreamPublisherMiddleware
from app.agent.tools import active_tools
from app.config import get_settings
from app.llm import get_chat_model

_MAX_MODEL_CALLS = 12


def _describe_write(tool_call, state, runtime) -> str:
    """Render a pending ticket write so the chat can preview exactly what will be filed."""
    return json.dumps({"action": tool_call["name"], "ticket": tool_call["args"]}, indent=2)


def _write_gate() -> HumanInTheLoopMiddleware:
    """Require explicit approval before anything reaches Jira.

    This is a structural gate rather than a prompt instruction: the tool call is
    suspended by the graph, so no wording the model produces and no reply the user
    types can cause a filing without an approve decision.
    """
    approval = InterruptOnConfig(
        allowed_decisions=["approve", "reject"],
        description=_describe_write,
    )
    return HumanInTheLoopMiddleware(
        interrupt_on={"create_ticket": approval, "link_to_existing": approval}
    )


def build_agent(checkpointer, publish):
    """Build the compiled agent.

    Args:
        checkpointer: An AsyncPostgresSaver, keyed at run time by conversation id.
        publish: Coroutine taking one SSE event dict, used for tool status lines.
    """
    middleware = [
        skills_middleware,
        _write_gate(),
        SummarizationMiddleware(model=get_chat_model("titler")),
        ToolRetryMiddleware(max_retries=2),
        ModelCallLimitMiddleware(thread_limit=_MAX_MODEL_CALLS),
        StreamPublisherMiddleware(publish),
    ]
    if get_settings().rag_enabled:
        # Gated with the documentation tools it polices: without them, its correction
        # would tell the model to call a tool that is not bound.
        middleware.insert(1, require_documentation)

    return create_agent(
        model=get_chat_model("agent"),
        tools=active_tools(),
        context_schema=TurnContext,
        checkpointer=checkpointer,
        middleware=middleware,
    )
