"""Async task queue (in-process) with concurrency cap + graceful drain."""
from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable

from loguru import logger

Task = Callable[..., Awaitable[Any]]


class TaskQueue:
    def __init__(self, *, max_concurrency: int = 10) -> None:
        self._queue: asyncio.Queue[tuple[Task, tuple[Any, ...], dict[str, Any]]] = (
            asyncio.Queue()
        )
        self._sem = asyncio.Semaphore(max_concurrency)
        self._workers: list[asyncio.Task[None]] = []
        self._running = False

    async def _worker(self, wid: int) -> None:
        logger.debug("Worker {id} started", id=wid)
        while self._running:
            try:
                fn, args, kwargs = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            async with self._sem:
                try:
                    await fn(*args, **kwargs)
                except Exception as exc:
                    logger.exception("Task failed: {e}", e=exc)
                finally:
                    self._queue.task_done()
        logger.debug("Worker {id} stopped", id=wid)

    async def start(self, workers: int = 4) -> None:
        self._running = True
        for i in range(workers):
            self._workers.append(asyncio.create_task(self._worker(i)))

    async def submit(
        self,
        fn: Task,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        await self._queue.put((fn, args, kwargs))

    async def stop(self, drain: bool = True) -> None:
        if drain:
            await self._queue.join()
        self._running = False
        for w in self._workers:
            w.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
