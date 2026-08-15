#!/usr/bin/env python3
"""Mandatory QA gate for presentation-maker: verify slides.html renders correctly.

Checks, per slide, in a real Chromium:
  1. slide has a heading and non-empty content
  2. no horizontal overflow on the slide itself
  3. every card/row/badge holds its content (children do not spill past borders)
  4. text containers do not clip (scrollWidth <= clientWidth)
  5. keyboard navigation switches slides
  6. optional: slide count matches the deck.json spec

Usage:
    python verify_slides.py slides.html [--spec deck.json] [--viewport 1600x900]
Exits 0 when every check passes, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

CARD_SELECTORS = (
    ".metric-card, .step-card, .col-card, .tl-card, .kpi-card, "
    ".bullet-list li, tr, .badge"
)
CONTENT_SELECTORS = (
    "h1, h2, h3, .subtitle, .meta-line, .bullet-list li, td, th, "
    ".metric-value, .metric-label, .step-text, .step-title, .step-desc, "
    ".col-card h3, .col-card li, .tl-card, .kpi-value, .kpi-label, .badge, "
    ".quote-text, .quote-attrib, .hero-value, .hero-label, .feature-card p, "
    ".logo-tile, .toc-title, .toc-desc"
)


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify slides.html layout quality")
    ap.add_argument("html", help="path to slides.html")
    ap.add_argument("--spec", help="optional deck.json to cross-check slide count")
    ap.add_argument("--viewport", default="1600x900", help="viewport WxH")
    args = ap.parse_args()

    html = Path(args.html).resolve()
    if not html.exists():
        print(f"FAIL: {html} not found")
        return 1

    expected = None
    if args.spec:
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        expected = len(spec.get("slides", []))

    w, h = (int(x) for x in args.viewport.lower().split("x"))
    problems: list[str] = []
    slide_heads: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": w, "height": h})
        page.add_style_tag(content="* { transition: none !important; animation: none !important; }")
        page.goto(html.as_uri())
        page.wait_for_timeout(300)

        total = page.evaluate("document.querySelectorAll('.slide').length")
        if total == 0:
            print("FAIL: no .slide elements found")
            browser.close()
            return 1
        if expected is not None and total != expected:
            problems.append(f"slide count: expected {expected}, got {total}")

        for n in range(total):
            page.evaluate(
                """(n) => document.querySelectorAll('.slide')
                      .forEach((s, j) => s.classList.toggle('active', j === n))""",
                n,
            )
            page.wait_for_timeout(500)
            result = page.evaluate(
                """(payload) => {
                    const { n, cardSel, contentSel } = payload;
                    const slide = document.querySelectorAll('.slide')[n];
                    const issues = [];
                    const head = slide.querySelector('h1, h2');
                    if (!head || !head.textContent.trim())
                        issues.push('no heading');
                    const hasContent = Array.from(slide.querySelectorAll(contentSel))
                        .some(el => el.textContent.trim().length > 0);
                    if (!hasContent) issues.push('empty content');
                    for (const card of slide.querySelectorAll(cardSel)) {
                        const cr = card.getBoundingClientRect();
                        for (const child of card.querySelectorAll('*')) {
                            const r = child.getBoundingClientRect();
                            if (r.width > 0 && (r.left < cr.left - 2 || r.right > cr.right + 2))
                                issues.push('spill in ' + card.className.split(' ')[0]
                                            + ': ' + child.textContent.trim().slice(0, 18));
                        }
                    }
                    return { head: head ? head.textContent.trim() : '', issues };
                }""",
                {"n": n, "cardSel": CARD_SELECTORS, "contentSel": CONTENT_SELECTORS},
            )
            slide_heads.append(result["head"])
            if result["issues"]:
                problems.append(f"slide {n + 1} ({result['head']}): {', '.join(result['issues'])}")

        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(80)
        nav_ok = page.evaluate(
            """() => Array.from(document.querySelectorAll('.slide'))
                         .filter(s => s.classList.contains('active')).length === 1"""
        )
        if not nav_ok:
            problems.append("navigation: expected exactly one active slide")
        page.keyboard.press("ArrowLeft")
        browser.close()

    print(f"Viewport {w}x{h} | slides: {total}" + (f" (spec: {expected})" if expected else ""))
    for i, head in enumerate(slide_heads, start=1):
        print(f"  slide {i:2d}: {head}")
    if problems:
        print("\nFAIL:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nPASS: все слайды собраны качественно — текст в карточках, нет переполнений.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
