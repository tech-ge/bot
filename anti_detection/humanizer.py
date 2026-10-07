"""Human-like delays, jitter, and pacing."""
from __future__ import annotations

import asyncio
import random

from loguru import logger

from config.settings import settings


class Humanizer:
    def __init__(
        self,
        min_delay: float | None = None,
        max_delay: float | None = None,
    ) -> None:
        env = settings.env_settings
        self.min_delay = min_delay if min_delay is not None else env.humanize_min_delay
        self.max_delay = max_delay if max_delay is not None else env.humanize_max_delay
        if self.min_delay > self.max_delay:
            self.min_delay, self.max_delay = self.max_delay, self.min_delay

    def delay_seconds(self) -> float:
        base = random.uniform(self.min_delay, self.max_delay)
        jitter = base * random.uniform(-0.15, 0.15)
        return max(0.1, base + jitter)

    async def sleep(self) -> None:
        d = self.delay_seconds()
        logger.debug("Humanizer sleeping {d:.2f}s", d=d)
        await asyncio.sleep(d)

    async def between_actions(self, count: int = 1) -> None:
        for _ in range(count):
            await self.sleep()


humanizer = Humanizer()
