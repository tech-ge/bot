from __future__ import annotations

import asyncio
from typing import Any

from platforms.twitter.api import TwitterAPI


class TwitterActions:
    def __init__(self, api: TwitterAPI) -> None:
        self.api = api

    async def post(self, content: str, media: list[str] | None = None) -> dict[str, Any]:
        return await asyncio.to_thread(self.api.post_tweet, content)

    async def reply(self, target_id: str, content: str) -> dict[str, Any]:
        return await asyncio.to_thread(self.api.reply, target_id, content)

    async def dm(self, user_id: str, content: str) -> dict[str, Any]:
        return await asyncio.to_thread(self.api.dm, user_id, content)

    async def like(self, target_id: str) -> dict[str, Any]:
        return await asyncio.to_thread(self.api.like, target_id)

    async def follow(self, user_id: str) -> dict[str, Any]:
        return await asyncio.to_thread(self.api.follow, user_id)
