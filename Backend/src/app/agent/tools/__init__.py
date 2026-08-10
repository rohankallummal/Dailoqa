"""The agent's tool registry.

Adding a capability means adding its tools here and dropping a SKILL.md into
``Backend/skills``. Nothing else about the agent changes.

The documentation tools are kept as their own list because the agent can be built
without them: ``rag_enabled`` turns the documentation capability off as a unit.
"""

from app.agent.tools.docs import (
    CITING_DOC_TOOLS,
    DOC_SKILL_NAME,
    DOC_TOOL_NAMES,
    citable_passages_retrieved,
    documentation_skill_loaded,
    documentation_tool_used,
    fetch_document_section,
    list_documentation_sources,
    search_documentation,
)
from app.agent.tools.evidence import request_evidence
from app.agent.tools.jira import create_ticket, link_to_existing, search_existing_issues
from app.agent.tools.skills import load_skill
from app.config import get_settings

TICKET_TOOLS = [search_existing_issues, request_evidence, create_ticket, link_to_existing]

DOC_TOOLS = [search_documentation, list_documentation_sources, fetch_document_section]

TOOLS = [load_skill, *TICKET_TOOLS, *DOC_TOOLS]
"""Every tool that exists. Use ``active_tools()`` to build an agent."""


def active_tools() -> list:
    """The tools this configuration exposes to the model.

    Documentation Q&A is switchable at runtime: with ``rag_enabled`` off the tools are
    never bound, so the model cannot call a capability whose corpus may be missing or
    stale. The skill is hidden alongside them (see the skills middleware) so it never
    advertises instructions for tools that are not there.
    """
    tools = [load_skill, *TICKET_TOOLS]
    if get_settings().rag_enabled:
        tools.extend(DOC_TOOLS)
    return tools


__all__ = [
    "CITING_DOC_TOOLS",
    "DOC_SKILL_NAME",
    "DOC_TOOLS",
    "DOC_TOOL_NAMES",
    "TICKET_TOOLS",
    "TOOLS",
    "active_tools",
    "citable_passages_retrieved",
    "documentation_skill_loaded",
    "documentation_tool_used",
    "create_ticket",
    "fetch_document_section",
    "link_to_existing",
    "list_documentation_sources",
    "load_skill",
    "request_evidence",
    "search_documentation",
    "search_existing_issues",
]
