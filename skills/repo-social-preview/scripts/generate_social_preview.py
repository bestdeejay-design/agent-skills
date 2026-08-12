#!/usr/bin/env python3
"""Generate a 1280x640 social preview (og:image) PNG for a GitHub repo.

The GitHub social preview is set ONLY through Settings -> Social preview (UI);
there is no REST API to upload it. This script only *creates* the image file
(1280x640, <1MB) so you can upload it manually.

Composition mirrors the repo's animated header: black (or dark) background,
white title + subtitle, repo URL, and procedural wave bands in COLD/WARM colors.
Requires Pillow: `pip install pillow`.

Usage:
    python3 generate_social_preview.py --name "Project Name" --desc "Short desc" \
        --user username --cold "#00E5FF" --warm "#0ABAB5" --out og-2026-08-11.png
"""
import argparse
import math
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required: pip install pillow")

W, H = 1280, 640


def find_font(bold=True):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Black.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Black.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def fit_font(text, max_w, start, fontfile):
    size = start
    while size > 24:
        f = ImageFont.truetype(fontfile, size) if fontfile else ImageFont.load_default()
        w = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), text, font=f)[2]
        if w <= max_w:
            return f
        size -= 4
    return ImageFont.truetype(fontfile, size) if fontfile else ImageFont.load_default()


def draw_wave(d, base_y, amp, wl, phase, rgb, alpha):
    pts = [(0, base_y + amp * math.sin(phase))]
    x = 0
    while x <= W:
        pts.append((x, base_y + amp * math.sin(2 * math.pi * x / wl + phase)))
        x += 4
    pts += [(W, H), (0, H)]
    d.polygon(pts, fill=rgb + (alpha,))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="Project Name")
    ap.add_argument("--desc", default="")
    ap.add_argument("--user", default="")
    ap.add_argument("--cold", default="#00E5FF", help="wave color 1 (hex)")
    ap.add_argument("--warm", default="#0ABAB5", help="wave color 2 (hex)")
    ap.add_argument("--out", default="og-2026-08-11.png")
    ap.add_argument("--pad", type=int, default=80, help="inner padding")
    args = ap.parse_args()

    fontfile = find_font()
    cold = hex2rgb(args.cold)
    warm = hex2rgb(args.warm)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    draw_wave(od, 500, 18, 460, 0.0, cold, 130)
    draw_wave(od, 525, 14, 380, 1.2, warm, 175)
    draw_wave(od, 548, 12, 300, 2.4, warm, 220)
    img = Image.alpha_composite(img, overlay)
    d = ImageDraw.Draw(img)

    title_font = fit_font(args.name, W - 2 * args.pad, 72, fontfile)
    tb = d.textbbox((0, 0), args.name, font=title_font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    d.text(((W - tw) // 2, 215), args.name, font=title_font, fill=(255, 255, 255, 255))

    if args.desc:
        sub_font = fit_font(args.desc, W - 2 * args.pad, 30, fontfile)
        sb = d.textbbox((0, 0), args.desc, font=sub_font)
        sw, sh = sb[2] - sb[0], sb[3] - sb[1]
        d.text(((W - sw) // 2, 215 + th + 18), args.desc, font=sub_font,
               fill=(255, 255, 255, 230))

    if args.user:
        url = f"github.com/{args.user}"
        u_font = fit_font(url, W - 2 * args.pad, 26, fontfile)
        ub = d.textbbox((0, 0), url, font=u_font)
        uw, uh = ub[2] - ub[0], ub[3] - ub[1]
        d.text(((W - uw) // 2, H - 70), url, font=u_font, fill=cold + (220,))

    img.convert("RGB").save(args.out, "PNG")
    print(f"saved {args.out} ({W}x{H})")


if __name__ == "__main__":
    main()
