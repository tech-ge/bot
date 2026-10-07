"""Telegram Bot API wrapper (aiogram)."""
from __future__ import annotations

from typing import Any

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.settings import settings


class TelegramAPI:
    def __init__(self, token: str) -> None:
        self.token = token
        self.bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

    async def close(self) -> None:
        await self.bot.session.close()

    async def send_message(self, chat_id: str, text: str) -> dict[str, Any]:
        msg = await self.bot.send_message(chat_id=chat_id, text=text)
        return {"message_id": msg.message_id, "chat_id": str(msg.chat.id)}

    async def reply(self, chat_id: str, reply_to: int, text: str) -> dict[str, Any]:
        msg = await self.bot.send_message(
            chat_id=chat_id, text=text, reply_to_message_id=reply_to
        )
        return {"message_id": msg.message_id}

    async def like(self, *_a: Any, **_kw: Any) -> dict[str, Any]:
        return {"ok": False, "reason": "telegram_has_no_likes"}

    async def follow(self, *_a: Any, **_kw: Any) -> dict[str, Any]:
        return {"ok": False, "reason": "telegram_has_no_follow"}
