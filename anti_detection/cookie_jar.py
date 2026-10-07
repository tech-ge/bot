"""Per-account cookie storage (import/export for browser sessions)."""
from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

from loguru import logger

from config.settings import settings


class CookieJar:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or (
            settings.base_dir / settings.env_settings.cookie_dir
        )
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _pkl(self, account_id: str) -> Path:
        return self.base_dir / f"{account_id}.pkl"

    def _json(self, account_id: str) -> Path:
        return self.base_dir / f"{account_id}.json"

    def save(self, account_id: str, cookies: list[dict[str, Any]]) -> None:
        self._pkl(account_id).write_bytes(pickle.dumps(cookies))
        self._json(account_id).write_text(
            json.dumps(cookies, indent=2), encoding="utf-8"
        )
        logger.debug("Saved {n} cookies for {id}", n=len(cookies), id=account_id)

    def load(self, account_id: str) -> list[dict[str, Any]]:
        p = self._pkl(account_id)
        if p.exists():
            try:
                return pickle.loads(p.read_bytes())
            except Exception as exc:
                logger.warning("Failed to load pickled cookies for {id}: {e}",
                               id=account_id, e=exc)
        j = self._json(account_id)
        if j.exists():
            try:
                return json.loads(j.read_text(encoding="utf-8"))
            except Exception as exc:
                logger.warning("Failed to load JSON cookies for {id}: {e}",
                               id=account_id, e=exc)
        return []

    def exists(self, account_id: str) -> bool:
        return self._pkl(account_id).exists() or self._json(account_id).exists()

    def delete(self, account_id: str) -> None:
        for p in (self._pkl(account_id), self._json(account_id)):
            if p.exists():
                p.unlink()


cookie_jar = CookieJar()
