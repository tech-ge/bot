"""Cross-post the same content to multiple bots (respecting isolation)."""
from __future__ import annotations

from typing import Any, Iterable

from copyright_guard.output_checker import OutputChecker
from strategies.base_strategy import BaseStrategy


class CrossPostStrategy(BaseStrategy):
    name = "cross_post"

    def __init__(
        self,
        bot: Any,
        peers: Iterable[Any] | None = None,
        *,
        content: str | None = None,
        media: list[str] | None = None,
    ) -> None:
        super().__init__(bot)
        self.peers = list(peers or [])
        self.content = content or ""
        self.media = media or []
        self.output_checker = OutputChecker()

    async def run_once(self) -> None:
        if not self.content:
            self.log.debug("No content to cross-post")
            return
        out = self.output_checker.check(self.content)
        if not out.ok:
            self.log.warning("Cross-post rejected: {r}", r=out.reason)
            return

        targets = [self.bot, *self.peers]
        for target in targets:
            try:
                result = await target.perform(
                    "post", content=self.content, media=self.media
                )
                self.log.info("Cross-posted to {id}: {r}",
                              id=target.id, r=result)
            except Exception as exc:
                self.log.warning("Cross-post to {id} failed: {e}",
                                 id=target.id, e=exc)
            await self.cool_down()
