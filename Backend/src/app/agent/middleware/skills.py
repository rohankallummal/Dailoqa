"""Middleware that advertises available skills without loading their bodies.

Skills are normally disclosed on demand: the catalogue lists names and descriptions, and
``load_skill`` fetches a body once the agent recognises which one applies. Documentation is
the exception, because its tools are bound unconditionally — the agent can reach them
without ever loading the skill, and then answers with none of the procedure that governs
how documentation must be used. So when a documentation tool has been called and the skill
was not loaded, its body is folded into the prompt here instead.
"""

from langchain.agents.middleware import dynamic_prompt

from app.agent.prompt import CORE_PROMPT
from app.agent.skills import skill_body, skill_descriptions
from app.agent.tools import DOC_SKILL_NAME, documentation_skill_loaded, documentation_tool_used
from app.config import get_settings


def _hidden_skills() -> frozenset[str]:
    """Skills whose capability is switched off for this configuration."""
    if get_settings().rag_enabled:
        return frozenset()
    return frozenset({DOC_SKILL_NAME})


def _skill_catalogue() -> str:
    """Render the one-line description of every advertised skill."""
    lines = [
        f"- {name}: {description}"
        for name, description in skill_descriptions(exclude=_hidden_skills())
    ]
    if not lines:
        return "No skills are currently available."
    return "\n".join(lines)


def _autoloaded_documentation(messages) -> str:
    """The documentation skill's body, when its tools are in use without it.

    Returns an empty string in every other case, so a ticketing conversation carries no
    documentation instructions and a thread that called ``load_skill`` does not receive the
    body a second time.
    """
    if DOC_SKILL_NAME in _hidden_skills():
        return ""
    if not documentation_tool_used(messages) or documentation_skill_loaded(messages):
        return ""
    return f"\n## {DOC_SKILL_NAME}\n{skill_body(DOC_SKILL_NAME)}\n"


@dynamic_prompt
def skills_middleware(request) -> str:
    """Build the system prompt: core instructions, the skill catalogue, and any auto-load."""
    messages = (request.state or {}).get("messages", [])
    return (
        f"{CORE_PROMPT}\n\n## Available skills\n{_skill_catalogue()}\n"
        f"{_autoloaded_documentation(messages)}"
    )
