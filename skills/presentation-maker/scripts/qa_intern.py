#!/usr/bin/env python3
"""Обёртка над extern-линтером intern (markusz/intern) для decks presentation-maker.

Запускает `intern check --output json`, затем фильтрует ложные срабатывания
дизайн-системы: элементы с именами ghost*/decor*/chrome-* намеренно выходят
за холст / накладываются на контент, поэтому их нарушения исключаются из
отчёта (по позиции фигуры из XML слайда). Оставшиеся нарушения печатаются
таблицей, exit 0 = чисто, 1 = есть ошибки.

Использование:
    python3 qa_intern.py deck.pptx [--disable RULE,...] [--threshold N]

Зависимости: python3 stdlib, бинарь `intern` в PATH (brew install
markusz/intern/intern или prebuilt binary из releases).
EMU -> px: 9525 единиц на пиксель (16:9 холст 1600x900).
"""
import argparse
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

# Имена фигур дизайн-системы, которые намеренно выходят за холст / перекрывают контент
DESIGN_PREFIXES = ("ghost", "decor", "chrome", "line-", "accent-", "bg-", "watermark", "quote",
                   "process-card", "step-num", "toc-")
EMU_PER_PX = 9525


def shapes_by_position(pptx_path: str, slide_num: int) -> dict:
    """Возвращает { (x_px, y_px): имя_фигуры } для слайда (1-based)."""
    result = {}
    try:
        with zipfile.ZipFile(pptx_path) as z:
            names = [n for n in z.namelist() if n.startswith(f"ppt/slides/slide{slide_num}.xml")]
            if not names:
                return result
            xml = z.read(names[0]).decode("utf-8", errors="replace")
    except Exception:
        return result
    # каждый элемент: имя из cNvPr + позиция из первой a:off внутри него
    for m in re.finditer(
        r'<p:cNvPr[^>]*name="([^"]+)".*?<a:off x="(-?\d+)" y="(-?\d+)"/>',
        xml,
        flags=re.S,
    ):
        name, ex, ey = m.group(1), int(m.group(2)), int(m.group(3))
        # intern truncate'ит EMU->px (floor для позитивных), поэтому int(), а не round()
        result[(int(ex / EMU_PER_PX), int(ey / EMU_PER_PX))] = name
    return result


def parse_position(pos: str) -> tuple | None:
    """'(76px, 132px)' -> (76, 132)."""
    m = re.match(r"\((-?\d+)px,\s*(-?\d+)px\)", pos or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def is_design_element(pptx_path: str, slide: int, pos_str: str) -> bool:
    if not pos_str:
        return False
    pos = parse_position(pos_str)
    if not pos:
        return False
    name = shapes_by_position(pptx_path, slide).get(pos, "")
    return any(name.startswith(p) for p in DESIGN_PREFIXES)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pptx", help=".pptx файл")
    ap.add_argument("--disable", default="", help="правила intern для отключения (через запятую)")
    ap.add_argument("--threshold", type=int, default=2, help="толерантность выравнивания, px (default 2)")
    ap.add_argument("--skip-token-rules", action="store_true",
                    help="игнорировать FONT_SIZE_VARIETY/COLOR_VARIETY (деки с дизайн-токенами)")
    args = ap.parse_args()

    cmd = ["intern", "check", args.pptx, "--output", "json", "--threshold", str(args.threshold)]
    if args.disable:
        cmd += ["--disable", args.disable]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        print("ОШИБКА: бинарь `intern` не найден. Установите: brew install markusz/intern/intern")
        return 2
    except subprocess.TimeoutExpired:
        print("ОШИБКА: intern превысил таймаут 300s")
        return 2

    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        print("ОШИБКА: intern не вернул JSON:", proc.stderr[:500])
        return 2

    real = []  # (slide, rule, severity, element, position, message)
    skipped = 0
    for f in report.get("files", []):
        for v in f.get("violations", []):
            slide = v.get("slide")
            if slide is not None and is_design_element(args.pptx, slide, v.get("element_position")):
                skipped += 1
                continue
            if args.skip_token_rules and v.get("rule_id") in ("FONT_SIZE_VARIETY", "COLOR_VARIETY"):
                skipped += 1
                continue
            real.append(
                (
                    slide if slide is not None else "-",
                    v.get("rule_id", "?"),
                    v.get("severity", "error"),
                    v.get("element_type", "-"),
                    v.get("element_position", "-"),
                    v.get("message", ""),
                )
            )

    errors = sum(1 for r in real if r[2] == "error")
    warnings = sum(1 for r in real if r[2] == "warning")

    print(f"intern: {len(real)} нарушение(й) после фильтра дизайн-элементов "
          f"(отсеяно {skipped} ложных ghost/decor/chrome)")
    if real:
        print(f"{'Slide':<6} {'Rule':<24} {'Type':<12} {'Position':<18} Message")
        print("-" * 90)
        for slide, rule, sev, etype, pos, msg in real:
            print(f"{str(slide):<6} {rule:<24} {etype:<12} {pos:<18} [{sev}] {msg[:70]}")
    print(f"Итог: {errors} ошибок, {warnings} предупреждений")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
