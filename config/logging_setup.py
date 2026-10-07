"""Loguru-based logging setup with stdlib bridge."""
from __future__ import annotations

import logging
import logging.config
import sys
from pathlib import Path

import yaml
from loguru import logger

from config.settings import settings

LOG_DIR = settings.base_dir / "logs"
LOGGING_YAML = settings.base_dir / "config" / "logging.yaml"


class _InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )
    logger.add(
        LOG_DIR / "app.log",
        level="DEBUG",
        rotation="10 MB",
        retention="14 days",
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )
    logger.add(
        LOG_DIR / "anti_detection.log",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        filter=lambda r: "anti_detection" in r["name"],
        enqueue=True,
    )

    if LOGGING_YAML.exists():
        with LOGGING_YAML.open("r", encoding="utf-8") as fh:
            config_dict = yaml.safe_load(fh) or {}
        logging.config.dictConfig(config_dict)

    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)

    for noisy in ("asyncio", "httpx", "httpcore", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
