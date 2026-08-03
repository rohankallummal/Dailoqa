"""Middleware that advertises available skills without loading their bodies."""

from langchain.agents.middleware import dynamic_prompt

from app.agent.prompt import CORE_PROMPT
from app.agent.skills import skill_descriptions


def _skill_catalogue() -> str:
    """Render the one-line description of every registered skill."""
    lines = [f"- {name}: {description}" for name, description in skill_descriptions()]
    if not lines:
        return "No skills are currently available."
    return "\n".join(lines)


@dynamic_prompt
def skills_middleware(request) -> str:
    """Append the skill catalogue to the core prompt for every model call."""
    return f"{CORE_PROMPT}\n\n## Available skills\n{_skill_catalogue()}\n"
