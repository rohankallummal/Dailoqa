"""Assembly of the DailoQA agent from its model, tools, and middleware."""

from langchain.agents import create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    InterruptOnConfig,
    ModelCallLimitMiddleware,
    SummarizationMiddleware,
    ToolRetryMiddleware,
)

from app.agent.context import TurnContext
from app.agent.middleware.skills import skills_middleware
from app.agent.middleware.streaming import StreamPublisherMiddleware
from app.agent.tools import TOOLS
from app.llm import get_chat_model

_MAX_MODEL_CALLS = 24


def _write_gate() -> HumanInTheLoopMiddleware:
    """Require explicit approval before anything reaches Jira.

    This is a structural gate rather than a prompt instruction: the tool call is
    suspended by the graph, so no wording the model produces and no reply the user
    types can cause a filing without an approve decision.

    No ``description`` is configured. The line the user actually reads is built by
    ``runner._write_summary`` from the drafted arguments, and nothing consumes the one on
    the interrupt itself, so supplying it only produced a second rendering that no reader
    ever saw.
    """
    approval = InterruptOnConfig(allowed_decisions=["approve", "reject"])
    return HumanInTheLoopMiddleware(
        interrupt_on={
            "create_bug": approval,
            "create_feature": approval,
            "link_to_existing": approval,
        }
    )


def build_agent(checkpointer, publish):
    """Build the compiled agent.

    Args:
        checkpointer: An AsyncPostgresSaver, keyed at run time by conversation id.
        publish: Coroutine taking one SSE event dict, used for tool status lines.
    """
    return create_agent(
        model=get_chat_model(),
        tools=TOOLS,
        context_schema=TurnContext,
        checkpointer=checkpointer,
        middleware=[
            skills_middleware,
            _write_gate(),
            SummarizationMiddleware(model=get_chat_model()),
            ToolRetryMiddleware(max_retries=2),
            ModelCallLimitMiddleware(thread_limit=_MAX_MODEL_CALLS),
            StreamPublisherMiddleware(publish),
        ],
    )
