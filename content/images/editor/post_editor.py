"""
Post-editor for images before publishing.
Handles per-platform aspect ratios, watermarks, and safe zones.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from loguru import logger

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Pillow not installed — pip install Pillow") from exc

from content.media_utils import temp_dir


# Common platform aspect ratios
ASPECTS: dict[str, tuple[int, int]] = {
    "instagram_square": (1080, 1080),
    "instagram_portrait": (1080, 1350),
    "instagram_story": (1080, 1920),
    "facebook_feed": (1200, 630),
    "facebook_square": (1080, 1080),
    "twitter_landscape": (1600, 900),
    "twitter_square": (1080, 1080),
    "snapchat_story": (1080, 1920),
    "telegram": (1280, 720),
    "generic": (1200, 1200),
}


@dataclass
class EditOptions:
    aspect: str = "generic"
    watermark_text: str = ""
    watermark_position: Literal["br", "bl", "tr", "tl", "center"] = "br"
    watermark_opacity: int = 160
    brand_color: tuple[int, int, int] = (0, 0, 0)
    add_border: bool = False
    border_color: tuple[int, int, int] = (255, 255, 255)
    border_width: int = 20
    add_safe_zone: bool = False  # overlay guide (dev only)
    max_size_kb: int | None = None


class PostEditor:
    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or temp_dir()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ---------- core ops ----------
    def _fit_aspect(self, im: Image.Image, size: tuple[int, int]) -> Image.Image:
        return ImageOps.fit(im, size, method=Image.LANCZOS, centering=(0.5, 0.5))

    def _add_watermark(self, im: Image.Image, opts: EditOptions) -> Image.Image:
        if not opts.watermark_text:
            return im
        base = im.convert("RGBA")
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
        w, h = base.size
        pad = 24
        # rough text size
        tw, th = (len(opts.watermark_text) * 8, 16)
        positions = {
            "br": (w - pad - tw, h - pad - th),
            "bl": (pad, h - pad - th),
            "tr": (w - pad - tw, pad),
            "tl": (pad, pad),
            "center": ((w - tw) // 2, (h - th) // 2),
        }
        x, y = positions.get(opts.watermark_position, positions["br"])
        draw.text((x, y), opts.watermark_text,
                  fill=(255, 255, 255, opts.watermark_opacity), font=font)
        return Image.alpha_composite(base, overlay).convert("RGB")

    def _add_border(self, im: Image.Image, opts: EditOptions) -> Image.Image:
        if not opts.add_border:
            return im
        return ImageOps.expand(im, border=opts.border_width,
                               fill=opts.border_color)

    def _add_safe_zone(self, im: Image.Image) -> Image.Image:
        draw = ImageDraw.Draw(im)
        w, h = im.size
        margin = int(min(w, h) * 0.1)
        draw.rectangle([margin, margin, w - margin, h - margin],
                       outline=(255, 0, 0), width=3)
        return im

    def _compress(self, im: Image.Image, max_kb: int) -> Image.Image:
        # iteratively reduce quality until under max_kb (approximate)
        from io import BytesIO
        quality = 90
        buf = BytesIO()
        while quality >= 40:
            buf.seek(0)
            buf.truncate()
            im.save(buf, format="JPEG", quality=quality, optimize=True)
            if buf.tell() / 1024 <= max_kb:
                break
            quality -= 10
        buf.seek(0)
        return Image.open(buf).convert("RGB")

    # ---------- public API ----------
    def edit(self, src: str | Path, opts: EditOptions) -> Path:
        src = Path(src)
        if not src.exists():
            raise FileNotFoundError(src)

        with Image.open(src) as raw:
            im = raw.convert("RGB")

        target = ASPECTS.get(opts.aspect, ASPECTS["generic"])
        im = self._fit_aspect(im, target)
        im = self._add_border(im, opts)
        im = self._add_watermark(im, opts)
        if opts.add_safe_zone:
            im = self._add_safe_zone(im)
        if opts.max_size_kb:
            im = self._compress(im, opts.max_size_kb)

        out = self.output_dir / f"{src.stem}_{opts.aspect}.jpg"
        im.save(out, "JPEG", quality=90, optimize=True)
        logger.info("Edited {s} -> {d} ({a})", s=src, d=out, a=opts.aspect)
        return out

    def edit_for_platform(
        self,
        src: str | Path,
        platform: str,
        *,
        watermark: str = "",
        max_size_kb: int | None = None,
    ) -> Path:
        aspect = {
            "instagram": "instagram_square",
            "facebook": "facebook_feed",
            "twitter": "twitter_landscape",
            "snapchat": "snapchat_story",
            "telegram": "telegram",
        }.get(platform, "generic")
        return self.edit(src, EditOptions(
            aspect=aspect,
            watermark_text=watermark,
            max_size_kb=max_size_kb,
        ))

    def batch_edit(self, sources: list[str | Path],
                   opts: EditOptions) -> list[Path]:
        out: list[Path] = []
        for s in sources:
            try:
                out.append(self.edit(s, opts))
            except Exception as exc:
                logger.warning("Edit failed for {s}: {e}", s=s, e=exc)
        return out


post_editor = PostEditor()
