"""The tool that pulls a skill's full instructions into the conversation."""

from langchain.tools import tool

from app.agent.skills import skill_body, skill_descriptions


@tool
async def load_skill(name: str) -> str:
    """Load the full instructions for one of your available skills.

    Call this as soon as you recognise which skill covers the user's request, before
    asking them anything. The instructions tell you exactly what to gather and which
    tools to call.

    Args:
        name: The exact skill name from your list of available skills.
    """
    try:
        return skill_body(name)
    except KeyError:
        available = ", ".join(name for name, _ in skill_descriptions())
        return f"No skill named '{name}'. Available skills: {available}."
