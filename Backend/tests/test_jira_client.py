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
