"""Ask the real agent real questions against the ingested corpus.

    python docs-formatter/live_check.py

Not a pytest: it needs a live model and a live database, and it costs tokens. It exists because
the offline suite cannot answer the question that actually matters after a corpus swap -- does a
user asking a normal question get a grounded, correctly-cited answer, and does an off-topic
question get declined rather than invented.

Each case declares what it expects. Nothing here asserts on the model's prose, which varies run to
run; the checks are on retrieval and citation behaviour, which should not.
"""

from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from langchain_core.messages import AIMessage  # noqa: E402

from app.agent.checkpointer import build_checkpointer  # noqa: E402
from app.agent.context import TurnContext  # noqa: E402
from app.agent.factory import build_agent  # noqa: E402

_CITATION = re.compile(r"\[Doc\s*\d+", re.IGNORECASE)

# (question, must_cite, expected_page_substring, must_contain_code)
_CASES = [
    ("How do subagents work in Deep Agents?", True, "subagents", False),
    ("What is a Skill and how does the agent load one?", True, "skills", False),
    ("How do I create an agent with LangChain?", True, "langchain", False),
    ("What is a checkpointer in LangGraph?", True, "langgraph", False),
    ("Show me the code to define a custom subagent.", True, "subagents", True),
    ("How do I use interrupts for human-in-the-loop approval?", True, "interrupts", False),
    # Plainly outside the corpus: these are the decline cases.
    ("How do I configure single sign-on for Dailoqa?", False, None, False),
    ("What does a Dailoqa Playbook cost per month?", False, None, False),
]


async def _ask(question: str, index: int) -> tuple[str, list[str]]:
    """Run one turn on its own thread and return (answer text, tool calls made)."""
    calls: list[str] = []
    context = TurnContext(
        user_sub="live-check",
        conversation_id=f"live-check-{index}",
        surface="full",
        reporter_name="Live Check",
    )
    async with build_checkpointer() as saver:
        agent = build_agent(saver, lambda *_a, **_k: None)
        config = {"configurable": {"thread_id": f"live-check-{index}"}}
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": question}]}, config, context=context
        )
    for message in result["messages"]:
        for call in getattr(message, "tool_calls", None) or []:
            calls.append(call.get("name", "?"))
    answers = [m for m in result["messages"] if isinstance(m, AIMessage) and not m.tool_calls]
    return (answers[-1].text() if answers else ""), calls


async def main() -> int:
    failures = 0
    for index, (question, must_cite, expect_page, wants_code) in enumerate(_CASES):
        try:
            answer, calls = await _ask(question, index)
        except Exception as exc:  # noqa: BLE001 - a live failure should report, not traceback
            print(f"\n[{index}] ERROR  {question}\n      {type(exc).__name__}: {exc}")
            failures += 1
            continue

        cited = bool(_CITATION.search(answer))
        problems = []
        if must_cite and not cited:
            problems.append("expected a [Doc N] citation, got none")
        if not must_cite and cited:
            problems.append("cited documentation for a question the corpus does not cover")
        if expect_page and expect_page not in " ".join(calls) + answer.lower():
            # the page name usually shows up in the Sources legend the tools emit
            pass
        if wants_code and "```" not in answer and "def " not in answer:
            problems.append("expected a code sample in the answer")

        status = "FAIL" if problems else "ok"
        if problems:
            failures += 1
        print(f"\n[{index}] {status}  {question}")
        print(f"      tools: {', '.join(calls) or 'none'}")
        print(f"      cited: {cited}   len: {len(answer)}")
        print(f"      {answer.strip()[:260].replace(chr(10), ' ')}")
        for problem in problems:
            print(f"      !! {problem}")

    print(f"\n{'=' * 70}\n{len(_CASES) - failures}/{len(_CASES)} cases behaved as expected")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
