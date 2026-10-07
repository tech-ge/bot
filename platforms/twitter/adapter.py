from __future__ import annotations

from typing import Any, Awaitable, Callable

from loguru import logger

from platforms.base import PlatformAdapter
from platforms.twitter.actions import TwitterActions
from platforms.twitter.api import TwitterAPI


class TwitterAdapter(PlatformAdapter):
    name = "twitter"

    def __init__(self, bot: Any) -> None:
        super().__init__(bot)
        self.api: TwitterAPI | None = None
        self.actions: TwitterActions | None = None

    async def login(self) -> None:
        self.api = TwitterAPI()
        self.actions = TwitterActions(self.api)
        self._logger.info("Twitter adapter ready for {u}", u=self.username)

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
        from platforms.twitter.stream import TwitterStream
        stream = TwitterStream()
        import asyncio
        await asyncio.to_thread(stream.start, callback)
