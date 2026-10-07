"""
Per-account isolation: bind fingerprint + proxy + cookie file together.
The isolator is the *only* place that ties those three things to one account.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loguru import logger

from accounts.account import Account
from anti_detection.cookie_jar import cookie_jar
from anti_detection.fingerprint import Fingerprint, fingerprint_manager
from anti_detection.proxy_manager import Proxy, proxy_manager


@dataclass
class Isolation:
    account_id: str
    fingerprint: Fingerprint
    proxy: Proxy | None
    cookie_file: str


class Isolator:
    """Binds fingerprint + proxy + cookies for one account. Never mixes them."""

    def __init__(self) -> None:
        self._bindings: dict[str, Isolation] = {}

    def bind(self, account: Account) -> Isolation:
        if account.id in self._bindings:
            return self._bindings[account.id]

        profile_id = account.isolation.profile_id or account.id
        fp = fingerprint_manager.load_or_create(profile_id)

        proxy_id = account.isolation.proxy_id or ""
        proxy = proxy_manager.assign(account.id, proxy_id) if proxy_id else \
                proxy_manager.get_for_account(account.id)
        if proxy is not None and not proxy.is_active():
            proxy = None

        cookie_file = account.isolation.cookie_file or account.auth.cookie_file or \
                      f"{account.id}.pkl"

        iso = Isolation(
            account_id=account.id,
            fingerprint=fp,
            proxy=proxy,
            cookie_file=cookie_file,
        )
        self._bindings[account.id] = iso
        logger.info(
            "Isolation bound for {id}: fp={fp}, proxy={p}, cookies={c}",
            id=account.id, fp=profile_id,
            p=(proxy.id if proxy else "direct"),
            c=cookie_file,
        )
        return iso

    def get(self, account_id: str) -> Isolation | None:
        return self._bindings.get(account_id)

    def release(self, account_id: str) -> None:
        self._bindings.pop(account_id, None)
        proxy_manager.release(account_id)

    # ---- concrete helpers used by adapters ----
    def context_args(self, account: Account) -> dict[str, Any]:
        iso = self.bind(account)
        args = fingerprint_manager.browser_context_args(iso.fingerprint)
        if iso.proxy is not None:
            args["proxy"] = iso.proxy.to_playwright()
        return args

    def init_script(self, account: Account) -> str:
        iso = self.bind(account)
        return fingerprint_manager.init_script(iso.fingerprint)

    def cookies(self, account: Account) -> list[dict[str, Any]]:
        return cookie_jar.load(account.id)

    def save_cookies(self, account: Account, cookies: list[dict[str, Any]]) -> None:
        cookie_jar.save(account.id, cookies)


isolator = Isolator()
