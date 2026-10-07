"""Engagement loop: like/follow a bounded, random subset of targets."""
from __future__ import annotations

import random
from typing import Any

from strategies.base_strategy import BaseStrategy


class EngagementStrategy(BaseStrategy):
    name = "engagement"

    def __init__(
        self,
        bot: Any,
        targets: list[str] | None = None,
        *,
        likes_per_run: int = 5,
        follows_per_run: int = 2,
    ) -> None:
        super().__init__(bot)
        self.targets = targets or []
        self.likes_per_run = likes_per_run
        self.follows_per_run = follows_per_run

    async def run_once(self) -> None:
        if not self.targets:
            self.log.debug("No targets configured")
            return

        picks = random.sample(self.targets,
                              k=min(len(self.targets), self.likes_per_run))
        for tid in picks:
            try:
                await self.bot.perform("like", target_id=tid)
                self.log.debug("Liked {t}", t=tid)
            except Exception:
                pass
            await self.cool_down()

        follow_picks = random.sample(
            self.targets, k=min(len(self.targets), self.follows_per_run)
        )
        for uid in follow_picks:
            try:
                await self.bot.perform("follow", user_id=uid)
                self.log.debug("Followed {u}", u=uid)
            except Exception:
                pass
            await self.cool_down()
