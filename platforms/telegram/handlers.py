"""Telegram command/message handlers."""
from __future__ import annotations

from typing import Any

from aiogram import Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru import logger


def register(dp: Dispatcher, bot_id: str) -> None:
    @dp.message(CommandStart())
    async def _start(message: Message) -> None:
        await message.answer(f"techgeo bot {bot_id} online.")

    @dp.message(F.text)
    async def _echo(message: Message) -> None:
        logger.debug("[{b}] msg from {u}: {t}",
                     b=bot_id, u=message.from_user.id if message.from_user else "?",
                     t=message.text)
