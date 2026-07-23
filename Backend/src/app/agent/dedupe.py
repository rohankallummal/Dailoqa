"""Deduplication: find an existing Jira issue that matches the user's report."""

from pydantic import BaseModel, Field

from app.jira.client import JiraClient
from app.llm import get_chat_model

_CONFIDENCE_THRESHOLD = 0.7


class DedupeVerdict(BaseModel):
    """The LLM's judgment on whether a candidate issue matches the report."""

    match_key: str | None = Field(default=None, description="The matching issue key, or null if none match.")
    confidence: float = Field(default=0.0, description="Confidence between 0 and 1 that the match is a true duplicate.")


def build_jql(kind: str, project_key: str, issue_type: str) -> str:
    """Build a JQL query for open issues of the matching type in the project."""
    return f'project = {project_key} AND issuetype = "{issue_type}" AND statusCategory != Done ORDER BY created DESC'


async def find_duplicate(kind: str, fields: dict, client=None, model=None) -> DedupeVerdict:
    """Search Jira for candidates and ask the LLM whether any is a true duplicate."""
    client = client or JiraClient()
    model = model or get_chat_model("agent")
    issue_type = client.issue_type_for(kind)
    candidates = await client.search_issues(
        build_jql(kind, client.project_key, issue_type), fields=["summary"], max_results=20
    )
    if not candidates:
        return DedupeVerdict(match_key=None, confidence=0.0)
    structured = model.with_structured_output(DedupeVerdict)
    prompt = f"New {kind} report: {fields}. Candidates: {candidates}. Which candidate, if any, is the same issue?"
    verdict = await structured.ainvoke(prompt)
    if verdict.confidence < _CONFIDENCE_THRESHOLD:
        return DedupeVerdict(match_key=None, confidence=verdict.confidence)
    return verdict
