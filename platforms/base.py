"""Abstract PlatformAdapter — every network implements this."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable

from loguru import logger


class PlatformAdapter(ABC):
    name: str = "base"

    def __init__(self, bot: Any) -> None:
        self.bot = bot
        self.account_id: str = bot.id
        self.username: str = bot.username
        self._logger = logger.bind(account=bot.id, platform=self.name)

    # ----- lifecycle -----
    @abstractmethod
    async def login(self) -> None:
        ...

    async def close(self) -> None:
        return None

    # ----- actions -----
    @abstractmethod
    async def post(self, content: str, media: list[str] | None = None) -> dict[str, Any]:
        ...

    @abstractmethod
    async def reply(self, target_id: str, content: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def dm(self, user_id: str, content: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def like(self, target_id: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def follow(self, user_id: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def listen(self, callback: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
        ...

    # ----- optional: inbox for auto-reply strategies -----
    async def fetch_inbox(self) -> list[dict[str, Any]]:
        """Return pending inbound messages. Override per platform."""
        return []
