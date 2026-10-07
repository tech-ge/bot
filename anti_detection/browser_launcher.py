"""
Playwright browser launcher with per-account fingerprint + proxy + cookies.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from loguru import logger

from anti_detection.cookie_jar import cookie_jar
from anti_detection.fingerprint import fingerprint_manager
from anti_detection.proxy_manager import proxy_manager
from config.settings import settings


class BrowserSession:
    def __init__(self, account_id: str) -> None:
        self.account_id = account_id
        self._pw: Any = None
        self._browser: Any = None
        self._context: Any = None
        self._page: Any = None

    async def open(self, *, headless: bool = True) -> Any:
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError("playwright not installed") from exc

        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-dev-shm-usage",
            ],
        )

        fp = fingerprint_manager.load_or_create(self.account_id)
        ctx_args = fingerprint_manager.browser_context_args(fp)

        # Proxy is optional — only attach when active.
        proxy_id = None
        proxy = proxy_manager.get_for_account(self.account_id)
        if proxy is None:
            proxy = proxy_manager.assign(self.account_id, proxy_id)
        if proxy is not None and proxy.is_active():
            ctx_args["proxy"] = proxy.to_playwright()
            logger.info("Using proxy {p} for {a}", p=proxy.id, a=self.account_id)

        self._context = await self._browser.new_context(**ctx_args)
        await self._context.add_init_script(fingerprint_manager.init_script(fp))

        cookies = cookie_jar.load(self.account_id)
        if cookies:
            try:
                await self._context.add_cookies(cookies)
                logger.info("Loaded {n} cookies for {id}",
                            n=len(cookies), id=self.account_id)
            except Exception as exc:
                logger.warning("Cookie load failed for {id}: {e}",
                               id=self.account_id, e=exc)

        self._page = await self._context.new_page()
        self._page.set_default_timeout(30_000)
        return self._page

    async def persist_cookies(self) -> None:
        if self._context is None:
            return
        try:
            cookies = await self._context.cookies()
            cookie_jar.save(self.account_id, cookies)
        except Exception as exc:
            logger.warning("Failed to persist cookies for {id}: {e}",
                           id=self.account_id, e=exc)

    async def close(self) -> None:
        try:
            await self.persist_cookies()
        finally:
            for obj in (self._context, self._browser):
                try:
                    if obj is not None:
                        await obj.close()
                except Exception:
                    pass
            if self._pw is not None:
                try:
                    await self._pw.stop()
                except Exception:
                    pass
            logger.debug("Browser session closed for {id}", id=self.account_id)


def profile_dir(account_id: str) -> Path:
    p = settings.base_dir / "anti_detection" / "profiles" / account_id
    p.mkdir(parents=True, exist_ok=True)
    return p
