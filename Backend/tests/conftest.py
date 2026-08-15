"""Shared test setup.

Pins a SelectorEventLoop on Windows: psycopg's async mode rejects the ProactorEventLoop
that Python installs by default there, and the database-backed tests would fail on that
alone. Also provides the fakes the agent tests drive the graph with, so no test in this
suite needs a live model or an API key.
"""

import asyncio
import json
import sys
from pathlib import Path

import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

from app.agent.context import TurnContext

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

_MANIFEST = Path(__file__).resolve().parents[1] / "docs-corpus" / "manifest.json"


def corpus_sources() -> set[str]:
    """Every page the corpus is supposed to contain, read from the manifest.

    Derived rather than hard-coded so that adding or renaming a page updates the tests with
    it. The previous literal set silently described a corpus that no longer existed the
    moment ``DOCS_PATH`` moved, which is a test that passes while asserting nothing.
    """
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    return {page["vault_path"] for page in manifest["pages"]}


def corpus_page(slug: str, topic: str | None = None) -> str:
    """The vault path of one page -- e.g. ``"skills"`` -> ``deep-agents/skills.md``.

    ``topic`` disambiguates slugs that exist in more than one place: each of the three topics
    ships an ``overview``. Raising on an ambiguous or unknown slug is deliberate, so a renamed
    page fails loudly here rather than quietly matching nothing downstream.
    """
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    matches = [
        page["vault_path"]
        for page in manifest["pages"]
        if page["slug"] == slug and (topic is None or page["topic"] == topic)
    ]
    if len(matches) != 1:
        raise LookupError(
            f"slug={slug!r} topic={topic!r} matched {len(matches)} manifest pages, expected 1"
        )
    return matches[0]


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
