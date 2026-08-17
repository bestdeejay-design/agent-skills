#!/usr/bin/env python3
"""qa_pixels.py — pixel-level quality gate for raster_to_svg output.

Prerequisite: render the generated SVGs in a real browser (element
screenshots at 1:1, e.g. via Playwright) and save them next to this file as
qa_<name>.png. The gate decodes the screenshots with the skill's own PNG
decoder and checks color coverage at control points and key regions.
Screenshots may carry a device-pixel-ratio (2x on Retina); every control
point is scaled from the SVG's intrinsic space. Exit 0 = all checks pass.

Usage: python3 evals/qa_pixels.py
"""
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from raster_to_svg import decode_png  # reuse the skill's decoder as the gate

FIX = os.path.join(HERE, "qa_%s.png")
FAILS = []
INTRINSIC = {
    "shapes-src": (200, 150), "shapes": (200, 150), "ring": (100, 100),
    "pixelart": (32, 32), "alpha": (160, 160), "mosaic": (120, 120),
}


def load(name):
    with open(FIX % name, "rb") as fh:
        w, h, rgba = decode_png(fh.read())
    iw, ih = INTRINSIC[name]
    return w, h, rgba, w / iw, h / ih


def px(rgba, w, x, y, sx, sy):
    base = (int(y * sy) * w + int(x * sx)) * 4
    return (rgba[base], rgba[base + 1], rgba[base + 2], rgba[base + 3])


def close(a, b, tol=45):
    return all(abs(x - y) <= tol for x, y in zip(a[:3], b[:3]))


def check(name, desc, cond):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}: {desc}")
    if not cond:
        FAILS.append(f"{name}: {desc}")


def coverage(rgba, w, h, sx, sy, cx, cy, r, target, tol=45, min_frac=0.9):
    hits = total = 0
    for y in range(max(0, cy - r), min(int(h / sy), cy + r + 1)):
        for x in range(max(0, cx - r), min(int(w / sx), cx + r + 1)):
            if (x - cx) ** 2 + (y - cy) ** 2 > r * r:
                continue
            total += 1
            if close(px(rgba, w, x, y, sx, sy), target, tol):
                hits += 1
    return (hits / total) if total else 0.0


def main():
    # ---- original sanity (the gate itself must be sound) ----
    w, h, img, sx, sy = load("shapes-src")
    check("src", "blue circle center", close(px(img, w, 150, 100, sx, sy), (20, 90, 220), 30))
    check("src", "red rect center", close(px(img, w, 55, 50, sx, sy), (220, 40, 40), 30))
    check("src", "green triangle", close(px(img, w, 70, 120, sx, sy), (50, 180, 70), 30))
    check("src", "ring hole is white", close(px(img, w, 150, 45, sx, sy), (255, 255, 255), 20))

    # ---- shapes contour ----
    w, h, img, sx, sy = load("shapes")
    check("shapes", "blue circle present", close(px(img, w, 150, 100, sx, sy), (20, 90, 220), 45))
    check("shapes", "red rect present", close(px(img, w, 55, 50, sx, sy), (220, 40, 40), 45))
    check("shapes", "green triangle present", close(px(img, w, 70, 120, sx, sy), (50, 180, 70), 45))
    check("shapes", "orange ring present", close(px(img, w, 150, 20, sx, sy), (240, 140, 20), 45))
    check("shapes", "ring hole preserved (white)",
          close(px(img, w, 150, 45, sx, sy), (255, 255, 255), 30))
    check("shapes", "background white", close(px(img, w, 10, 140, sx, sy), (255, 255, 255), 20))
    frac = coverage(img, w, h, sx, sy, 150, 100, 36, (20, 90, 220))
    check("shapes", f"circle coverage {frac:.2f} >= 0.9", frac >= 0.9)
    frac = coverage(img, w, h, sx, sy, 150, 45, 13, (255, 255, 255))
    check("shapes", f"ring hole coverage {frac:.2f} >= 0.9", frac >= 0.9)

    # ---- ring: hole must survive ----
    w, h, img, sx, sy = load("ring")
    check("ring", "ring body black", close(px(img, w, 50, 20, sx, sy), (20, 20, 20), 30))
    check("ring", "hole is white", close(px(img, w, 50, 50, sx, sy), (250, 250, 250), 30))
    frac = coverage(img, w, h, sx, sy, 50, 50, 24, (250, 250, 250))
    check("ring", f"hole coverage {frac:.2f} >= 0.9", frac >= 0.9)

    # ---- pixelart: heart recognizable ----
    w, h, img, sx, sy = load("pixelart")
    check("pixelart", "heart red", close(px(img, w, 16, 14, sx, sy), (230, 60, 90), 45))
    check("pixelart", "background dark", close(px(img, w, 4, 4, sx, sy), (30, 30, 40), 45))

    # ---- alpha: transparency respected ----
    w, h, img, sx, sy = load("alpha")
    check("alpha", "purple circle", close(px(img, w, 60, 80, sx, sy), (150, 60, 220), 45))
    check("alpha", "teal square", close(px(img, w, 115, 65, sx, sy), (40, 200, 190), 45))

    # ---- mosaic: gradient direction readable ----
    w, h, img, sx, sy = load("mosaic")
    r, g, b, _ = px(img, w, 8, 8, sx, sy)
    check("mosaic", f"left side blue-ish (r={r},g={g},b={b})", b > r and b > g)
    r, g, b, _ = px(img, w, 112, 112, sx, sy)
    check("mosaic", f"right side yellow-ish (r={r},g={g},b={b})", r > b and g > b)

    print("-" * 60)
    if FAILS:
        print(f"QA FAILED: {len(FAILS)} check(s)")
        sys.exit(1)
    print("QA PASSED: all checks ok")
    sys.exit(0)


if __name__ == "__main__":
    main()