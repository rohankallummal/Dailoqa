"""The agent's tool registry.

Adding a capability means adding its tools here and dropping a SKILL.md into
``Backend/skills``. Nothing else about the agent changes.
"""

from app.agent.tools.documentation import read_documentation, search_documentation
from app.agent.tools.evidence import request_evidence
from app.agent.tools.jira import create_ticket, link_to_existing, search_existing_issues
from app.agent.tools.skills import load_skill
from app.agent.tools.steps import request_steps

TOOLS = [
    load_skill,
    search_existing_issues,
    request_steps,
    request_evidence,
    create_ticket,
    link_to_existing,
    search_documentation,
    read_documentation,
]

__all__ = ["TOOLS"]
