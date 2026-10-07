"""Auto-reply strategy for inbound mentions/messages."""
from __future__ import annotations

from typing import Any

from ai.intent import classify
from content.generator import content_generator
from copyright_guard.output_checker import OutputChecker
from strategies.base_strategy import BaseStrategy


class AutoReplyStrategy(BaseStrategy):
    name = "auto_reply"

    def __init__(
        self,
        bot: Any,
        keywords: list[str] | None = None,
        max_replies: int = 10,
    ) -> None:
        super().__init__(bot)
        self.keywords = [k.lower() for k in (keywords or [])]
        self.max_replies = max_replies
        self.output_checker = OutputChecker()
        self._replied: set[str] = set()

    def _matches(self, text: str) -> bool:
        if not self.keywords:
            return True
        t = text.lower()
        return any(k in t for k in self.keywords)

    async def run_once(self) -> None:
        inbox: list[dict[str, Any]] = await self._fetch_inbox()
        count = 0
        for item in inbox:
            if count >= self.max_replies:
                break
            target_id = str(item.get("id", ""))
            text = str(item.get("text", ""))
            if not target_id or target_id in self._replied:
                continue
            if not self._matches(text):
                continue

            intent = classify(text)
            reply_text = await content_generator.generate_reply(text)
            out = self.output_checker.check(reply_text)
            if not out.ok:
                self.log.warning("Reply rejected: {r}", r=out.reason)
                continue

            try:
                await self.bot.perform("reply", target_id=target_id,
                                       content=reply_text)
                self._replied.add(target_id)
                count += 1
                self.log.info("Replied to {t} (intent={i})",
                              t=target_id, i=intent.name)
            except Exception:
                continue
            await self.cool_down()

    async def _fetch_inbox(self) -> list[dict[str, Any]]:
        adapter = getattr(self.bot, "_adapter", None)
        if adapter is None or not hasattr(adapter, "fetch_inbox"):
            return []
        try:
            return await adapter.fetch_inbox()
        except Exception as exc:
            self.log.warning("fetch_inbox failed: {e}", e=exc)
            return []
