from __future__ import annotations

from typing import Any, Awaitable, Callable

from loguru import logger

from platforms.base import PlatformAdapter
from platforms.snapchat.actions import SnapchatActions
from platforms.snapchat.api import SnapchatAPI


class SnapchatAdapter(PlatformAdapter):
    name = "snapchat"

    def __init__(self, bot: Any) -> None:
        super().__init__(bot)
        self.api: SnapchatAPI | None = None
        self.actions: SnapchatActions | None = None

    async def login(self) -> None:
        self.api = SnapchatAPI()
        self.actions = SnapchatActions(self.api)
        self._logger.warning("Snapchat organic automation is limited — Marketing API only")

    async def close(self) -> None:
        if self.api:
            await self.api.close()

    async def post(self, content: str, media: list[str] | None = None) -> dict[str, Any]:
        assert self.actions
        return await self.actions.post(content, media)

    async def reply(self, target_id: str, content: str) -> dict[str, Any]:
        assert self.actions
        return await self.actions.reply(target_id, content)

    async def dm(self, user_id: str, content: str) -> dict[str, Any]:
        assert self.actions
        return await self.actions.dm(user_id, content)

    async def like(self, target_id: str) -> dict[str, Any]:
        assert self.actions
        return await self.actions.like(target_id)

    async def follow(self, user_id: str) -> dict[str, Any]:
        assert self.actions
        return await self.actions.follow(user_id)

    async def listen(self, callback: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
        logger.info("Snapchat listener not implemented")
