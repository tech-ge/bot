"""Per-account token-bucket rate limiter."""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field

from loguru import logger


@dataclass
class Bucket:
    capacity: int
    refill_per_sec: float
    tokens: float = field(init=False)
    last_refill: float = field(init=False)

    def __post_init__(self) -> None:
        self.tokens = float(self.capacity)
        self.last_refill = time.monotonic()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_sec)
        self.last_refill = now

    def try_consume(self, n: float = 1.0) -> bool:
        self._refill()
        if self.tokens >= n:
            self.tokens -= n
            return True
        return False

    def wait_time(self, n: float = 1.0) -> float:
        self._refill()
        if self.tokens >= n:
            return 0.0
        deficit = n - self.tokens
        return deficit / self.refill_per_sec if self.refill_per_sec > 0 else float("inf")


class RateLimiter:
    """Manages buckets per (account_id, action)."""

    def __init__(self) -> None:
        self._buckets: dict[tuple[str, str], Bucket] = {}
        self._lock = asyncio.Lock()

    def configure(
        self,
        account_id: str,
        action: str,
        *,
        capacity: int,
        refill_per_sec: float,
    ) -> None:
        self._buckets[(account_id, action)] = Bucket(
            capacity=capacity, refill_per_sec=refill_per_sec
        )

    async def acquire(self, account_id: str, action: str) -> None:
        key = (account_id, action)
        async with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                # default: 20/min
                bucket = Bucket(capacity=20, refill_per_sec=20 / 60)
                self._buckets[key] = bucket

        while True:
            async with self._lock:
                if bucket.try_consume(1):
                    return
                wait = bucket.wait_time(1)
            logger.debug("Rate limit hit for {a}/{act}; sleeping {w:.2f}s",
                         a=account_id, act=action, w=wait)
            await asyncio.sleep(max(wait, 0.1))


rate_limiter = RateLimiter()
