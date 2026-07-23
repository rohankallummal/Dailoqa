import pytest

from app.jira.client import JiraClient
from app.jira.tools import get_jira_tools


class _FakeClient(JiraClient):
    def __init__(self):
        self.searched = None
        self.project_key = "KAN"

    async def search_issues(self, jql, fields=None, max_results=20):
        self.searched = jql
        return [{"key": "KAN-1", "fields": {"summary": "dup"}}]


def test_tools_expose_search_and_create_with_descriptions():
    tools = get_jira_tools(_FakeClient())
    names = {t.name for t in tools}
    assert "jira_search_issues" in names
    assert "jira_create_issue" in names
    search = next(t for t in tools if t.name == "jira_search_issues")
    assert search.description
    assert search.args_schema is not None


@pytest.mark.asyncio
async def test_search_tool_invokes_client():
    client = _FakeClient()
    search = next(t for t in get_jira_tools(client) if t.name == "jira_search_issues")
    result = await search.ainvoke({"jql": "project = KAN"})
    assert client.searched == "project = KAN"
    assert result[0]["key"] == "KAN-1"
