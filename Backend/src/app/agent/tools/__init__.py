"""The agent's tool registry.

Adding a capability means adding its tools here and dropping a SKILL.md into
``Backend/skills``. Nothing else about the agent changes.
"""

from app.agent.tools.jira import create_ticket, link_to_existing, search_existing_issues
from app.agent.tools.skills import load_skill

TOOLS = [load_skill, search_existing_issues, create_ticket, link_to_existing]

__all__ = ["TOOLS", "create_ticket", "link_to_existing", "load_skill", "search_existing_issues"]
