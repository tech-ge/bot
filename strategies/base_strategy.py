"""Base class for all strategies."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from anti_detection.humanizer import humanizer


class BaseStrategy(ABC):
    name: str = "base"

    def __init__(self, bot: Any) -> None:
        self.bot = bot
        self.log = logger.bind(account=bot.id, strategy=self.name)

    @abstractmethod
    async def run_once(self) -> None:
        ...

    async def safe_run(self) -> None:
        try:
            await self.bot.breaker.wait_if_paused(self.bot.id)
            await self.run_once()
        except Exception as exc:
            self.log.exception("Strategy {n} failed: {e}", n=self.name, e=exc)
            await self.bot.breaker.record_warning(self.bot.id, reason=self.name)

    async def cool_down(self) -> None:
        await humanizer.sleep()
