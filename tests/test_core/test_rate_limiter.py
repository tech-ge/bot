from __future__ import annotations

import pytest

from core.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_acquire():
    rl = RateLimiter()
    rl.configure("acc", "action", capacity=2, refill_per_sec=1000)
    await rl.acquire("acc", "action")
    await rl.acquire("acc", "action")
