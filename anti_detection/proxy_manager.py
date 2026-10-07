"""Sticky / rotating proxy manager. Reads proxies.yaml."""
from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from config.settings import settings


@dataclass
class Proxy:
    id: str
    url: str
    region: str = ""
    tags: list[str] | None = None

    def is_active(self) -> bool:
        return bool(self.url.strip())

    def to_playwright(self) -> dict[str, str]:
        from urllib.parse import urlparse
        p = urlparse(self.url)
        out: dict[str, str] = {"server": f"{p.scheme}://{p.hostname}:{p.port}"}
        if p.username:
            out["username"] = p.username
        if p.password:
            out["password"] = p.password
        return out


class ProxyManager:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (settings.base_dir / settings.env_settings.proxy_file)
        self._proxies: dict[str, Proxy] = {}
        self._assignments: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            logger.warning("No proxy file at {p} — running direct", p=self.path)
            return
        try:
            data = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            logger.exception("Failed to parse {p}: {e}", p=self.path, e=exc)
            return
        for item in data.get("proxies", []) or []:
            pid = item.get("id")
            if not pid:
                continue
            self._proxies[pid] = Proxy(
                id=pid,
                url=item.get("url", "") or "",
                region=item.get("region", "") or "",
                tags=item.get("tags"),
            )
        logger.info("Loaded {n} proxies ({a} active)",
                    n=len(self._proxies),
                    a=sum(1 for p in self._proxies.values() if p.is_active()))

    def assign(self, account_id: str, proxy_id: str | None = None) -> Proxy | None:
        if account_id in self._assignments:
            return self._proxies.get(self._assignments[account_id])
        chosen = proxy_id or ""
        if chosen and chosen in self._proxies:
            self._assignments[account_id] = chosen
            p = self._proxies[chosen]
            if p.is_active():
                logger.info("Assigned proxy {p} to {a}", p=chosen, a=account_id)
            return p if p.is_active() else None
        active = [p for p in self._proxies.values() if p.is_active()]
        if not active:
            return None
        p = random.choice(active)
        self._assignments[account_id] = p.id
        logger.info("Assigned proxy {p} to {a}", p=p.id, a=account_id)
        return p

    def get_for_account(self, account_id: str) -> Proxy | None:
        pid = self._assignments.get(account_id)
        if not pid:
            return None
        p = self._proxies.get(pid)
        return p if p and p.is_active() else None

    def release(self, account_id: str) -> None:
        self._assignments.pop(account_id, None)

    def as_dict(self) -> dict[str, Any]:
        return {
            "proxies": [p.__dict__ for p in self._proxies.values()],
            "assignments": dict(self._assignments),
        }


proxy_manager = ProxyManager()
