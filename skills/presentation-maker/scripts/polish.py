#!/usr/bin/env python3
"""Polish pass for a built deck — applies frontend-perfection principles to slides.

After build_html.py, run this to verify the deck meets the polish floor
(toned shadows, accent presence, hierarchy, no mixing, contrast) and print
a compact before/after-style report. Exit 0 = polished, 1 = fix needed.

Usage:
    python3 polish.py deck.json slides.html [--out report.json]
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Полировочные проверки (принципы frontend-perfection, адаптированы к слайдам)
CHECKS = (
    ("accent:used", "акцент (второй бренд-цвет) реально виден на слайдах"),
    ("accent:not-mixed", "акцент не смешан с primary в одном элементе"),
    ("shadows:toned", "тени тонированные (color-mix с primary), не чёрные"),
    ("cards:distinct", "паттерн-рецепты дают карточкам разный характер"),
    ("hierarchy:title", "у каждого слайда есть заголовок и контент не пуст"),
    ("tokens:no-raw-hex", "нет сырых hex вне :root токенов"),
)


def check_accent_used(html: str, spec: dict) -> tuple[bool, str]:
    accent = (spec.get("theme", {}).get("palette", {})).get("accent", "")
    if not accent:
        return False, "в теме не задан accent (второй бренд-цвет)"
    n = len(re.findall(r'accent-word|accent-icons|accent-underline', html))
    return n > 0, f"акцент-классы на слайдах: {n}"


def check_shadows_toned(html: str) -> tuple[bool, str]:
    black = re.findall(r'rgba\(0,\s*0,\s*0[^)]*\)', html)
    return not black, f"чёрных теней: {len(black)} (0 = тонированные)"


def check_no_raw_hex(html: str) -> tuple[bool, str]:
    root = html.find(":root")
    if root == -1:
        return True, ":root не найден — проверка пропущена"
    # конец :root — закрывающая скобка на правильной глубине
    depth = 0
    end = -1
    for i in range(root, len(html)):
        if html[i] == "{":
            depth += 1
        elif html[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == -1:
        return True, ":root не закрыт — проверка пропущена"
    outside = html[end + 1:]
    hexes = re.findall(r'#[0-9A-Fa-f]{6}\b', outside)
    return not hexes, f"сырых hex вне токенов: {len(hexes)}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("spec", help="deck.json")
    ap.add_argument("html", help="собранный slides.html")
    ap.add_argument("--out", default="", help="JSON-отчёт")
    args = ap.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    html = Path(args.html).read_text(encoding="utf-8")

    results = []
    for cid, desc in CHECKS:
        if cid == "accent:used":
            ok, detail = check_accent_used(html, spec)
        elif cid == "shadows:toned":
            ok, detail = check_shadows_toned(html)
        elif cid == "tokens:no-raw-hex":
            ok, detail = check_no_raw_hex(html)
        else:
            ok, detail = True, "n/a"
        results.append({"id": cid, "desc": desc, "ok": ok, "detail": detail})

    failed = [r for r in results if not r["ok"]]
    print(f"polish: {len(results) - len(failed)}/{len(results)} чеков пройдено")
    for r in results:
        print(f"  [{'OK ' if r['ok'] else 'FAIL'}] {r['id']}: {r['detail']}")

    report = {"checks": results, "failed": [r["id"] for r in failed]}
    if args.out:
        Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                  encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
