"""Celery tasks for engagement loops."""
from __future__ import annotations

from typing import Any

from loguru import logger

from workers.celery_app import celery_app


@celery_app.task(name="workers.engagement_worker.tick")
def tick(account_id: str) -> dict[str, Any]:
    logger.debug("engagement tick for {a}", a=account_id)
    return {"account_id": account_id, "ticked": True}
