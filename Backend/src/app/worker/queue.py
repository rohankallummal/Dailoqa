"""Postgres-backed job queue operations for the ticket worker."""

from datetime import datetime, timezone

from sqlalchemy import select, update

from app.db.models import Job


async def claim_next_job(session, worker_id: str) -> Job | None:
    """Claim the oldest queued job with FOR UPDATE SKIP LOCKED; mark it running."""
    stmt = (
        select(Job)
        .where(Job.status == "queued")
        .order_by(Job.created_at)
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    job = (await session.execute(stmt)).scalar_one_or_none()
    if job is None:
        return None
    job.status = "running"
    job.locked_at = datetime.now(timezone.utc)
    job.locked_by = worker_id
    await session.flush()
    return job


async def set_job_action(session, job_id: str, action: str, jira_key: str | None = None) -> None:
    """Persist the resolved action (and jira_key) as the resume anchor."""
    values = {"action": action}
    if jira_key is not None:
        values["jira_key"] = jira_key
    await session.execute(update(Job).where(Job.id == job_id).values(**values))


async def complete_job(session, job_id: str) -> None:
    """Mark a job succeeded."""
    await session.execute(update(Job).where(Job.id == job_id).values(status="succeeded"))


async def fail_job(session, job_id: str, error: str, max_attempts: int = 5) -> None:
    """Record a failure; requeue with incremented attempts, or mark failed at the cap."""
    job = (await session.execute(select(Job).where(Job.id == job_id))).scalar_one()
    job.attempts = (job.attempts or 0) + 1
    job.last_error = error
    if job.attempts >= max_attempts:
        job.status = "failed"
    else:
        job.status = "queued"
        job.locked_at = None
        job.locked_by = None
    await session.flush()
