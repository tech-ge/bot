"""Retry helpers with exponential backoff + jitter."""
from __future__ import annotations

import asyncio
import random
from typing import Awaitable, Callable, TypeVar

from loguru import logger

T = TypeVar("T")


async def retry_async(
    fn: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    jitter: float = 0.3,
    retry_on: tuple[type[Exception], ...] = (Exception,),
    label: str = "task",
) -> T:
    last_exc: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return await fn()
        except retry_on as exc:
            last_exc = exc
            if attempt == attempts:
                break
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            delay += random.uniform(0, delay * jitter)
            logger.warning("[{l}] attempt {a}/{n} failed: {e} — retrying in {d:.2f}s",
                           l=label, a=attempt, n=attempts, e=exc, d=delay)
            await asyncio.sleep(delay)
    assert last_exc is not None
    raise last_exc
