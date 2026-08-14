"""Core system prompt for the DailoQA assistant, authored in ``prompt.md``."""

from pathlib import Path

PROMPT_PATH = Path(__file__).resolve().parent / "prompt.md"

CORE_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")
