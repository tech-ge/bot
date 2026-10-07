"""Thin wrapper over APScheduler AsyncIOScheduler."""
from __future__ import annotations

from typing import Any, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from config.settings import settings


class Scheduler:
    def __init__(self) -> None:
        cfg = settings.get("scheduler", default={}) or {}
        job_defaults = cfg.get("job_defaults", {}) or {}
        self._sched = AsyncIOScheduler(
            timezone=cfg.get("timezone", "UTC"),
            job_defaults={
                "coalesce": job_defaults.get("coalesce", True),
                "max_instances": job_defaults.get("max_instances", 1),
                "misfire_grace_time": job_defaults.get("misfire_grace_time", 60),
            },
        )

    def start(self) -> None:
        if not self._sched.running:
            self._sched.start()
            logger.info("Scheduler started")

    def shutdown(self, wait: bool = False) -> None:
        if self._sched.running:
            self._sched.shutdown(wait=wait)
            logger.info("Scheduler stopped")

    def add_interval(
        self,
        fn: Callable[..., Any],
        *,
        seconds: int | None = None,
        minutes: int | None = None,
        hours: int | None = None,
        job_id: str | None = None,
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
    ) -> str:
        trigger = IntervalTrigger(
            seconds=seconds or 0,
            minutes=minutes or 0,
            hours=hours or 0,
        )
        job = self._sched.add_job(
            fn,
            trigger=trigger,
            id=job_id,
            args=args,
            kwargs=kwargs or {},
            replace_existing=True,
        )
        logger.debug("Scheduled job {id}", id=job.id)
        return job.id

    def remove(self, job_id: str) -> None:
        try:
            self._sched.remove_job(job_id)
        except Exception:
            pass


scheduler = Scheduler()
