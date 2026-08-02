"""LangChain tool wrappers over JiraClient for use inside the agent graph."""

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.jira.adf import build_document
from app.jira.client import JiraClient


class SearchIssuesArgs(BaseModel):
    """Arguments for searching Jira for candidate duplicate issues."""

    jql: str = Field(description="A JQL query, e.g. 'project = KAN AND issuetype = Bug AND statusCategory != Done'.")
    max_results: int = Field(default=20, description="Maximum number of candidate issues to return.")


class CreateIssueArgs(BaseModel):
    """Arguments for creating a new Jira issue."""

    issue_type: str = Field(description="Issue type display name, e.g. 'Bug' or 'Request'.")
    summary: str = Field(description="Short one-line summary of the ticket.")
    description: str = Field(description="Full plain-text description; converted to ADF.")
    labels: list[str] = Field(default_factory=list, description="Labels to attach to the issue.")


def get_jira_tools(client: JiraClient | None = None) -> list:
    """Return LangChain tools bound to a JiraClient for the agent to call."""
    client = client or JiraClient()

    async def _search(jql: str, max_results: int = 20):
        return await client.search_issues(jql, fields=["summary", "status", "labels"], max_results=max_results)

    async def _create(issue_type: str, summary: str, description: str, labels: list[str] | None = None):
        return await client.create_issue(issue_type, summary, build_document(description), labels or [])

    return [
        StructuredTool.from_function(
            coroutine=_search,
            name="jira_search_issues",
            description="Search Jira for existing issues matching a JQL query to detect duplicates.",
            args_schema=SearchIssuesArgs,
        ),
        StructuredTool.from_function(
            coroutine=_create,
            name="jira_create_issue",
            description="Create a new Jira issue (bug or feature request) in the configured project.",
            args_schema=CreateIssueArgs,
        ),
    ]
