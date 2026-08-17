"""Resume-aware orchestration of a single ticket-creation job."""

from app.worker.create_step import create_ticket
from app.worker.dedupe import find_duplicate
from app.worker.link_step import link_ticket
from app.worker.notify import deliver_result
from app.worker.outcome import ALREADY_REPORTED, outcome_body
from app.worker.queue import complete_job

_NOTIFICATIONS = {
    "already_reported": ("ticket_already_reported", "Already reported"),
    "create": ("ticket_created", "Ticket created"),
    "link": ("ticket_linked", "Linked to existing"),
}


async def _resolve_ticket(session, job, client, model) -> tuple[str, str]:
    """Return the (jira_key, action) for a job, resuming a prior run when anchored.

    A job already anchored with jira_key + action is resumed through the same step that
    anchored it, so each step re-applies its own idempotent side effects: neither repeats
    the Jira issue itself, and both retry an evidence upload that never landed. Returning
    the key directly here instead would strand the resume branch of create_ticket, and a
    report whose attachments failed once would never get them. A fresh job runs
    authoritative dedupe and either links to a match or creates a new issue.

    The action "already_reported" is returned but never persisted. job.action is the resume
    anchor and must stay "create" or "link" so a resumed job re-enters the step that
    anchored it.
    """
    if job.jira_key and job.action in ("create", "link"):
        if job.action == "link":
            linked = await link_ticket(session, job, client, job.jira_key)
            return job.jira_key, ("link" if linked else "already_reported")
        await create_ticket(session, job, client)
        return job.jira_key, job.action

    verdict = await find_duplicate(job.payload["kind"], job.payload.get("ticket", {}), client=client, model=model)
    if verdict.match_key:
        linked = await link_ticket(session, job, client, verdict.match_key)
        return verdict.match_key, ("link" if linked else "already_reported")
    return await create_ticket(session, job, client), "create"


async def process_job(session, job, client, model=None, worker_id: str | None = None) -> bool:
    """Run one job: dedupe (unless resuming) -> create/link -> complete -> notify.

    Returns whether the job was completed. Completion is fenced on worker_id and happens
    before the notification, so a worker whose lease expired and was reaped mid-job tells
    the user nothing and leaves the job to whoever owns it now.

    Evidence cleanup is deliberately not done here: the caller commits after this
    returns, and deleting the files first would lose them if that commit failed and the
    job were retried. The caller removes the directory once the commit succeeds.
    """
    key, action = await _resolve_ticket(session, job, client, model)
    if not await complete_job(session, job.id, worker_id):
        return False
    kind = job.payload["kind"]
    if action == "already_reported":
        body = ALREADY_REPORTED[kind]
    else:
        body = await outcome_body(kind, action, key)
    notification_type, title = _NOTIFICATIONS[action]
    await deliver_result(session, job, notification_type, title, body, key)
    return True
