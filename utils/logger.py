"""Thin loguru helper for module-scoped loggers."""
from __future__ import annotations

from loguru import logger


def get_logger(name: str):
    return logger.bind(module=name)
