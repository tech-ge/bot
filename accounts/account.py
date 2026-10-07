"""Account model — typed view over per-account YAML."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from config.settings import settings


@dataclass
class IsolationConfig:
    profile_id: str = ""
    proxy_id: str = ""
    fingerprint_file: str = ""
    cookie_file: str = ""


@dataclass
class AuthConfig:
    method: str = "cookie"          # cookie | oauth | graph | bot_token | password
    cookie_file: str = ""
    token_env: str = ""
    api_key_env: str = ""
    api_secret_env: str = ""
    access_token_env: str = ""
    access_secret_env: str = ""
    page_id_env: str = ""
    ig_user_id: str = ""


@dataclass
class Account:
    id: str
    platform: str
    type: str = "personal"
    username: str = ""
    enabled: bool = True

    auth: AuthConfig = field(default_factory=AuthConfig)
    isolation: IsolationConfig = field(default_factory=IsolationConfig)

    limits: dict[str, Any] = field(default_factory=dict)
    topics: list[str] = field(default_factory=list)
    images: list[str] = field(default_factory=list)
    chat_id: str = ""

    raw: dict[str, Any] = field(default_factory=dict)

    # ---- constructors ----
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Account":
        auth = AuthConfig(**(data.get("auth") or {}))
        iso = IsolationConfig(**(data.get("isolation") or {}))
        return cls(
            id=str(data["id"]),
            platform=str(data["platform"]),
            type=str(data.get("type", "personal")),
            username=str(data.get("username", "")),
            enabled=bool(data.get("enabled", True)),
            auth=auth,
            isolation=iso,
            limits=dict(data.get("limits") or {}),
            topics=list(data.get("topics") or []),
            images=list(data.get("images") or []),
            chat_id=str(data.get("chat_id", "") or ""),
            raw=dict(data),
        )

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Account":
        p = Path(path)
        if not p.is_absolute():
            p = settings.base_dir / p
        if not p.exists():
            raise FileNotFoundError(f"Account YAML not found: {p}")
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        acct = cls.from_dict(data)
        logger.debug("Loaded account {id} from {p}", id=acct.id, p=p)
        return acct

    # ---- helpers ----
    def is_page(self) -> bool:
        return self.type == "page"

    def is_bot(self) -> bool:
        return self.type == "bot"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "platform": self.platform,
            "type": self.type,
            "username": self.username,
            "enabled": self.enabled,
            "auth": self.auth.__dict__,
            "isolation": self.isolation.__dict__,
            "limits": self.limits,
            "topics": self.topics,
            "images": self.images,
            "chat_id": self.chat_id,
        }
