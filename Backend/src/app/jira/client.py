"""Async Jira Cloud client routed through the scoped-token endpoint."""

import httpx

from app.config import Settings, get_settings
from app.jira.adf import _to_adf

_TENANT_INFO_PATH = "/_edge/tenant_info"
_SCOPED_HOST = "https://api.atlassian.com/ex/jira"


class JiraClient:
    """Minimal async client for Jira Cloud REST v3 using a scoped API token."""

    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or get_settings()
        self._site_url = settings.jira_site_url.rstrip("/")
        self._email = settings.jira_email
        self._token = settings.jira_api_token
        self.project_key = settings.jira_project_key
        self.issue_type_bug = settings.jira_issue_type_bug
        self.issue_type_feature = settings.jira_issue_type_feature
        self._cloud_id: str | None = None

    def _auth(self) -> tuple[str, str]:
        return (self._email or "", self._token or "")

    async def resolve_cloud_id(self) -> str:
        """Resolve and cache the site's cloudId via the unauthenticated tenant_info endpoint."""
        if self._cloud_id is None:
            async with httpx.AsyncClient() as http:
                response = await http.get(f"{self._site_url}{_TENANT_INFO_PATH}")
                response.raise_for_status()
                self._cloud_id = response.json()["cloudId"]
        return self._cloud_id

    async def _api_base(self) -> str:
        cloud_id = await self.resolve_cloud_id()
        return f"{_SCOPED_HOST}/{cloud_id}/rest/api/3"

    async def create_issue(
        self,
        issue_type: str,
        summary: str,
        description: str,
        labels: list[str] | None = None,
    ) -> dict:
        """Create a Jira issue and return its key and id.

        issue_type is the display name (e.g. "Bug" or "Request"); description is
        plain text converted to ADF. Returns {"key", "id"}.
        """
        base = await self._api_base()
        fields = {
            "project": {"key": self.project_key},
            "issuetype": {"name": issue_type},
            "summary": summary,
            "description": _to_adf(description),
        }
        if labels:
            fields["labels"] = labels
        async with httpx.AsyncClient() as http:
            response = await http.post(f"{base}/issue", auth=self._auth(), json={"fields": fields})
            response.raise_for_status()
            data = response.json()
        return {"key": data["key"], "id": data["id"]}

    async def search_issues(
        self,
        jql: str,
        fields: list[str] | None = None,
        max_results: int = 20,
    ) -> list[dict]:
        """Run a JQL search and return the matching issues (each key + fields).

        Used to find candidate duplicate tickets before creating a new one.
        """
        base = await self._api_base()
        payload = {"jql": jql, "maxResults": max_results}
        if fields:
            payload["fields"] = fields
        async with httpx.AsyncClient() as http:
            response = await http.post(f"{base}/search/jql", auth=self._auth(), json=payload)
            response.raise_for_status()
            return response.json().get("issues", [])
