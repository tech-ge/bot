from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import Dispatcher
from loguru import logger

from config.settings import settings
from platforms.base import PlatformAdapter
from platforms.telegram.actions import TelegramActions
from platforms.telegram.api import TelegramAPI
from platforms.telegram.handlers import register as register_handlers


class TelegramAdapter(PlatformAdapter):
    name = "telegram"

    def __init__(self, bot: Any) -> None:
        super().__init__(bot)
        self.api: TelegramAPI | None = None
        self.actions: TelegramActions | None = None
        self.dp: Dispatcher | None = None
        self.default_chat_id: str = str(bot.cfg.get("chat_id", "") or "")

    def _resolve_token(self) -> str:
        auth = self.bot.cfg.get("auth") or {}
        token_ref = auth.get("token_env") or self.bot.cfg.get("token_env") or ""
        env = settings.env_settings
        if token_ref and hasattr(env, token_ref):
            val = getattr(env, token_ref)
            if val:
                return val
        return env.tg_bot_token_01 or env.tg_bot_token_02 or ""

    async def login(self) -> None:
        token = self._resolve_token()
        if not token:
            raise RuntimeError(f"No Telegram token for account {self.account_id}")
        self.api = TelegramAPI(token)
        self.actions = TelegramActions(self.api, self.default_chat_id)
        self.dp = Dispatcher()
        register_handlers(self.dp, self.account_id)
        me = await self.api.bot.get_me()
        self._logger.info("Telegram bot ready: @{u}", u=me.username)

    async def close(self) -> None:
        if self.api:
            await self.api.close()

    async def post(self, content: str, media: list[str] | None = None) -> dict[str, Any]:
        if self.actions is None:
            raise RuntimeError("Telegram adapter not logged in")
        if not self.default_chat_id:
            logger.warning("Telegram post skipped: no chat_id for {id}",
                           id=self.account_id)
            return {"ok": False, "reason": "no_chat_id"}
        return await self.actions.post(content, media)

    async def reply(self, target_id: str, content: str) -> dict[str, Any]:
        if self.actions is None:
            raise RuntimeError("Telegram adapter not logged in")
        return await self.actions.reply(target_id, content)

    async def dm(self, user_id: str, content: str) -> dict[str, Any]:
        if self.actions is None:
            raise RuntimeError("Telegram adapter not logged in")
        return await self.actions.dm(user_id, content)

    async def like(self, target_id: str) -> dict[str, Any]:
        return {"ok": False, "reason": "telegram_has_no_likes"}

    async def follow(self, user_id: str) -> dict[str, Any]:
        return {"ok": False, "reason": "telegram_has_no_follow"}

    async def listen(self, callback: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
        if self.dp is None or self.api is None:
            logger.warning("Telegram listener skipped: not logged in")
            return
        import asyncio
        await asyncio.to_thread(self.api.bot.run_polling)  # type: ignore[arg-type]
