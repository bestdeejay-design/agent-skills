#!/usr/bin/env python3
"""vision_qa — визуальная приёмка презентации (Слой 4).

Важно: этот скрипт САМ не умеет "смотреть" на слайды — vision-модель есть
только у агента, который выполняет скил (Claude Code и т.п.), не у
изолированного Python-процесса. Поэтому vision_qa устроен в три шага:

  1. `vision_qa.py shoot slides.html` — скриншотит каждый слайд через
     .active-переключение (дожидаясь конца CSS-transition) и печатает
     ФИКСИРОВАННУЮ рубрику + список путей к картинкам. Дальше АГЕНТ обязан
     реально посмотреть на каждый файл (инструментом чтения изображений) и
     оценить по рубрике — это не опциональный шаг, а часть gate.

  2. `vision_qa.py record slides.html --slide 4 --verdict FAIL
       --check иерархия=PASS --check читаемость=FAIL
       --recommendation "..."` — агент записывает вердикт по каждому
     слайду сюда, по одному вызову на слайд, после реального просмотра.

  3. `vision_qa.py finalize slides.html` — считает итог: PASS только если
     ЗАПИСАН вердикт по каждому слайду и все они PASS. Если по какому-то
     слайду вердикта нет вообще — это FAIL с явным указанием "не
     проверено", а не тихий PASS. Раньше здесь была структурная заглушка,
     которая помечала PASS всё подряд, не глядя на скриншоты — это
     удалено, потому что не ловит вообще ничего.

Использование:
    python3 vision_qa.py shoot slides.html [--out-dir vision_shots]
    python3 vision_qa.py record slides.html --slide N --verdict PASS|FAIL
        [--check "пункт=PASS|FAIL" ...] [--recommendation "..."]
    python3 vision_qa.py finalize slides.html
"""
import argparse
import json
import sys
from pathlib import Path

RUBRIC = """Оцени слайд презентации по каждому пункту (PASS/FAIL + одна фраза почему):
1. ИЕРАРХИЯ: с первого взгляда (1 сек) понятно, что на слайде главное?
2. ЧИТАЕМОСТЬ: весь текст читается без напряжения, ничего не наложено друг
   на друга, ничего не обрезано на глаз?
3. БАЛАНС: распределение элементов не выглядит случайным — есть композиционная
   логика (не "текст в углу, дыра посередине")?
4. ВОЗДУХ: достаточно пустого пространства, слайд не перегружен?
5. НЕ-ШАБЛОННОСТЬ: если бы ты видел 20 слайдов подряд из этой же деки,
   этот выглядел бы отличимым от остальных?
6. СООТВЕТСТВИЕ БРИФУ: соответствует ли ритму/доминирующему приёму из брифа?
7. ЭМОЦИОНАЛЬНЫЙ ВЕС: если это climax/hook — ощущается ли смена темпа?
   Если bridge/quiet — не перетягивает ли внимание больше, чем должен?
Слайд получает PASS, только если ВСЕ 7 пунктов — PASS."""

REPORT_SUFFIX = ".vision_qa.json"


def _report_path(html_path: str) -> Path:
    return Path(html_path).with_suffix(REPORT_SUFFIX)


def _load_report(html_path: str) -> dict:
    p = _report_path(html_path)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"rubric": RUBRIC, "slides": {}}


def _save_report(html_path: str, report: dict) -> None:
    _report_path(html_path).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def cmd_shoot(args) -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("vision_qa: playwright недоступен — скриншоты не созданы", file=sys.stderr)
        return 1
    out_dir = Path(args.out_dir)
    out_dir.mkdir(exist_ok=True, parents=True)
    shots = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 900})
        page.goto(Path(args.html).resolve().as_uri())
        page.wait_for_timeout(600)
        n = page.evaluate("document.querySelectorAll('.slide').length")
        for i in range(n):
            page.evaluate(
                "(i) => document.querySelectorAll('.slide').forEach((s, j) => "
                "s.classList.toggle('active', j === i))", i)
            page.wait_for_timeout(450)  # дождаться конца CSS-transition
            shot = out_dir / f"slide-{i + 1:02d}.jpg"
            page.screenshot(path=str(shot), type="jpeg", quality=90)
            shots.append(shot)
        browser.close()

    report = _load_report(args.html)
    report["total_slides"] = len(shots)
    report["screenshots"] = [str(s) for s in shots]
    _save_report(args.html, report)

    print(RUBRIC)
    print()
    print(f"Скриншотов: {len(shots)}. Теперь ПОСМОТРИ на каждый файл ниже и оцени "
          f"по рубрике выше, затем запиши вердикт командой "
          f"`vision_qa.py record {args.html} --slide N --verdict ...`:")
    for i, s in enumerate(shots, start=1):
        print(f"  {i}: {s}")
    return 0


def cmd_record(args) -> int:
    report = _load_report(args.html)
    checks = {}
    for c in args.check or []:
        if "=" not in c:
            print(f"vision_qa: --check должен быть вида 'пункт=PASS|FAIL', получено: {c}", file=sys.stderr)
            return 2
        k, v = c.split("=", 1)
        checks[k.strip()] = v.strip().upper()
    report.setdefault("slides", {})[str(args.slide)] = {
        "verdict": args.verdict.upper(),
        "checks": checks,
        "recommendation": args.recommendation or "",
    }
    _save_report(args.html, report)
    print(f"vision_qa: слайд {args.slide} записан как {args.verdict.upper()}")
    return 0


def cmd_finalize(args) -> int:
    report = _load_report(args.html)
    total = report.get("total_slides", 0)
    slides = report.get("slides", {})
    if not total:
        print("vision_qa: нет данных о числе слайдов — сначала запусти `shoot`", file=sys.stderr)
        return 2
    missing = [i for i in range(1, total + 1) if str(i) not in slides]
    failed = {k: v for k, v in slides.items() if v.get("verdict") != "PASS"}
    report["verdict"] = "PASS" if not missing and not failed else "FAIL"
    report["missing"] = missing
    _save_report(args.html, report)
    if missing:
        print(f"vision_qa: FAIL — не оценено вручную: слайды {missing}. "
              f"Это НЕ пропуск проверки — без реального просмотра слайд не может "
              f"считаться принятым.", file=sys.stderr)
    for k, v in failed.items():
        print(f"vision_qa: слайд {k} — FAIL: {v.get('recommendation', '(без рекомендации)')}", file=sys.stderr)
    print(f"vision_qa итог: {report['verdict']}")
    return 0 if report["verdict"] == "PASS" else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("shoot", help="скриншотить каждый слайд + напечатать рубрику")
    sp.add_argument("html")
    sp.add_argument("--out-dir", default="vision_shots")
    sp.set_defaults(func=cmd_shoot)

    rp = sub.add_parser("record", help="записать вердикт агента по одному слайду")
    rp.add_argument("html")
    rp.add_argument("--slide", type=int, required=True)
    rp.add_argument("--verdict", required=True, choices=["PASS", "FAIL", "pass", "fail"])
    rp.add_argument("--check", action="append", help="пункт=PASS|FAIL, можно повторять")
    rp.add_argument("--recommendation", default="")
    rp.set_defaults(func=cmd_record)

    fp = sub.add_parser("finalize", help="посчитать итоговый вердикт по деке")
    fp.add_argument("html")
    fp.set_defaults(func=cmd_finalize)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
