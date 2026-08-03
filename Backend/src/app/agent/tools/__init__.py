"""The agent's tool registry.

Adding a capability means adding its tools here and dropping a SKILL.md into
``Backend/skills``. Nothing else about the agent changes.
"""

from app.agent.tools.skills import load_skill

TOOLS = [load_skill]

__all__ = ["TOOLS", "load_skill"]
