"""Worker poll loop that drains the job queue."""

import asyncio
import logging
import time
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.db.models import Job
from app.db.notifications import purge_expired
from app.db.repositories import list_evidence_holding_conversation_ids
from app.evidence.storage import delete_dir, sweep_orphans
from app.jira.client import JiraClient
from app.worker.notify import deliver_result
from app.worker.outcome import TICKET_FAILED
from app.worker.processor import process_job
from app.worker.queue import claim_next_job, fail_job, find_stale_jobs

logger = logging.getLogger(__name__)

LEASE_SECONDS = 600.0
REAP_INTERVAL_SECONDS = 60.0
SWEEP_INTERVAL_SECONDS = 3600.0
PURGE_INTERVAL_SECONDS = 3600.0


async def _process_claimed_job(maker, job_id: str, worker_id: str, client, model=None) -> str | None:
    """Process a claimed job in its own session; return an error message on failure.

    A dedicated session means a processing rollback cannot lose the job's already
    committed claimed/locked state. Evidence files are removed only once the commit has
    succeeded, so a job that is rolled back and retried still has them.

    A job whose lease was reaped mid-flight is rolled back and reported as neither success
    nor failure: it now belongs to another worker, so recording an attempt against it here
    would spend one of somebody else's retries.
    """
    async with maker() as session:
        job = (await session.execute(select(Job).where(Job.id == job_id))).scalar_one()
        try:
            completed = await process_job(session, job, client, model=model, worker_id=worker_id)
            if not completed:
                await session.rollback()
                logger.warning("job %s lost its lease mid-flight; left to its new owner", job_id)
                return None
            await session.commit()
        except Exception as error:  # noqa: BLE001
            await session.rollback()
            return str(error)
        delete_dir(job.user_sub, job.conversation_id)
    return None


async def _record_attempt_failure(session, job_id: str, error_text: str) -> None:
    """Record a failed attempt in the caller's transaction; notify once attempts hit the cap."""
    await fail_job(session, job_id, error_text)
    job = (await session.execute(select(Job).where(Job.id == job_id))).scalar_one()
    if job.status == "failed":
        await deliver_result(
            session, job, "ticket_failed", "Ticket creation failed", TICKET_FAILED, None,
        )


async def _record_failure(maker, job_id: str, error_text: str) -> None:
    """Record a failed attempt in its own session."""
    async with maker() as session:
        await _record_attempt_failure(session, job_id, error_text)
        await session.commit()


async def reap_stale_jobs(maker, lease_seconds: float = LEASE_SECONDS) -> int:
    """Return jobs abandoned by a dead worker to the queue; return how many were reaped.

    A worker that dies mid-job never clears its lock, so the row stays running and
    ``claim_next_job`` skips it forever, locking that conversation's chat input for
    good. Each expiry is recorded as an ordinary failed attempt, so a job that keeps
    killing its worker walks the attempt counter up and eventually fails for real
    instead of being requeued in a loop.

    Finding the stale rows and recording their failures share one transaction. The row
    locks find_stale_jobs takes are held until it commits, so a second reaper cannot read
    the same attempts value and overwrite this one's increment.
    """
    async with maker() as session:
        stale = await find_stale_jobs(session, lease_seconds)
        for job_id in stale:
            await _record_attempt_failure(session, job_id, "worker lease expired")
        await session.commit()
    if stale:
        logger.warning("reaped %s stale job(s): %s", len(stale), ", ".join(stale))
    return len(stale)


async def _sweep_evidence(maker) -> int:
    """Sweep orphaned evidence directories, keeping those still in use; return how many.

    The keep set is read from the database on every pass rather than cached, so a report
    confirmed between two sweeps is protected by the next one.
    """
    async with maker() as session:
        keep = await list_evidence_holding_conversation_ids(session)
    return sweep_orphans(keep_conversation_ids=keep)


async def _purge_notifications(maker) -> int:
    """Delete notifications past the retention window; return how many were removed.

    Retention is enforced regardless of read state, so a notification the user never
    opened is still removed once it ages out.
    """
    async with maker() as session:
        removed = await purge_expired(session)
        await session.commit()
    return removed


async def run_one(maker, client, worker_id: str, model=None) -> bool:
    """Claim and process one job; record failure on error. Return whether a job was handled.

    Claim, process, and failure-recording each run in their own session so a rollback
    in one phase cannot undo another.
    """
    async with maker() as session:
        claimed = await claim_next_job(session, worker_id)
        await session.commit()
        if claimed is None:
            return False
        job_id = claimed.id

    error_text = await _process_claimed_job(maker, job_id, worker_id, client, model=model)
    if error_text is not None:
        await _record_failure(maker, job_id, error_text)
    return True


async def run_forever(poll_interval: float = 2.0) -> None:
    """Continuously drain the queue; sleep briefly when idle.

    Three periodic chores run alongside the drain: expired job leases are reaped,
    evidence directories orphaned by abandoned conversations are swept, and notifications
    past their retention window are purged. None may abort the loop, so all three swallow
    their failures. LEASE_SECONDS must stay
    comfortably above the worst-case job duration -- dedupe, issue creation, and an
    attachment upload bounded by JiraClient._UPLOAD_TIMEOUT -- or a healthy long job is
    reaped mid-flight and re-claimed by another worker. The completion fence keeps that
    from being reported twice, but it still costs the job one of its attempts, so the
    lease is a margin to size generously rather than a correctness backstop.
    """
    engine = create_async_engine(get_settings().database_url)
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    client = JiraClient()
    worker_id = f"worker-{uuid.uuid4().hex[:8]}"
    next_reap = 0.0
    next_sweep = 0.0
    next_purge = 0.0
    while True:
        if time.monotonic() >= next_reap:
            next_reap = time.monotonic() + REAP_INTERVAL_SECONDS
            try:
                await reap_stale_jobs(maker)
            except Exception as error:  # noqa: BLE001
                logger.warning("stale-job sweep failed: %s", error)
        if time.monotonic() >= next_sweep:
            next_sweep = time.monotonic() + SWEEP_INTERVAL_SECONDS
            try:
                removed = await _sweep_evidence(maker)
                if removed:
                    logger.info("swept %s orphaned evidence director%s", removed, "y" if removed == 1 else "ies")
            except Exception as error:  # noqa: BLE001
                logger.warning("evidence sweep failed: %s", error)
        if time.monotonic() >= next_purge:
            next_purge = time.monotonic() + PURGE_INTERVAL_SECONDS
            try:
                purged = await _purge_notifications(maker)
                if purged:
                    logger.info("purged %s expired notification(s)", purged)
            except Exception as error:  # noqa: BLE001
                logger.warning("notification purge failed: %s", error)
        handled = await run_one(maker, client, worker_id)
        if not handled:
            await asyncio.sleep(poll_interval)
