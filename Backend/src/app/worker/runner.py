"""Worker poll loop that drains the job queue."""

import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.db.models import Job
from app.jira.client import JiraClient
from app.worker.notify import deliver_result
from app.worker.processor import process_job
from app.worker.queue import claim_next_job, fail_job


async def _process_claimed_job(maker, job_id: str, client, model=None) -> str | None:
    """Process a claimed job in its own session; return an error message on failure.

    A dedicated session means a processing rollback cannot lose the job's already
    committed claimed/locked state.
    """
    async with maker() as session:
        job = (await session.execute(select(Job).where(Job.id == job_id))).scalar_one()
        try:
            await process_job(session, job, client, model=model)
            await session.commit()
        except Exception as error:  # noqa: BLE001 - one bad job must not crash the worker
            await session.rollback()
            return str(error)
    return None


async def _record_failure(maker, job_id: str, error_text: str) -> None:
    """Record a failed attempt; emit a ticket_failed notification once attempts hit the cap."""
    async with maker() as session:
        await fail_job(session, job_id, error_text)
        job = (await session.execute(select(Job).where(Job.id == job_id))).scalar_one()
        if job.status == "failed":
            await deliver_result(
                session, job, "ticket_failed", "Ticket creation failed",
                "We couldn't create your ticket. Please contact support.", None,
            )
        await session.commit()


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

    error_text = await _process_claimed_job(maker, job_id, client, model=model)
    if error_text is not None:
        await _record_failure(maker, job_id, error_text)
    return True


async def run_forever(poll_interval: float = 2.0) -> None:
    """Continuously drain the queue; sleep briefly when idle."""
    engine = create_async_engine(get_settings().database_url)
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    client = JiraClient()
    worker_id = f"worker-{uuid.uuid4().hex[:8]}"
    while True:
        handled = await run_one(maker, client, worker_id)
        if not handled:
            await asyncio.sleep(poll_interval)
