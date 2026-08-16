"""End-to-end agent behaviour against the real gateway.

Marked live because each test drives the model. Run with:
docker compose run --rm api pytest tests/live -q -m live
"""

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.agent.context import TurnContext
from app.agent.factory import build_agent

pytestmark = pytest.mark.live

TERMINATION = "sorry, we can’t proceed with raising this issue."

REPORT = "the dashboard chart goes blank when I switch to the yearly view"


async def _publish(event):
    return None


def _normalise(text: str) -> str:
    return text.replace("'", "’").strip().lower()


class Session:
    """One scripted conversation against the agent graph."""

    def __init__(self, name):
        self.agent = build_agent(InMemorySaver(), _publish)
        self.config = {"configurable": {"thread_id": name}}
        self.context = TurnContext(
            user_sub=f"u-{name}",
            conversation_id=name,
            surface="panel",
            reporter_name="Tester",
            client_environment={"browser": "Chrome 129"},
        )
        self.tools = []
        self.all_tools = []
        self.prose = ""
        self.drafts = []
        self.transcript = ""

    async def say(self, payload):
        self.tools, self.prose = [], ""
        async for chunk in self.agent.astream(
            payload, self.config, context=self.context, stream_mode="updates"
        ):
            for update in chunk.values():
                if not isinstance(update, dict):
                    continue
                for message in update.get("messages", []):
                    for call in getattr(message, "tool_calls", None) or []:
                        self.tools.append(call["name"])
                        self.all_tools.append(call["name"])
                        if call["name"] in ("create_ticket", "link_to_existing"):
                            self.drafts.append(call["args"])
                    if type(message).__name__ == "AIMessage":
                        content = message.content
                        if isinstance(content, list):
                            content = "".join(
                                block.get("text", "")
                                for block in content
                                if isinstance(block, dict)
                            )
                        self.prose += content or ""
        self.transcript += f"\n{self.prose}"
        state = await self.agent.aget_state(self.config)
        return state.interrupts[0].value if state.interrupts else None

    async def user(self, text):
        return await self.say({"messages": [{"role": "user", "content": text}]})


def _is_evidence(value):
    return isinstance(value, dict) and "evidence_request" in value


def _is_steps(value):
    return isinstance(value, dict) and "steps_request" in value


@pytest.mark.parametrize("trial", range(3))
async def test_steps_are_collected_before_evidence(trial):
    session = Session(f"order-{trial}")

    value = await session.user(REPORT)

    assert "request_evidence" not in session.tools
    assert _is_steps(value), f"expected a steps prompt, got tools={session.tools}"


@pytest.mark.parametrize("trial", range(3))
async def test_refusing_steps_twice_terminates_without_filing(trial):
    session = Session(f"stop-{trial}")

    value = await session.user(REPORT)
    for _ in range(4):
        if not _is_steps(value):
            break
        value = await session.say(Command(resume=""))

    assert session.drafts == []
    assert TERMINATION in _normalise(session.transcript)


@pytest.mark.parametrize("trial", range(3))
async def test_steps_without_evidence_still_file(trial):
    session = Session(f"file-{trial}")

    value = await session.user(REPORT)
    assert _is_steps(value)
    value = await session.say(
        Command(resume="1. Open the dashboard\n2. Click the yearly toggle\n3. Chart goes blank")
    )
    if _is_evidence(value):
        value = await session.say(Command(resume=[]))
    if not session.drafts:
        await session.user("that's everything, please submit it")

    assert session.drafts, "expected a ticket to be drafted from steps alone"
    assert session.drafts[-1].get("steps_to_reproduce") is None


@pytest.mark.parametrize("trial", range(3))
async def test_evidence_is_offered_after_the_steps(trial):
    session = Session(f"offer-{trial}")

    value = await session.user(REPORT)
    assert _is_steps(value)
    for _ in range(4):
        value = await session.say(
            Command(resume="1. Open the dashboard\n2. Click the yearly toggle")
        )
        if not _is_steps(value):
            break

    assert _is_evidence(value), f"expected the picker after steps, got tools={session.all_tools}"
    assert session.all_tools.index("request_steps") < session.all_tools.index("request_evidence")


@pytest.mark.parametrize("trial", range(3))
async def test_the_users_own_words_become_the_steps(trial):
    session = Session(f"verbatim-{trial}")

    await session.user(REPORT)
    await session.say(Command(resume="1. Open the dashboard\n2. Click the yearly toggle"))
    state = await session.agent.aget_state(session.config)
    recorded = [
        str(message.content)
        for message in state.values["messages"]
        if getattr(message, "name", None) == "request_steps"
    ]

    assert recorded, "expected request_steps to have recorded a result"
    assert "Open the dashboard" in recorded[-1]
    assert "Click the yearly toggle" in recorded[-1]
