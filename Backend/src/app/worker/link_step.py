"""Idempotent linking of a reporter to an existing Jira issue."""

import logging

from sqlalchemy import select

from app.db.models import Ticket, TicketReporter
from app.evidence.storage import categorize
from app.jira.adf import (
    AFFECTED_USERS_HEADING,
    LEGACY_SIMILAR_REPORTS_HEADING,
    MORE_EVIDENCE_HEADING,
    affected_users_section,
    more_evidence_section,
    replace_section,
)
from app.jira.affected_users import AFFECTED_USERS_FILENAME, LEGACY_FILENAME, build_workbook
from app.worker.create_step import record_reporter
from app.worker.evidence_step import attach_evidence, evidence_of, reporter_prefix, upload_names
from app.worker.queue import set_job_action

logger = logging.getLogger(__name__)


def _is_repeat_report(existing, job_created_at) -> bool:
    """Whether a reporter row predates its job, meaning an earlier report wrote it.

    A row written after the job was created belongs to this job's own earlier attempt, so a
    resumed first-time link is not mistaken for the same user reporting twice.
    """
    return existing is not None and existing.added_at < job_created_at


async def _reporter_rows(session, ticket_id: str) -> list[dict]:
    """Return every recorded reporter for a ticket, oldest first."""
    rows = (
        (
            await session.execute(
                select(TicketReporter)
                .where(TicketReporter.ticket_id == ticket_id)
                .order_by(TicketReporter.added_at)
            )
        )
        .scalars()
        .all()
    )
    return [
        {"name": row.user_name or row.user_sub, "oauth_id": row.user_sub, "reported_at": row.added_at}
        for row in rows
    ]


def linked_evidence(attachments: list[dict], prefixes: list[str]) -> list[dict]:
    """Return the attachments contributed by reporters who linked after the issue existed.

    The naming convention is the only marker, which is what lets this be rebuilt from the
    live issue rather than tracked in the database: a retry recomputes the same list.
    """
    if not prefixes:
        return []
    selected = [
        item
        for item in attachments
        if any(item["filename"].startswith(f"{prefix}-") for prefix in prefixes)
    ]
    return [
        {
            "name": item["filename"],
            "category": categorize(item["filename"]),
            "size": item.get("size") or 0,
        }
        for item in sorted(selected, key=lambda item: item["filename"])
    ]


async def _replace_spreadsheet(client, issue_key: str, rows: list[dict]) -> None:
    """Upload a freshly generated workbook, removing whatever it supersedes.

    Both the current and the legacy filename are removed, so an issue last touched before
    the rename ends up holding one spreadsheet rather than two.
    """
    superseded = {AFFECTED_USERS_FILENAME, LEGACY_FILENAME}
    for attachment in await client.list_attachments(issue_key):
        if attachment["filename"] in superseded:
            await client.delete_attachment(attachment["id"])
    await client.add_attachment_bytes(issue_key, AFFECTED_USERS_FILENAME, build_workbook(rows))


async def _refresh_sections(client, issue_key: str, prefixes: list[str]) -> None:
    """Rewrite More Evidence and Affected Users, dropping the legacy section.

    Both are replaced rather than appended because their contents change with every new
    report, and the legacy Similar Reports heading is removed so a migrated issue does not
    carry two descriptions of the same thing.
    """
    files = linked_evidence(await client.list_attachments(issue_key), prefixes)
    document = await client.get_description(issue_key)
    document = replace_section(document, LEGACY_SIMILAR_REPORTS_HEADING, [])
    document = replace_section(document, MORE_EVIDENCE_HEADING, more_evidence_section(files))
    document = replace_section(
        document, AFFECTED_USERS_HEADING, affected_users_section(AFFECTED_USERS_FILENAME)
    )
    await client.update_description(issue_key, document)


async def update_shared_sections(session, client, ticket_id: str, issue_key: str) -> None:
    """Refresh the spreadsheet and both sections once a second user reports.

    Failures are logged and swallowed. The reporter link and the evidence upload are the
    load-bearing work, and everything here is regenerated from the reporter rows and the
    issue's own attachments on the next link, so a failed attempt heals itself rather than
    costing the job an attempt.

    The first row is the reporter who filed the issue, so their evidence keeps its original
    filenames and stays out of More Evidence.
    """
    rows = await _reporter_rows(session, ticket_id)
    if len(rows) < 2:
        return
    prefixes = [reporter_prefix(row["name"], row["oauth_id"]) for row in rows[1:]]
    try:
        await _replace_spreadsheet(client, issue_key, rows)
        await _refresh_sections(client, issue_key, prefixes)
    except Exception as error:  # noqa: BLE001
        logger.warning("shared sections update failed for %s: %s", issue_key, error)


async def link_ticket(session, job, client, match_key: str) -> bool:
    """Attach the reporter to an existing issue: comment + label + reporter row, once.

    Returns whether this link should be reported as fresh. False means the same user had
    already reported the issue before this job existed, which the caller turns into the
    already-reported outcome rather than a link.

    The ticket_reporters (ticket_id, user_sub) unique row is the authoritative link
    marker and makes this safe to retry (a rare duplicate comment is tolerated).

    Evidence is uploaded to the matched issue on every attempt, before the reporter row is
    consulted. The reporter row cannot gate it: an upload that failed after that row was
    written would never be retried, and the caller deletes the files once the job
    commits, so the screenshots proving a duplicate report would be lost for good.

    The Similar Reports refresh runs on every attempt for the same reason: it is driven by
    the reporter rows, so a retry after the row was written still produces the spreadsheet.
    """
    ticket = (await session.execute(select(Ticket).where(Ticket.jira_key == match_key))).scalar_one_or_none()
    if ticket is None:
        ticket = Ticket(jira_key=match_key, type=job.payload["kind"], title=match_key)
        session.add(ticket)
        await session.flush()
    existing = (
        await session.execute(
            select(TicketReporter).where(
                TicketReporter.ticket_id == ticket.id, TicketReporter.user_sub == job.user_sub
            )
        )
    ).scalar_one_or_none()
    repeat = _is_repeat_report(existing, job.created_at)
    await set_job_action(session, job.id, "link", jira_key=match_key)
    reporter_name = (job.payload.get("reporter", {})).get("name") or job.user_sub
    prefix = reporter_prefix(reporter_name, job.user_sub)
    await attach_evidence(
        job, client, match_key, upload_names(prefix, [item["name"] for item in evidence_of(job)])
    )
    if existing is None:
        await client.add_comment(match_key, f"Also reported by {reporter_name}")
        await client.add_labels(match_key, ["also-affected"])
        await record_reporter(session, ticket.id, job.user_sub, reporter_name)
    await update_shared_sections(session, client, ticket.id, match_key)
    return not repeat
