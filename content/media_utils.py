"""Media helpers: resize, watermark, format conversion."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from loguru import logger

from config.settings import settings


def media_dir() -> Path:
    p = settings.base_dir / "content" / "media"
    p.mkdir(parents=True, exist_ok=True)
    return p


def temp_dir() -> Path:
    p = media_dir() / "temp"
    p.mkdir(parents=True, exist_ok=True)
    return p


def images_dir() -> Path:
    p = media_dir() / "images"
    p.mkdir(parents=True, exist_ok=True)
    return p


def videos_dir() -> Path:
    p = media_dir() / "videos"
    p.mkdir(parents=True, exist_ok=True)
    return p


def resize_image(path: str | Path, width: int, height: int,
                 out: str | Path | None = None) -> Path:
    try:
        from PIL import Image  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Pillow not installed") from exc

    src = Path(path)
    dst = Path(out) if out else temp_dir() / f"{src.stem}_{width}x{height}{src.suffix}"
    with Image.open(src) as im:
        im = im.convert("RGB")
        im = im.resize((width, height))
        im.save(dst)
    logger.debug("Resized {s} -> {d}", s=src, d=dst)
    return dst


def watermark_image(path: str | Path, text: str,
                    out: str | Path | None = None) -> Path:
    try:
        from PIL import Image, ImageDraw, ImageFont  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Pillow not installed") from exc

    src = Path(path)
    dst = Path(out) if out else temp_dir() / f"{src.stem}_wm{src.suffix}"
    with Image.open(src).convert("RGBA") as base:
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
        pad = 12
        w, h = base.size
        draw.text((w - pad - 200, h - pad - 20), text,
                  fill=(255, 255, 255, 160), font=font)
        combined = Image.alpha_composite(base, overlay).convert("RGB")
        combined.save(dst)
    logger.debug("Watermarked {s} -> {d}", s=src, d=dst)
    return dst


def to_webp(path: str | Path, out: str | Path | None = None,
            quality: int = 85) -> Path:
    try:
        from PIL import Image  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Pillow not installed") from exc

    src = Path(path)
    dst = Path(out) if out else temp_dir() / f"{src.stem}.webp"
    with Image.open(src) as im:
        im.save(dst, "WEBP", quality=quality)
    return dst


def info(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    return {
        "path": str(p),
        "exists": p.exists(),
        "size_bytes": p.stat().st_size if p.exists() else 0,
        "suffix": p.suffix,
    }
