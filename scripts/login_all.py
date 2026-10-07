"""One-time login for every enabled account, then persist cookies."""
from __future__ import annotations

import asyncio

from loguru import logger

from config.logging_setup import setup_logging
from core.bot import BotManager
from config.settings import settings


async def main() -> None:
    setup_logging()
    mgr = BotManager(settings=settings)
    await mgr.load_accounts()
    for acc in mgr.accounts:
        try:
            await acc.start()
        except Exception as exc:
            logger.exception("Login failed for {id}: {e}", id=acc.id, e=exc)
        finally:
            await acc.stop()


if __name__ == "__main__":
    asyncio.run(main())
