#!/usr/bin/env python3
"""Render the themed slides.html (16:9) into a multi-page PDF — one slide per page.

WHY THIS REUSES slides.html (the core of "looks no worse")
----------------------------------------------------------
The HTML deck produced by ``build_html.py`` is the single source of truth for the
visual design: the palette lives in ``:root`` CSS variables, the layout is driven
by the same ``.slide`` / ``.deck`` rules, and the fonts are whatever the deck
loaded. For the PDF we do NOT re-implement any layout, theme, or typography — we
take that exact ``slides.html`` and only *reflow* it for print:

  * every ``.slide`` becomes a static, full-page block (16:9) that breaks to its
    own page, instead of the on-screen "one active slide at a time" carousel;
  * navigation chrome (``.nav-hint``, ``.progress``, ``.slide-head`` page number)
    is hidden;
  * print-color-adjust is forced to ``exact`` so gradients/backgrounds survive;
  * we emulate ``screen`` media so web fonts and colors render exactly as on screen.

Because the PDF is generated from the *same* DOM + *same* CSS, the output is
visually 1:1 with the HTML — same fonts, colors, spacing, and component shapes.

The 16:9 page is achieved by sizing each slide to ``100vw x 56.25vw`` (i.e. the
browser viewport, set to 1600x900) and emitting a ``@page { size: 1600px 900px }``
with zero margins, so one slide == one landscape page.

Usage:
    python3 build_pdf.py slides.html deck.pdf [--viewport 1600x900]

Exit codes:
    0  success (prints page count)
    1  render failure (Playwright launched but pdf() raised)
    2  Playwright not installed
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# --- graceful dependency handling -------------------------------------------
try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - environment dependent
    print("Playwright not installed: pip install playwright && playwright install chromium")
    sys.exit(2)


# Print stylesheet injected into the live page before pdf(). Plain (no media
# query) so it applies under the emulated "screen" media used for rendering.
PRINT_CSS = """
html, body {
    height: auto !important;
    overflow: visible !important;
    background: var(--background) !important;
}
.deck {
    height: auto !important;
    width: 100% !important;
    position: static !important;
}
.slide {
    position: static !important;
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    transform: none !important;
    width: 100vw !important;
    height: 56.25vw !important;   /* 16:9 at a 1600px-wide viewport -> 900px */
    margin: 0 !important;
    padding: clamp(56px, 6vw, 88px) !important;
    break-after: page !important;
    page-break-after: always !important;
}
.slide:last-child {
    break-after: auto !important;
    page-break-after: auto !important;
}
.slide-head, .nav-hint, .progress {
    display: none !important;
}
* {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}
@page {
    size: 1600px 900px;
    margin: 0;
}
"""


def parse_viewport(s: str) -> tuple[int, int]:
    try:
        w, h = s.lower().split("x")
        return int(w), int(h)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"--viewport must be WxH (e.g. 1600x900), got {s!r}"
        )


def build_pdf(html_path: Path, pdf_path: Path, viewport: tuple[int, int]) -> int:
    uri = html_path.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": viewport[0], "height": viewport[1]})
            page.goto(uri, wait_until="networkidle")

            # Make sure web fonts are settled (resolves even if they fall back).
            try:
                page.evaluate("document.fonts && document.fonts.ready")
            except Exception:
                pass

            # Reflow the deck for print: one slide per page, no nav chrome.
            page.add_style_tag(content=PRINT_CSS)

            # Render as "screen" so colors/fonts match the on-screen deck 1:1.
            page.emulate_media(media="screen")

            n = page.evaluate("document.querySelectorAll('.slide').length")
            if not n:
                print(f"error: no .slide elements found in {html_path}")
                return 1

            try:
                page.pdf(
                    path=str(pdf_path),
                    landscape=True,          # ignored because width/height given; kept for clarity
                    width="1600px",
                    height="900px",
                    margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
                    prefer_css_page_size=True,
                    page_ranges="1-" + str(n),
                )
            except Exception as exc:  # pragma: no cover - runtime dependent
                print(f"error: PDF render failed: {exc}")
                return 1
        finally:
            browser.close()

    size = pdf_path.stat().st_size if pdf_path.exists() else 0
    print(f"PDF written: {pdf_path} ({n} pages, {size} bytes)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Render themed slides.html into a multi-page 16:9 PDF (one slide per page)."
    )
    ap.add_argument("html", help="input slides.html (themed deck)")
    ap.add_argument("pdf", help="output PDF path")
    ap.add_argument(
        "--viewport",
        default="1600x900",
        type=parse_viewport,
        help="render viewport WxH used to resolve vw/clamp() units (default 1600x900)",
    )
    args = ap.parse_args()

    html_path = Path(args.html)
    if not html_path.exists():
        print(f"error: input not found: {html_path}")
        return 1

    return build_pdf(html_path, Path(args.pdf), args.viewport)


if __name__ == "__main__":
    sys.exit(main())
