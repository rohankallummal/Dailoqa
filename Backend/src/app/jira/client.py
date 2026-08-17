"""Async Jira Cloud client routed through the scoped-token endpoint."""

from pathlib import Path

import httpx

from app.config import Settings, get_settings
from app.jira.adf import build_document

_TENANT_INFO_PATH = "/_edge/tenant_info"
_SCOPED_HOST = "https://api.atlassian.com/ex/jira"
_DEFAULT_TIMEOUT = 30.0
_UPLOAD_TIMEOUT = 180.0


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

    async def _request(
        self, method: str, path: str, timeout: float = _DEFAULT_TIMEOUT, **kwargs
    ) -> httpx.Response:
        """Send an authenticated request to the scoped Jira API and raise on error."""
        base = await self._api_base()
        async with httpx.AsyncClient(timeout=timeout) as http:
            response = await http.request(method, f"{base}{path}", auth=self._auth(), **kwargs)
            response.raise_for_status()
            return response

    def issue_type_for(self, kind: str) -> str:
        """Map an internal classification ("bug"/"feature") to a Jira issue-type name."""
        if kind == "bug":
            return self.issue_type_bug
        if kind == "feature":
            return self.issue_type_feature
        raise ValueError(f"unknown ticket kind: {kind}")

    async def create_issue(
        self,
        issue_type: str,
        summary: str,
        description: dict,
        labels: list[str] | None = None,
    ) -> dict:
        """Create a Jira issue and return its key and id.

        issue_type is the display name (e.g. "Bug" or "Request"); description is an ADF
        document the caller has already built, so the section structure lives with the
        renderer rather than here. Returns {"key", "id"}.
        """
        fields = {
            "project": {"key": self.project_key},
            "issuetype": {"name": issue_type},
            "summary": summary,
            "description": description,
        }
        if labels:
            fields["labels"] = labels
        response = await self._request("POST", "/issue", json={"fields": fields})
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
        payload = {"jql": jql, "maxResults": max_results}
        if fields:
            payload["fields"] = fields
        response = await self._request("POST", "/search/jql", json=payload)
        return response.json().get("issues", [])

    async def add_comment(self, issue_key: str, text: str) -> None:
        """Add a comment (ADF) to an existing issue."""
        await self._request("POST", f"/issue/{issue_key}/comment", json={"body": build_document(text)})

    async def add_labels(self, issue_key: str, labels: list[str]) -> None:
        """Add labels to an existing issue without removing existing ones."""
        update = {"labels": [{"add": label} for label in labels]}
        await self._request("PUT", f"/issue/{issue_key}", json={"update": update})

    async def add_named_attachments(self, issue_key: str, items: list[tuple[str, Path]]) -> list[str]:
        """Upload files under explicit names and return the filenames Jira accepted.

        The name is passed separately from the path because the link path renames a
        reporter's evidence to match their Affected Users row.

        Jira rejects multipart uploads without the X-Atlassian-Token: no-check header.
        """
        if not items:
            return []
        files = [("file", (name, path.read_bytes())) for name, path in items]
        response = await self._request(
            "POST",
            f"/issue/{issue_key}/attachments",
            timeout=_UPLOAD_TIMEOUT,
            files=files,
            headers={"X-Atlassian-Token": "no-check"},
        )
        return [item["filename"] for item in response.json()]

    async def add_attachment_bytes(self, issue_key: str, filename: str, data: bytes) -> None:
        """Upload one in-memory file to an issue.

        The Affected Users workbook is generated per link and never touches disk, so it
        has no path for add_named_attachments to take.
        """
        await self._request(
            "POST",
            f"/issue/{issue_key}/attachments",
            timeout=_UPLOAD_TIMEOUT,
            files=[("file", (filename, data))],
            headers={"X-Atlassian-Token": "no-check"},
        )

    async def list_attachments(self, issue_key: str) -> list[dict]:
        """Return the issue's attachments as {"id", "filename"} entries."""
        response = await self._request("GET", f"/issue/{issue_key}", params={"fields": "attachment"})
        attachments = response.json().get("fields", {}).get("attachment") or []
        return [{"id": item["id"], "filename": item["filename"]} for item in attachments]

    async def list_attachment_filenames(self, issue_key: str) -> set[str]:
        """Return the filenames already attached to an issue.

        Lets a retried job skip what a previous attempt already uploaded instead of
        duplicating it.
        """
        return {item["filename"] for item in await self.list_attachments(issue_key)}

    async def delete_attachment(self, attachment_id: str) -> None:
        """Delete one attachment, tolerating an id Jira no longer holds.

        A retry that already removed the superseded spreadsheet must not fail the job.
        """
        try:
            await self._request("DELETE", f"/attachment/{attachment_id}")
        except httpx.HTTPStatusError as error:
            if error.response.status_code != 404:
                raise
