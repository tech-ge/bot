"""Long-running listeners (streams, webhooks)."""
from __future__ import annotations

import asyncio
from typing import Any

from loguru import logger


class ListenerWorker:
    def __init__(self, name: str) -> None:
        self.name = name
        self._task: asyncio.Task[None] | None = None

    async def _loop(self) -> None:
        logger.info("Listener {n} started", n=self.name)
        while True:
            try:
                await asyncio.sleep(5)
                # hook: fetch and dispatch inbound events
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.exception("Listener {n} error: {e}", n=self.name, e=exc)

    def start(self) -> None:
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except Exception:
                pass


def spawn(name: str) -> ListenerWorker:
    w = ListenerWorker(name)
    w.start()
    return w
