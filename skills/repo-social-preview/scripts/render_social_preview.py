#!/usr/bin/env python3
"""Render a hero-section HTML into a GitHub social preview PNG (1280x640).

Uses headless Chrome so the PNG is a pixel-perfect capture of real web layout
(webfonts, gradients, flexbox) - no raster composition, no generated SVG.

Usage:
    python3 render_social_preview.py hero.html --out og.png [--width 1280] [--height 640]

Pure Python 3 standard library (subprocess + tempfile).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "google-chrome",
    "chromium",
    "chromium-browser",
)


def find_chrome() -> str:
    for cand in CHROME_CANDIDATES:
        path = Path(cand)
        if path.is_file():
            return str(path)
        if "/" not in cand:
            from shutil import which
            resolved = which(cand)
            if resolved:
                return resolved
    print("ERROR: no Chrome/Chromium found; install Google Chrome or put a binary on PATH")
    sys.exit(2)


def render(html_path: Path, out: Path, width: int, height: int) -> None:
    chrome = find_chrome()
    url = html_path.resolve().as_uri()
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
            "--force-device-scale-factor=1",
            "--virtual-time-budget=10000",
            f"--window-size={width},{height}",
        f"--screenshot={out.resolve()}",
        url,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if proc.returncode != 0 and not out.is_file():
            print(f"ERROR: chrome failed (rc={proc.returncode})\n{proc.stderr[-800:]}")
            sys.exit(2)
    except subprocess.TimeoutExpired:
        if not out.is_file():
            print("ERROR: chrome timed out and wrote no screenshot")
            sys.exit(2)
        print("note: chrome did not exit in time, but the screenshot was written")


def verify(out: Path) -> None:
    size = out.stat().st_size
    kb = size / 1024
    over = " OVER 1MB LIMIT" if size >= 1024 * 1024 else ""
    print(f"written: {out} ({kb:.0f} KB){over}")
    try:
        from struct import unpack
        with open(out, "rb") as f:
            sig = f.read(24)
        if sig[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = unpack(">II", sig[16:24])
            print(f"dimensions: {w}x{h}")
    except Exception as e:
        print(f"(could not read dimensions: {e})")


def main() -> None:
    ap = argparse.ArgumentParser(description="Hero-section HTML -> GitHub social preview PNG")
    ap.add_argument("html", help="path to hero.html (standalone page)")
    ap.add_argument("--out", default="og.png", help="output PNG path")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=640)
    args = ap.parse_args()

    html = Path(args.html)
    if not html.is_file():
        print(f"ERROR: HTML not found: {html}")
        sys.exit(2)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    render(html, out, args.width, args.height)
    verify(out)


if __name__ == "__main__":
    main()
