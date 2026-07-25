"""Resume-aware orchestration of a single ticket-creation job."""

from app.agent.dedupe import find_duplicate
from app.worker.create_step import create_ticket
from app.worker.link_step import link_ticket
from app.worker.notify import deliver_result
from app.worker.queue import complete_job


async def _resolve_ticket(session, job, client, model) -> tuple[str, str]:
    """Return the (jira_key, action) for a job, resuming a prior run when anchored.

    A job already anchored with jira_key + action is resumed: the link side effect is
    re-applied idempotently, the create side effect is not repeated. A fresh job runs
    authoritative dedupe and either links to a match or creates a new issue.
    """
    if job.jira_key and job.action in ("create", "link"):
        if job.action == "link":
            await link_ticket(session, job, client, job.jira_key)
        return job.jira_key, job.action

    verdict = await find_duplicate(job.payload["kind"], job.payload.get("fields", {}), client=client, model=model)
    if verdict.match_key:
        await link_ticket(session, job, client, verdict.match_key)
        return verdict.match_key, "link"
    return await create_ticket(session, job, client), "create"


async def process_job(session, job, client, model=None) -> None:
    """Run one job to completion: dedupe (unless resuming) -> create/link -> notify."""
    key, action = await _resolve_ticket(session, job, client, model)
    if action == "create":
        await deliver_result(session, job, "ticket_created", "Ticket created", f"Created {key}.", key)
    else:
        await deliver_result(session, job, "ticket_linked", "Linked to existing", f"Linked your report to {key}.", key)
    await complete_job(session, job.id)
