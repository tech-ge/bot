"""Export cookies for all accounts to disk (JSON + PKL)."""
from __future__ import annotations

import asyncio

from loguru import logger

from config.logging_setup import setup_logging
from anti_detection.browser_launcher import BrowserSession


async def main() -> None:
    setup_logging()
    logger.info("Cookie export requires an active browser session per account.")
    # Example: create and persist a session for one account
    session = BrowserSession("ig_personal_01")
    try:
        await session.open(headless=True)
        await session.persist_cookies()
        logger.success("Cookies exported for ig_personal_01")
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(main())
