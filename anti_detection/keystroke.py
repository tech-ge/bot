"""Human-like typing / pasting helpers for browser automation."""
from __future__ import annotations

import asyncio
import random
from typing import Any

from loguru import logger


async def type_text(
    page: Any,
    selector: str,
    text: str,
    *,
    min_cps: float = 4.0,
    max_cps: float = 9.0,
) -> None:
    """Type char-by-char with variable speed."""
    await page.click(selector)
    for ch in text:
        await page.type(selector, ch, delay=0)
        await asyncio.sleep(random.uniform(1.0 / max_cps, 1.0 / min_cps))


async def paste_text(page: Any, selector: str, text: str) -> None:
    """
    Set clipboard-style value instantly (faster, avoids keystroke heuristics).
    Falls back to fill() if clipboard unavailable.
    """
    try:
        await page.evaluate(
            """([sel, val]) => {
                const el = document.querySelector(sel);
                if (!el) return;
                el.focus();
                el.value = val;
                el.dispatchEvent(new Event('input', {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true}));
            }""",
            [selector, text],
        )
    except Exception as exc:
        logger.debug("paste_text fallback to fill: {e}", e=exc)
        await page.fill(selector, text)


async def human_click(page: Any, selector: str) -> None:
    """Move mouse to element with a small random offset, then click."""
    box = await page.locator(selector).bounding_box()
    if not box:
        await page.click(selector)
        return
    x = box["x"] + box["width"] * random.uniform(0.3, 0.7)
    y = box["y"] + box["height"] * random.uniform(0.3, 0.7)
    await page.mouse.move(x, y, steps=random.randint(8, 20))
    await asyncio.sleep(random.uniform(0.05, 0.2))
    await page.mouse.click(x, y)


async def scroll_like_human(page: Any, amount: int | None = None) -> None:
    amount = amount or random.randint(200, 900)
    steps = random.randint(3, 8)
    for _ in range(steps):
        delta = amount // steps + random.randint(-30, 30)
        await page.mouse.wheel(0, delta)
        await asyncio.sleep(random.uniform(0.15, 0.5))
