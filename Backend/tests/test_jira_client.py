import json

import httpx
import pytest
import respx

from app.config import get_settings
from app.jira.client import JiraClient

CLOUD_ID = "1324a887-0000-0000-0000-000000000000"


@pytest.fixture(autouse=True)
def _jira_env(base_env, monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("JIRA_SITE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "bot@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "secret-token")
    monkeypatch.setenv("JIRA_PROJECT_KEY", "KAN")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.mark.asyncio
@respx.mock
async def test_resolve_cloud_id_hits_tenant_info_and_caches():
    route = respx.get("https://example.atlassian.net/_edge/tenant_info").mock(
        return_value=httpx.Response(200, json={"cloudId": CLOUD_ID})
    )
    client = JiraClient()
    assert await client.resolve_cloud_id() == CLOUD_ID
    assert await client.resolve_cloud_id() == CLOUD_ID
    assert route.call_count == 1


@pytest.mark.asyncio
@respx.mock
async def test_api_base_uses_scoped_route():
    respx.get("https://example.atlassian.net/_edge/tenant_info").mock(
        return_value=httpx.Response(200, json={"cloudId": CLOUD_ID})
    )
    base = await JiraClient()._api_base()
    assert base == f"https://api.atlassian.com/ex/jira/{CLOUD_ID}/rest/api/3"


@pytest.mark.asyncio
@respx.mock
async def test_create_issue_posts_adf_and_returns_key():
    respx.get("https://example.atlassian.net/_edge/tenant_info").mock(
        return_value=httpx.Response(200, json={"cloudId": CLOUD_ID})
    )
    create = respx.post(
        f"https://api.atlassian.com/ex/jira/{CLOUD_ID}/rest/api/3/issue"
    ).mock(return_value=httpx.Response(201, json={"id": "10001", "key": "KAN-1"}))

    result = await JiraClient().create_issue(
        issue_type="Bug",
        summary="Search returns no results",
        description="Steps: search, see empty results.",
        labels=["agent-filed"],
    )

    assert result == {"key": "KAN-1", "id": "10001"}
    fields = json.loads(create.calls.last.request.read())["fields"]
    assert fields["project"]["key"] == "KAN"
    assert fields["issuetype"]["name"] == "Bug"
    assert fields["description"]["type"] == "doc"


@pytest.mark.asyncio
@respx.mock
async def test_search_issues_returns_issue_list():
    respx.get("https://example.atlassian.net/_edge/tenant_info").mock(
        return_value=httpx.Response(200, json={"cloudId": CLOUD_ID})
    )
    respx.post(
        f"https://api.atlassian.com/ex/jira/{CLOUD_ID}/rest/api/3/search/jql"
    ).mock(
        return_value=httpx.Response(
            200,
            json={"issues": [{"key": "KAN-1", "fields": {"summary": "Search bug"}}]},
        )
    )
    issues = await JiraClient().search_issues(
        jql='project = KAN AND issuetype = Bug AND statusCategory != Done',
        fields=["summary"],
        max_results=10,
    )
    assert issues == [{"key": "KAN-1", "fields": {"summary": "Search bug"}}]


@pytest.mark.asyncio
@respx.mock
async def test_add_comment_posts_adf_body():
    respx.get("https://example.atlassian.net/_edge/tenant_info").mock(
        return_value=httpx.Response(200, json={"cloudId": CLOUD_ID})
    )
    route = respx.post(
        f"https://api.atlassian.com/ex/jira/{CLOUD_ID}/rest/api/3/issue/KAN-1/comment"
    ).mock(return_value=httpx.Response(201, json={"id": "9"}))
    await JiraClient().add_comment("KAN-1", "Also reported by user@example.com")
    assert json.loads(route.calls.last.request.read())["body"]["type"] == "doc"


@pytest.mark.asyncio
@respx.mock
async def test_add_labels_puts_update_ops():
    respx.get("https://example.atlassian.net/_edge/tenant_info").mock(
        return_value=httpx.Response(200, json={"cloudId": CLOUD_ID})
    )
    route = respx.put(
        f"https://api.atlassian.com/ex/jira/{CLOUD_ID}/rest/api/3/issue/KAN-1"
    ).mock(return_value=httpx.Response(204))
    await JiraClient().add_labels("KAN-1", ["also-affected"])
    update = json.loads(route.calls.last.request.read())["update"]
    assert update["labels"][0]["add"] == "also-affected"
