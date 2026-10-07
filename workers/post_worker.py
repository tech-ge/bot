"""Celery tasks for scheduled posting."""
from __future__ import annotations

import asyncio
from typing import Any

from loguru import logger

from workers.celery_app import celery_app


def _run(coro: Any) -> Any:
    return asyncio.get_event_loop().run_until_complete(coro)


@celery_app.task(name="workers.post_worker.post_now")
def post_now(account_id: str, content: str,
             media: list[str] | None = None) -> dict[str, Any]:
    logger.info("post_now task for {a}", a=account_id)
    # Full wiring happens through BotManager in the main app;
    # this is a stub for external triggering.
    return {"account_id": account_id, "content_len": len(content),
            "media": media or [], "queued": True}
