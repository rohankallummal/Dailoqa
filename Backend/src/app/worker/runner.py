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


async def run_one(maker, client, worker_id: str, model=None) -> bool:
    """Claim and process one job; record failure on error. Return whether a job was handled.

    Processing runs in a fresh session so a processing rollback cannot lose the
    claimed/locked state; failure is recorded in yet another clean session, and a
    final failure (attempts at the cap) emits a ticket_failed notification.
    """
    async with maker() as session:
        claimed = await claim_next_job(session, worker_id)
        await session.commit()
        if claimed is None:
            return False
        job_id = claimed.id

    error_text: str | None = None
    async with maker() as session:
        job = (await session.execute(select(Job).where(Job.id == job_id))).scalar_one()
        try:
            await process_job(session, job, client, model=model)
            await session.commit()
        except Exception as error:  # noqa: BLE001 - one bad job must not crash the worker
            await session.rollback()
            error_text = str(error)

    if error_text is not None:
        async with maker() as session:
            await fail_job(session, job_id, error_text)
            job = (await session.execute(select(Job).where(Job.id == job_id))).scalar_one()
            if job.status == "failed":
                await deliver_result(
                    session, job, "ticket_failed", "Ticket creation failed",
                    "We couldn't create your ticket. Please contact support.", None,
                )
            await session.commit()
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
