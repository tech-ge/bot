"""
Browser fingerprint generator + persistence.
Produces a stable per-account fingerprint (canvas, webgl, UA, tz, screen, etc.).
"""
from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from loguru import logger

from config.settings import settings


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) "
    "Gecko/20100101 Firefox/127.0",
]

TIMEZONES = [
    "America/New_York", "America/Chicago", "America/Los_Angeles",
    "Europe/London", "Europe/Berlin", "Europe/Paris",
    "Asia/Tokyo", "Asia/Dubai", "Africa/Nairobi",
]

LANGUAGES = ["en-US", "en-GB", "en-CA", "en-AU"]

SCREENS = [
    {"width": 1920, "height": 1080},
    {"width": 2560, "height": 1440},
    {"width": 1440, "height": 900},
    {"width": 1536, "height": 864},
    {"width": 1366, "height": 768},
]

PLATFORMS = ["Win32", "MacIntel", "Linux x86_64"]

HARDWARE_CONCURRENCY = [4, 8, 12, 16]
DEVICE_MEMORY = [4, 8, 16]


@dataclass
class Fingerprint:
    profile_id: str
    user_agent: str
    timezone: str
    language: str
    screen: dict[str, int]
    platform: str
    hardware_concurrency: int
    device_memory: int
    webgl_vendor: str = "Google Inc. (Intel)"
    webgl_renderer: str = "ANGLE (Intel, Intel UHD Graphics 630, OpenGL 4.5)"
    canvas_noise_seed: int = 0
    audio_noise_seed: int = 0
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FingerprintManager:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or (
            settings.base_dir / settings.env_settings.fingerprint_dir
        )
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, profile_id: str) -> Path:
        return self.base_dir / f"{profile_id}.json"

    def generate(self, profile_id: str) -> Fingerprint:
        fp = Fingerprint(
            profile_id=profile_id,
            user_agent=random.choice(USER_AGENTS),
            timezone=random.choice(TIMEZONES),
            language=random.choice(LANGUAGES),
            screen=random.choice(SCREENS).copy(),
            platform=random.choice(PLATFORMS),
            hardware_concurrency=random.choice(HARDWARE_CONCURRENCY),
            device_memory=random.choice(DEVICE_MEMORY),
            canvas_noise_seed=random.randint(1, 2**31 - 1),
            audio_noise_seed=random.randint(1, 2**31 - 1),
        )
        return fp

    def load_or_create(self, profile_id: str) -> Fingerprint:
        path = self._path(profile_id)
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                return Fingerprint(**data)
            except Exception as exc:
                logger.warning("Bad fingerprint file {p}: {e} — regenerating",
                               p=path, e=exc)
        fp = self.generate(profile_id)
        self.save(fp)
        logger.info("Created fingerprint for {id}", id=profile_id)
        return fp

    def save(self, fp: Fingerprint) -> None:
        path = self._path(fp.profile_id)
        path.write_text(json.dumps(fp.to_dict(), indent=2), encoding="utf-8")

    def refresh(self, profile_id: str) -> Fingerprint:
        fp = self.generate(profile_id)
        self.save(fp)
        return fp

    # ---- Playwright injection payload ----
    def browser_context_args(self, fp: Fingerprint) -> dict[str, Any]:
        return {
            "user_agent": fp.user_agent,
            "locale": fp.language,
            "timezone_id": fp.timezone,
            "viewport": fp.screen,
            "screen": fp.screen,
            "device_scale_factor": 1,
            "is_mobile": False,
            "has_touch": False,
            "java_script_enabled": True,
            "extra_http_headers": {
                "Accept-Language": fp.language,
                "Sec-CH-UA-Platform": f'"{fp.platform}"',
            },
        }

    def init_script(self, fp: Fingerprint) -> str:
        """JS injected at document start to spoof navigator/webgl/canvas."""
        screen = fp.screen
        return f"""
        (() => {{
          const fp = {json.dumps(fp.to_dict())};
          Object.defineProperty(navigator, 'platform', {{ get: () => fp.platform }});
          Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => fp.hardware_concurrency }});
          Object.defineProperty(navigator, 'deviceMemory', {{ get: () => fp.device_memory }});
          Object.defineProperty(navigator, 'languages', {{ get: () => [fp.language, 'en'] }});
          Object.defineProperty(screen, 'width', {{ get: () => {screen['width']} }});
          Object.defineProperty(screen, 'height', {{ get: () => {screen['height']} }});
          Object.defineProperty(screen, 'availWidth', {{ get: () => {screen['width']} }});
          Object.defineProperty(screen, 'availHeight', {{ get: () => {screen['height']} }});
          const origGetParameter = WebGLRenderingContext.prototype.getParameter;
          WebGLRenderingContext.prototype.getParameter = function(p) {{
            if (p === 37445) return fp.webgl_vendor;
            if (p === 37446) return fp.webgl_renderer;
            return origGetParameter.call(this, p);
          }};
          const seed = fp.canvas_noise_seed;
          const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
          HTMLCanvasElement.prototype.toDataURL = function() {{
            const ctx = this.getContext('2d');
            if (ctx) {{
              const w = this.width, h = this.height;
              const img = ctx.getImageData(0, 0, Math.min(w, 20), Math.min(h, 20));
              for (let i = 0; i < img.data.length; i += 4) {{
                img.data[i] ^= (seed & 0xff);
              }}
              ctx.putImageData(img, 0, 0);
            }}
            return origToDataURL.apply(this, arguments);
          }};
        }})();
        """


fingerprint_manager = FingerprintManager()
