"""Shared test setup.

Pins a SelectorEventLoop on Windows: psycopg's async mode rejects the ProactorEventLoop
that Python installs by default there, and the database-backed tests would fail on that
alone. Also provides the fakes the agent tests drive the graph with, so no test in this
suite needs a live model or an API key.
"""

import asyncio
import sys

import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

from app.agent.context import TurnContext

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class ScriptedModel(FakeMessagesListChatModel):
    """A fake chat model that replays a fixed list of AI messages.

    ``create_agent`` binds tools to whatever model it is given, which the stock fake
    rejects; accepting the bind and returning itself is enough to drive the real agent
    graph deterministically.
    """

    def bind_tools(self, tools, **kwargs):
        return self


@pytest.fixture
def turn_context() -> TurnContext:
    """A fresh per-turn context, as the runner builds for each user message."""
    return TurnContext(
        user_sub="test-user",
        conversation_id="test-conversation",
        surface="full",
        reporter_name="Test User",
    )


@pytest.fixture
def scripted_model():
    """Build a model that replays the given AI messages, one per model call."""

    def build(responses):
        return ScriptedModel(responses=responses)

    return build
