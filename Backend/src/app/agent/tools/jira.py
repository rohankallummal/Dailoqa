"""Tools that let the agent search Jira and enqueue durable ticket jobs.

Ticket writes never call Jira inline. They enqueue a Job row and let the existing
worker do the creation, so a dropped connection or a crashed request can never lose
a report the user already confirmed.
"""

import logging
from typing import Literal

from langchain.tools import ToolRuntime, tool

from app.db.base import async_session
from app.db.models import Job
from app.db.repositories import reported_issue_keys
from app.evidence.storage import evidence_dir, normalize_manifest
from app.jira.client import JiraClient

logger = logging.getLogger(__name__)

_MAX_CANDIDATES = 20


def _escape(term: str) -> str:
    """Escape a user-derived term for safe embedding in a JQL quoted string."""
    return term.replace("\\", "\\\\").replace('"', '\\"')


def _candidate_jql(keywords: list[str], issue_type: str, project_key: str) -> str:
    """Build a JQL query matching open issues of a type whose text mentions the keywords."""
    terms = [_escape(word) for word in keywords if word.strip()]
    clause = " OR ".join(f'text ~ "{term}"' for term in terms)
    query = f'project = {project_key} AND issuetype = "{issue_type}" AND statusCategory != Done'
    if clause:
        query = f"{query} AND ({clause})"
    return f"{query} ORDER BY updated DESC"


def _mark_reported(issues: list[dict], reported: frozenset[str]) -> list[dict]:
    """Attach already_reported_by_you to every candidate, leaving the input untouched."""
    return [{**issue, "already_reported_by_you": issue.get("key") in reported} for issue in issues]


async def _flag_own_reports(user_sub: str, issues: list[dict]) -> list[dict]:
    """Mark which candidates this user has already filed a report against.

    A lookup failure marks nothing rather than failing the search. The Jira results are
    already in hand, refusing here would block filing outright, and the worker runs the
    authoritative check before any ticket is written.
    """
    keys = [issue["key"] for issue in issues if issue.get("key")]
    if not keys:
        return _mark_reported(issues, frozenset())
    try:
        async with async_session() as session:
            reported = await reported_issue_keys(session, user_sub, keys)
    except Exception as error:
        logger.warning("own-report lookup failed for %s: %s", user_sub, error)
        reported = frozenset()
    return _mark_reported(issues, reported)


@tool
async def search_existing_issues(
    keywords: list[str],
    kind: Literal["bug", "feature"],
    runtime: ToolRuntime,
) -> list[dict]:
    """Search Jira for open issues that may already cover the user's report.

    Always run this before filing anything. Filing a duplicate is worse than filing
    nothing.

    Every result carries ``already_reported_by_you``. When it is true, this same user has
    already filed a report against that issue.

    Args:
        keywords: Distinctive words from the report — the error text, the affected
            feature, the page name. Do not pass generic words like "error" or "bug".
        kind: "bug" for a defect, "feature" for a requested capability.
    """
    client = JiraClient()
    jql = _candidate_jql(keywords, client.issue_type_for(kind), client.project_key)
    issues = await client.search_issues(jql, fields=["summary", "status"], max_results=_MAX_CANDIDATES)
    return await _flag_own_reports(runtime.context.user_sub, issues)


async def _enqueue(runtime: ToolRuntime, payload: dict, jira_key: str | None, action: str | None) -> str:
    """Insert a queued job for the worker and return its id."""
    context = runtime.context
    async with async_session() as session:
        job = Job(
            type="create_ticket",
            status="queued",
            conversation_id=context.conversation_id,
            user_sub=context.user_sub,
            payload=payload,
            jira_key=jira_key,
            action=action,
        )
        session.add(job)
        await session.flush()
        job_id = job.id
        await session.commit()
    return job_id


def _stored_evidence(user_sub: str, conversation_id: str) -> list[dict]:
    """Rebuild the evidence manifest from the files actually on disk.

    The manifest reaches the agent as a resumed interrupt value inside
    ``request_evidence`` and is never threaded through agent state, so the conversation's
    evidence directory is the only place that truth still lives by the time a ticket is
    filed. Reading it back is also the safer source: name, category, and size are
    re-derived from the stored files, so a ticket can never claim an attachment that is
    not on disk for the worker to upload.
    """
    try:
        directory = evidence_dir(user_sub, conversation_id)
    except ValueError:
        return []
    if not directory.is_dir():
        return []
    names = [{"name": path.name} for path in sorted(directory.iterdir()) if path.is_file()]
    return normalize_manifest(user_sub, conversation_id, names)


def _payload(runtime: ToolRuntime, kind: str, ticket: dict) -> dict:
    """Build the worker payload from the drafted ticket and trusted turn context."""
    context = runtime.context
    return {
        "kind": kind,
        "ticket": ticket,
        "client_environment": context.client_environment,
        "reporter": {"name": context.reporter_name, "oauth_id": context.user_sub},
        "evidence": _stored_evidence(context.user_sub, context.conversation_id),
    }


@tool
async def create_ticket(
    kind: Literal["bug", "feature"],
    title: str,
    summary: str,
    description: str,
    runtime: ToolRuntime,
    steps_to_reproduce: list[str] | None = None,
) -> str:
    """File a new ticket with the DailoQA development team.

    Only call this once you have searched for duplicates and the user has agreed to
    proceed. Write every field in clear prose based solely on what the user actually
    said — never invent a detail.

    Args:
        kind: "bug" for a defect, "feature" for a requested capability.
        title: Short enough to read at a glance on a Jira board.
        summary: One or two plain sentences on what is wrong or wanted, and where.
        description: The full account — for a bug, what happens versus what was
            expected; for a feature, the capability and the problem it solves. Never
            the browser, device, or operating system: those are captured from the
            user's session and written into their own section of the issue.
        steps_to_reproduce: Ordered reproduction steps. Bugs only, and only when the
            user described them or attached no evidence.
    """
    ticket = {
        "title": title,
        "summary": summary,
        "issue_description" if kind == "bug" else "feature": description,
        "steps_to_reproduce": steps_to_reproduce or [],
    }
    if kind == "feature":
        ticket["problem_statement"] = summary
    job_id = await _enqueue(runtime, _payload(runtime, kind, ticket), None, None)
    return f"Queued for filing as job {job_id}. Tell the user it is being submitted."


@tool
async def link_to_existing(
    issue_key: str,
    note: str,
    kind: Literal["bug", "feature"],
    runtime: ToolRuntime,
) -> str:
    """Attach this user's report to an existing Jira issue instead of filing a duplicate.

    Call this once you have judged that an existing issue is the same problem the user
    is describing. That judgement is yours to make — the user cannot see the tracker,
    so do not ask them to confirm the match.

    Args:
        issue_key: The Jira key of the matching issue, e.g. "KAN-482".
        note: What this reporter adds — a different trigger, extra detail, or
            "same as described".
        kind: "bug" or "feature", matching the existing issue.
    """
    ticket = {"title": issue_key, "summary": note, "issue_description": note, "steps_to_reproduce": []}
    payload = _payload(runtime, kind, ticket)
    job_id = await _enqueue(runtime, payload, issue_key, "link")
    return f"Queued as job {job_id}. Tell the user their report was recorded and is with the team."
