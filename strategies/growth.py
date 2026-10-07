"""Growth strategy — daily budget tracking for follows/likes."""
from __future__ import annotations

import time
from typing import Any

from strategies.base_strategy import BaseStrategy


class GrowthStrategy(BaseStrategy):
    name = "growth"

    def __init__(self, bot: Any, daily_follow_budget: int = 20,
                 daily_like_budget: int = 100) -> None:
        super().__init__(bot)
        self.daily_follow_budget = daily_follow_budget
        self.daily_like_budget = daily_like_budget
        self._day = self._today()
        self._follows = 0
        self._likes = 0

    def _today(self) -> str:
        return time.strftime("%Y-%m-%d", time.gmtime())

    def _rollover(self) -> None:
        d = self._today()
        if d != self._day:
            self._day = d
            self._follows = 0
            self._likes = 0

    async def run_once(self) -> None:
        self._rollover()
        if self._follows >= self.daily_follow_budget and \
           self._likes >= self.daily_like_budget:
            self.log.debug("Daily budgets reached")
            return
        self.log.debug("Growth tick (follows {f}/{fb}, likes {l}/{lb})",
                       f=self._follows, fb=self.daily_follow_budget,
                       l=self._likes, lb=self.daily_like_budget)
        await self.cool_down()
