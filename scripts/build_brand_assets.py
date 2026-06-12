#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Insider Lawyers brand asset package.

Produces (in the site root):

  favicon.svg                     -- "IL" monogram, 64x64 viewBox
  favicon.ico                     -- 16+32+48 multi-size ICO
  favicon-16x16.png
  favicon-32x32.png
  apple-touch-icon.png            -- 180x180
  icon-192.png                    -- PWA standard icon
  icon-512.png                    -- PWA large icon
  icon-maskable-512.png           -- maskable icon w/ safe area
  site.webmanifest
  og-default.png                  -- 1200x630 social default
  og-default.svg                  -- editable source
  social-assets/og-default.png    -- mirrored copy for /social-assets/

Design direction:
  * "IL" monogram on a deep navy gradient background.
  * Colors derived from the existing site palette:
      navy   #01366c
      blue   #01468a
      yellow #fbba00
  * Looks like an information / resource brand, not a traditional law firm.
  * No gavel, no scales, no badge.
  * The OG default is a horizontal layout with a brand mark, headline and tagline.
  * Maskable icon adds a 10% safe-area bleed.

Idempotent. Re-run any time. Requires Pillow.

    python insiderlawyers-com/scripts/build_brand_assets.py
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---------------------------------------------------------------------------

_WORKSPACE = Path(r"C:\Users\georgea\insiderlawyer-com-lps")
ROOT = _WORKSPACE / "insiderlawyers-com"
SOCIAL = ROOT / "social-assets"

NAVY = (1, 54, 108, 255)
NAVY_DEEP = (4, 30, 64, 255)
BLUE = (1, 70, 138, 255)
YELLOW = (251, 186, 0, 255)
WHITE = (255, 255, 255, 255)
WHITE_SOFT = (255, 255, 255, 235)
SLATE = (203, 213, 225, 255)


# ---------------------------------------------------------------------------
# Font loading: prefer common Windows / system fonts. Fallback to default.
# ---------------------------------------------------------------------------

def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates_bold = [
        r"C:\Windows\Fonts\seguibl.ttf",   # Segoe UI Black
        r"C:\Windows\Fonts\seguisb.ttf",   # Segoe UI Semibold
        r"C:\Windows\Fonts\segoeuib.ttf",  # Segoe UI Bold
        r"C:\Windows\Fonts\arialbd.ttf",
    ]
    candidates_regular = [
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    pool = candidates_bold if bold else candidates_regular
    for path in pool:
        if Path(path).is_file():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Vertical gradient fill helper
# ---------------------------------------------------------------------------

def _vertical_gradient(size: tuple[int, int], top: tuple[int, int, int, int],
                       bottom: tuple[int, int, int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGBA", size, top)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        a = int(top[3] + (bottom[3] - top[3]) * t)
        d.line([(0, y), (w, y)], fill=(r, g, b, a))
    return img


def _diagonal_gradient(size: tuple[int, int],
                       a: tuple[int, int, int, int],
                       b: tuple[int, int, int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGBA", size, a)
    px = img.load()
    for y in range(h):
        for x in range(w):
            t = ((x + y) / max(1, (w + h - 2)))
            r = int(a[0] + (b[0] - a[0]) * t)
            g = int(a[1] + (b[1] - a[1]) * t)
            bl = int(a[2] + (b[2] - a[2]) * t)
            al = int(a[3] + (b[3] - a[3]) * t)
            px[x, y] = (r, g, bl, al)
    return img


def _rounded_square(size: int, radius: int, fill_top, fill_bottom) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    grad = _diagonal_gradient((size, size), fill_top, fill_bottom)
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
    canvas.paste(grad, (0, 0), mask)
    return canvas


def _draw_il_mark(canvas: Image.Image, *, accent_color=YELLOW) -> Image.Image:
    """Draw an "IL" monogram centered on the canvas with a yellow underline accent."""
    w, h = canvas.size
    d = ImageDraw.Draw(canvas)
    # Choose font size relative to canvas
    font_size = int(h * 0.62)
    font = _load_font(font_size, bold=True)
    text = "iL"
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (w - tw) // 2 - bbox[0]
    y = int(h * 0.10) - bbox[1]
    # Soft drop shadow for contrast at small sizes
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.text((x + max(1, w // 64), y + max(1, h // 64)), text, font=font,
            fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=max(1, w // 128)))
    canvas.alpha_composite(shadow)
    d.text((x, y), text, font=font, fill=WHITE)
    # Accent underline
    underline_h = max(2, h // 16)
    underline_w = int(w * 0.46)
    ux = (w - underline_w) // 2
    uy = int(h * 0.82)
    d.rounded_rectangle(
        (ux, uy, ux + underline_w, uy + underline_h),
        radius=max(1, underline_h // 2),
        fill=accent_color,
    )
    return canvas


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

def make_icon_png(size: int, *, maskable: bool = False) -> Image.Image:
    """Square PNG icon at the requested edge size."""
    radius = int(size * 0.22)
    if maskable:
        # Render mark in inner safe area (80%) so OS rounded-mask doesn't clip it.
        bg = _rounded_square(size, 0, NAVY, NAVY_DEEP)  # full bleed
        # Replace with full square (no rounded corners) for maskable spec
        bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        bg_grad = _diagonal_gradient((size, size), NAVY, NAVY_DEEP)
        bg.paste(bg_grad, (0, 0))
        inner_size = int(size * 0.80)
        inner_pad = (size - inner_size) // 2
        inner = Image.new("RGBA", (inner_size, inner_size), (0, 0, 0, 0))
        _draw_il_mark(inner)
        bg.alpha_composite(inner, (inner_pad, inner_pad))
        return bg
    canvas = _rounded_square(size, radius, NAVY, NAVY_DEEP)
    return _draw_il_mark(canvas)


def make_favicon_svg() -> str:
    """A small, hand-tuned SVG favicon. Not generated from PIL (vector, scalable)."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" '
        'aria-label="Insider Lawyers">\n'
        '  <defs>\n'
        '    <linearGradient id="bg" x1="0" y1="0" x2="64" y2="64" '
        'gradientUnits="userSpaceOnUse">\n'
        '      <stop offset="0" stop-color="#01366c"/>\n'
        '      <stop offset="1" stop-color="#041e40"/>\n'
        '    </linearGradient>\n'
        '  </defs>\n'
        '  <rect width="64" height="64" rx="14" fill="url(#bg)"/>\n'
        '  <text x="32" y="44" text-anchor="middle" '
        'font-family="Segoe UI, Arial, sans-serif" font-weight="900" '
        'font-size="36" fill="#ffffff" letter-spacing="-1">iL</text>\n'
        '  <rect x="18" y="50" width="28" height="4" rx="2" fill="#fbba00"/>\n'
        '</svg>\n'
    )


def make_og_default(width: int = 1200, height: int = 630) -> Image.Image:
    img = _diagonal_gradient((width, height), NAVY, NAVY_DEEP)
    d = ImageDraw.Draw(img)
    # Subtle yellow accent ribbon along the left side
    d.rectangle((0, 0, 14, height), fill=YELLOW)
    # Logo block on the left
    mark_size = 200
    mark = make_icon_png(mark_size)
    img.alpha_composite(mark, (90, 80))
    # Headline
    headline_font = _load_font(74, bold=True)
    sub_font = _load_font(36, bold=False)
    eyebrow_font = _load_font(28, bold=True)
    d.text((90, 320), "INSIDER LAWYERS", font=eyebrow_font, fill=YELLOW)
    d.text((90, 360), "California Injury", font=headline_font, fill=WHITE)
    d.text((90, 440), "Claim Resource", font=headline_font, fill=WHITE)
    d.text((90, 540), "Settlement reviews · second opinions · claim guides",
           font=sub_font, fill=SLATE)
    return img


def write_ico(target: Path, sizes: list[int] = [16, 32, 48]) -> None:
    icons = [make_icon_png(s) for s in sizes]
    icons[0].save(target, format="ICO", sizes=[(s, s) for s in sizes],
                   append_images=icons[1:])


def write_manifest(target: Path) -> None:
    data = {
        "name": "Insider Lawyers",
        "short_name": "Insider",
        "description": "California injury claim resource: settlement reviews, second opinions, demand letters, and claim guides.",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#041e40",
        "theme_color": "#01366c",
        "lang": "en-US",
        "dir": "ltr",
        "categories": ["legal", "reference", "education"],
        "icons": [
            {"src": "/favicon-16x16.png", "sizes": "16x16", "type": "image/png"},
            {"src": "/favicon-32x32.png", "sizes": "32x32", "type": "image/png"},
            {"src": "/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ROOT.mkdir(exist_ok=True)
    SOCIAL.mkdir(exist_ok=True)

    # PNG favicons / icons
    make_icon_png(16).save(ROOT / "favicon-16x16.png")
    make_icon_png(32).save(ROOT / "favicon-32x32.png")
    make_icon_png(180).save(ROOT / "apple-touch-icon.png")
    make_icon_png(192).save(ROOT / "icon-192.png")
    make_icon_png(512).save(ROOT / "icon-512.png")
    make_icon_png(512, maskable=True).save(ROOT / "icon-maskable-512.png")

    # ICO multi-size
    write_ico(ROOT / "favicon.ico", sizes=[16, 32, 48])

    # SVG
    (ROOT / "favicon.svg").write_text(make_favicon_svg(), encoding="utf-8")

    # OG default
    og = make_og_default()
    og_dst1 = ROOT / "og-default.png"
    og.save(og_dst1, format="PNG", optimize=True)
    # Mirror to /social-assets/ so the existing /social-assets/ folder also has
    # a real default image.
    og_dst2 = SOCIAL / "og-default.png"
    og.save(og_dst2, format="PNG", optimize=True)
    # Smaller JPG fallback for og:image sizing-sensitive consumers
    og_jpg = ROOT / "og-default.jpg"
    og.convert("RGB").save(og_jpg, format="JPEG", quality=88, optimize=True, progressive=True)

    # Manifest
    write_manifest(ROOT / "site.webmanifest")

    out_files = [
        "favicon.svg", "favicon.ico", "favicon-16x16.png", "favicon-32x32.png",
        "apple-touch-icon.png", "icon-192.png", "icon-512.png",
        "icon-maskable-512.png", "og-default.png", "og-default.jpg",
        "site.webmanifest",
    ]
    print("Wrote brand assets:")
    for f in out_files:
        p = ROOT / f
        print(f"  - /{f}  ({p.stat().st_size} bytes)")
    print(f"  - /social-assets/og-default.png  ({(SOCIAL / 'og-default.png').stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
