"""InstagramAdapter — wires API + actions into PlatformAdapter."""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from loguru import logger

from platforms.base import PlatformAdapter
from platforms.instagram.actions import InstagramActions
from platforms.instagram.api import InstagramAPI


class InstagramAdapter(PlatformAdapter):
    name = "instagram"

    def __init__(self, bot: Any) -> None:
        super().__init__(bot)
        self.api: InstagramAPI | None = None
        self.actions: InstagramActions | None = None
        self.ig_user_id = "me"  # or resolved on login

    async def login(self) -> None:
        self.api = InstagramAPI(self.username)
        self.actions = InstagramActions(self.api, self.ig_user_id)
        self._logger.info("Instagram adapter ready for {u}", u=self.username)

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
        logger.info("Instagram listener not yet implemented")
