from __future__ import annotations

from typing import Any

from platforms.telegram.api import TelegramAPI


class TelegramActions:
    def __init__(self, api: TelegramAPI, default_chat_id: str) -> None:
        self.api = api
        self.default_chat_id = default_chat_id

    async def post(self, content: str, media: list[str] | None = None) -> dict[str, Any]:
        return await self.api.send_message(self.default_chat_id, content)

    async def reply(self, target_id: str, content: str) -> dict[str, Any]:
        chat_id, _, msg_id = target_id.partition(":")
        return await self.api.reply(chat_id, int(msg_id or 0), content)

    async def dm(self, user_id: str, content: str) -> dict[str, Any]:
        return await self.api.send_message(user_id, content)

    async def like(self, target_id: str) -> dict[str, Any]:
        return await self.api.like()

    async def follow(self, user_id: str) -> dict[str, Any]:
        return await self.api.follow()
