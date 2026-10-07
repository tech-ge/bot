"""Lightweight async event bus for internal signaling."""
from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any, Awaitable, Callable

from loguru import logger

Handler = Callable[..., Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def subscribe(self, event: str, handler: Handler) -> None:
        async with self._lock:
            self._handlers[event].append(handler)
            logger.debug("Subscribed {h} to event '{e}'",
                         h=handler.__qualname__, e=event)

    async def unsubscribe(self, event: str, handler: Handler) -> None:
        async with self._lock:
            if handler in self._handlers[event]:
                self._handlers[event].remove(handler)

    async def publish(self, event: str, **payload: Any) -> None:
        handlers = list(self._handlers.get(event, []))
        if not handlers:
            return
        results = await asyncio.gather(
            *(h(**payload) for h in handlers),
            return_exceptions=True,
        )
        for h, r in zip(handlers, results):
            if isinstance(r, Exception):
                logger.exception("Event handler {h} failed: {err}",
                                 h=h.__qualname__, err=r)


bus = EventBus()
