"""Circuit breaker to auto-pause an account on warning signals."""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field

from loguru import logger


@dataclass
class BreakerState:
    trips_today: int = 0
    paused_until: float = 0.0
    last_trip_day: str = ""
    warnings: int = 0


class CircuitBreaker:
    def __init__(
        self,
        *,
        warning_threshold: int = 1,
        pause_minutes: int = 45,
        max_trips_per_day: int = 3,
    ) -> None:
        self.warning_threshold = warning_threshold
        self.pause_minutes = pause_minutes
        self.max_trips_per_day = max_trips_per_day
        self._states: dict[str, BreakerState] = {}
        self._lock = asyncio.Lock()

    def _today(self) -> str:
        return time.strftime("%Y-%m-%d", time.gmtime())

    async def _state(self, account_id: str) -> BreakerState:
        async with self._lock:
            st = self._states.setdefault(account_id, BreakerState())
            if st.last_trip_day != self._today():
                st.trips_today = 0
                st.last_trip_day = self._today()
            return st

    async def record_warning(self, account_id: str, reason: str = "") -> None:
        st = await self._state(account_id)
        st.warnings += 1
        logger.warning("Warning for {a} ({n}/{t}): {r}",
                       a=account_id, n=st.warnings,
                       t=self.warning_threshold, r=reason)
        if st.warnings >= self.warning_threshold:
            await self.trip(account_id, reason=reason)

    async def trip(self, account_id: str, reason: str = "") -> None:
        st = await self._state(account_id)
        if st.trips_today >= self.max_trips_per_day:
            logger.error("Circuit breaker for {a} exceeded daily cap — refusing",
                         a=account_id)
            return
        st.trips_today += 1
        st.warnings = 0
        st.paused_until = time.monotonic() + self.pause_minutes * 60
        logger.error("Circuit TRIP for {a}: paused {m} min ({r})",
                     a=account_id, m=self.pause_minutes, r=reason)

    async def is_paused(self, account_id: str) -> bool:
        st = await self._state(account_id)
        if st.paused_until and time.monotonic() < st.paused_until:
            return True
        return False

    async def wait_if_paused(self, account_id: str) -> None:
        st = await self._state(account_id)
        while st.paused_until and time.monotonic() < st.paused_until:
            remaining = st.paused_until - time.monotonic()
            logger.info("{a} paused; sleeping {r:.1f}s", a=account_id, r=remaining)
            await asyncio.sleep(min(remaining, 30))
        st.paused_until = 0.0

    async def reset(self, account_id: str) -> None:
        async with self._lock:
            self._states[account_id] = BreakerState()
