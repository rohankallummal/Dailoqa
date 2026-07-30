"""Resume-aware orchestration of a single ticket-creation job."""

from app import messages
from app.agent.dedupe import find_duplicate
from app.worker.create_step import create_ticket
from app.worker.link_step import link_ticket
from app.worker.notify import deliver_result
from app.worker.queue import complete_job


async def _resolve_ticket(session, job, client, model) -> tuple[str, str]:
    """Return the (jira_key, action) for a job, resuming a prior run when anchored.

    A job already anchored with jira_key + action is resumed through the same step that
    anchored it, so each step re-applies its own idempotent side effects: neither repeats
    the Jira issue itself, and both retry an evidence upload that never landed. Returning
    the key directly here instead would strand the resume branch of create_ticket, and a
    report whose attachments failed once would never get them. A fresh job runs
    authoritative dedupe and either links to a match or creates a new issue.
    """
    if job.jira_key and job.action in ("create", "link"):
        if job.action == "link":
            await link_ticket(session, job, client, job.jira_key)
        else:
            await create_ticket(session, job, client)
        return job.jira_key, job.action

    verdict = await find_duplicate(job.payload["kind"], job.payload.get("fields", {}), client=client, model=model)
    if verdict.match_key:
        await link_ticket(session, job, client, verdict.match_key)
        return verdict.match_key, "link"
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
    body = messages.outcome_for(job.payload["kind"], action)
    if action == "create":
        await deliver_result(session, job, "ticket_created", "Ticket created", body, key)
    else:
        await deliver_result(session, job, "ticket_linked", "Linked to existing", body, key)
    return True
