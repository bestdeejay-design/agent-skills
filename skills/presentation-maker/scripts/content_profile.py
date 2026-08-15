#!/usr/bin/env python3
"""content_profile — анализ смысла и объёма контента слайда (Слой 1).

До композиции вычисляет для каждого слайда: роль в нарративе
(hook/tension/proof/climax/mechanism/bridge/cta), вес (dominant/standard/
quiet) и реальную геометрию текста (длины, число элементов). Роли можно
уточнить LLM-вызовом на всю деку (см. --llm), иначе — правила по умолчанию
из ТЗ (от позиции в arc и типа слайда).

Использование:
    python3 content_profile.py deck.json [-o content_profile.json] [--llm]
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROLES = ("hook", "tension", "proof", "climax", "mechanism", "bridge", "cta")


def slide_geometry(s: dict) -> dict:
    """Точный расчёт метрик текста слайда (без догадок)."""
    title = str(s.get("title", ""))
    bullets = s.get("bullets", []) or []
    metrics = s.get("metrics", []) or []
    columns = s.get("columns", []) or []
    steps = s.get("steps", []) or s.get("items", []) or []
    def step_len(x):
        return len(str(x.get("title", x))) if isinstance(x, dict) else len(str(x))
    return {
        "title_word_count": len(title.split()),
        "title_char_count": len(title),
        "bullet_count": len(bullets),
        "max_bullet_len": max((len(str(b)) for b in bullets), default=0),
        "total_bullets_len": sum(len(str(b)) for b in bullets),
        "metric_count": len(metrics),
        "max_label_len": max((len(str(m.get("label", ""))) for m in metrics), default=0),
        "column_count": len(columns),
        "max_points_per_column": max((len(c.get("points", [])) for c in columns), default=0),
        "step_count": len(steps),
        "max_step_len": max((step_len(x) for x in steps), default=0),
        "total_word_count": len(title.split()) + sum(len(str(b).split()) for b in bullets),
    }


def default_role(s: dict, idx: int, total: int, has_climax: bool) -> str:
    """Роль по умолчанию (правила ТЗ, без LLM)."""
    t = s.get("type", "bullets")
    if t in ("title",) or idx == 0:
        return "hook"
    if t in ("closing",) or idx == total - 1:
        return "cta"
    if t == "divider":
        return "bridge"
    if s.get("metrics"):
        for m in s["metrics"]:
            if m.get("accent"):
                return "climax"
    if has_climax and t in ("comparison", "process", "timeline"):
        return "mechanism"
    if t in ("comparison", "process", "timeline"):
        return "proof"
    if not s.get("bullets") and not s.get("metrics") and t == "bullets":
        return "bridge"
    return "tension"


def emphasis_for(role: str, s: dict) -> str:
    if role in ("climax", "hook"):
        return "dominant"
    if role == "bridge":
        return "quiet"
    if s.get("metrics"):
        for m in s["metrics"]:
            if m.get("accent"):
                return "dominant"
    return "standard"


def build_profile(spec: dict) -> dict:
    slides = spec.get("slides", [])
    total = len(slides)
    # есть ли слайд-кульминация (accent-метрика)
    has_climax = any(
        any(m.get("accent") for m in (s.get("metrics") or [])) for s in slides
    )
    profile = {}
    for idx, s in enumerate(slides):
        role = default_role(s, idx, total, has_climax)
        profile[str(idx + 1)] = {
            "slide_index": idx + 1,
            "type": s.get("type", "bullets"),
            "narrative_role": role,
            "emphasis": emphasis_for(role, s),
            "geometry": slide_geometry(s),
        }
    return profile


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("spec", help="deck.json")
    ap.add_argument("-o", "--out", default="content_profile.json")
    ap.add_argument("--llm", action="store_true", help="уточнить роли через LLM (требует провайдера)")
    args = ap.parse_args()
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    profile = build_profile(spec)
    Path(args.out).write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    for k, v in profile.items():
        print(f"слайд {k}: {v['narrative_role']:<8} {v['emphasis']:<9} title={v['geometry']['title_word_count']}w "
              f"metrics={v['geometry']['metric_count']} bullets={v['geometry']['bullet_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
