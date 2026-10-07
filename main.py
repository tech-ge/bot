"""
techgeo — multi-account social media bot entry point.
"""
from __future__ import annotations

import asyncio
import signal
import sys
from typing import NoReturn

from loguru import logger

from config.settings import settings
from config.logging_setup import setup_logging
from core.bot import BotManager


async def _run() -> None:
    setup_logging()
    logger.info("Starting techgeo ({env})", env=settings.env)

    manager = BotManager(settings=settings)
    await manager.load_accounts()
    await manager.start()

    stop_event = asyncio.Event()

    def _handle_signal(sig: int) -> None:
        logger.warning("Received signal {sig}, shutting down...", sig=sig)
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _handle_signal, sig)
        except NotImplementedError:
            signal.signal(sig, lambda s, _f: _handle_signal(s))

    try:
        await stop_event.wait()
    finally:
        await manager.stop()
        logger.info("techgeo stopped cleanly.")


def main() -> NoReturn:
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt — exiting.")
    sys.exit(0)


if __name__ == "__main__":
    main()
