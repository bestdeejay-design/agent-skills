#!/usr/bin/env python3
"""gen_fixtures.py — deterministic test PNGs for raster_to_svg.py.

Pure stdlib (zlib, struct). Generates fixtures/ in the skill's evals dir:
  shapes.png    200x150 colored shapes + hole (contour test)
  gradient.png  120x120 color gradient (mosaic test)
  alpha.png     160x160 transparent background + shapes (alpha test)
  pixelart.png  32x32  hard-edged pixel art (crisp contours)
  ring.png      100x100 black ring on white (holes in one color)
"""

import os
import struct
import zlib

PNG_SIG = b"\x89PNG\r\n\x1a\n"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fixtures")


def _chunk(ctype, data):
    c = struct.pack(">I", len(data)) + ctype + data
    return c + struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)


def make_png(w, h, pixel_fn):
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # filter: None
        for x in range(w):
            raw += bytes(pixel_fn(x, y))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)  # RGBA8, non-interlaced
    return PNG_SIG + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + _chunk(b"IEND", b"")


def in_circle(x, y, cx, cy, r):
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def shapes(x, y):
    # white background
    if in_circle(x, y, 150, 100, 40):
        return (20, 90, 220, 255)          # blue circle
    if in_circle(x, y, 150, 45, 35):
        if in_circle(x, y, 150, 45, 14):
            return (255, 255, 255, 255)    # white hole (ring)
        return (240, 140, 20, 255)         # orange ring
    if 20 <= x <= 90 and 20 <= y <= 80:
        return (220, 40, 40, 255)          # red rect
    # green triangle: (30,110) (110,110) (70,148)
    if 30 <= x <= 110 and 110 <= y <= 148:
        if y <= 110 + (x - 30) * 38 / 80 and y <= 110 + (110 - x) * 38 / 80:
            return (50, 180, 70, 255)
    return (255, 255, 255, 255)


def gradient(x, y):
    t = x / 119.0
    r = int(20 + 200 * t)
    g = int(60 + 120 * t)
    b = int(220 - 180 * t)
    return (r, g, b, 255)


def alpha(x, y):
    if in_circle(x, y, 60, 80, 45):
        return (150, 60, 220, 255)          # purple circle
    if 90 <= x <= 140 and 30 <= y <= 100:
        return (40, 200, 190, 255)          # teal square
    return (0, 0, 0, 0)                     # transparent


def pixelart(x, y):
    # 32x32 heart, hard edges
    hx, hy = x / 32.0, y / 32.0
    cx1, cy1, r1 = 0.32, 0.35, 0.22
    cx2, cy2, r2 = 0.68, 0.35, 0.22
    in_heart = ((hx - cx1) ** 2 + (hy - cy1) ** 2 <= r1 ** 2 or
                (hx - cx2) ** 2 + (hy - cy2) ** 2 <= r2 ** 2 or
                (0.32 <= hx <= 0.68 and 0.42 <= hy <= 0.72))
    if in_heart:
        return (230, 60, 90, 255)
    return (30, 30, 40, 255)


def ring(x, y):
    if in_circle(x, y, 50, 50, 40) and not in_circle(x, y, 50, 50, 28):
        return (20, 20, 20, 255)
    return (250, 250, 250, 255)


FIXTURES = {
    "shapes.png": (200, 150, shapes),
    "gradient.png": (120, 120, gradient),
    "alpha.png": (160, 160, alpha),
    "pixelart.png": (32, 32, pixelart),
    "ring.png": (100, 100, ring),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, (w, h, fn) in sorted(FIXTURES.items()):
        path = os.path.join(OUT, name)
        with open(path, "wb") as fh:
            fh.write(make_png(w, h, fn))
        print(f"{name}: {w}x{h} -> {os.path.getsize(path)} bytes")


if __name__ == "__main__":
    main()