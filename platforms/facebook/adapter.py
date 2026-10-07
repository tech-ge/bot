from __future__ import annotations

from typing import Any, Awaitable, Callable

from loguru import logger

from platforms.base import PlatformAdapter
from platforms.facebook.actions import FacebookActions
from platforms.facebook.api import FacebookAPI


class FacebookAdapter(PlatformAdapter):
    name = "facebook"

    def __init__(self, bot: Any) -> None:
        super().__init__(bot)
        self.api: FacebookAPI | None = None
        self.actions: FacebookActions | None = None

    async def login(self) -> None:
        self.api = FacebookAPI()
        self.actions = FacebookActions(self.api)
        self._logger.info("Facebook adapter ready for {u}", u=self.username)

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
        logger.info("Facebook listener requires webhook setup (see webhooks/)")
