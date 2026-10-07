from __future__ import annotations

import pytest

from core.retry import retry_async


@pytest.mark.asyncio
async def test_retry_succeeds():
    calls = {"n": 0}

    async def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("boom")
        return "ok"

    result = await retry_async(flaky, attempts=5, base_delay=0.01, label="t")
    assert result == "ok"
    assert calls["n"] == 3
