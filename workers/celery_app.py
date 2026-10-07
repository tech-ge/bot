"""Celery app for techgeo background jobs."""
from __future__ import annotations

from celery import Celery

from config.settings import settings

celery_app = Celery(
    "techgeo",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "workers.post_worker",
        "workers.engagement_worker",
        "workers.listener_worker",
        "workers.cleanup_worker",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
