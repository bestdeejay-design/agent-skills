#!/usr/bin/env python3
"""creative_brief — арт-дирекшн на уровне деки (Слой 2).

Одно художественное решение на всю деку (ритм, сигнатурный приём,
climax-подача), чтобы дека №30 не походила на №1, но была цельной.
Генерируется по правилам из контента + опционально уточняется LLM.

Использование:
    python3 creative_brief.py deck.json --profile content_profile.json
                                        [-o creative_brief.json] [--llm]
"""
import argparse
import json
import sys
from pathlib import Path

# Каталог ритмов: когда какой уместен (детерминированные правила)
RHYTHMS = ("dense-punchy", "airy-editorial", "data-forward", "narrative-slow")


def pick_rhythm(spec: dict, profile: dict) -> str:
    goal = spec.get("goal", "")
    n = len(spec.get("slides", []))
    if goal == "pitch":
        return "dense-punchy" if n <= 12 else "narrative-slow"
    if goal in ("report", "edu"):
        return "data-forward"
    return "airy-editorial"


def pick_signature(spec: dict, profile: dict) -> dict:
    """Сигнатурный приём: машинно-читаемое правило рендера + описание."""
    # сколько climax-слайдов (по profile) — от этого зависит приём
    climaxes = [k for k, v in profile.items() if v.get("emphasis") == "dominant"]
    if climaxes:
        return {
            "move": "climax-single-number",
            "description": "каждый climax-слайд — одна огромная цифра и минимум текста",
            "render_rule": {"climax": "hero-number-only"},
            "applies_to": [int(k) for k in climaxes],
        }
    return {
        "move": "numbered-sections",
        "description": "номера разделов крупно слева, всё остальное — чисто",
        "render_rule": {"all": "index-num-large"},
        "applies_to": [],
    }


def climax_treatment(spec: dict, profile: dict) -> dict:
    out = {}
    for k, v in profile.items():
        if v.get("emphasis") == "dominant" and v.get("metrics"):
            idx = int(k)
            label = v["geometry"].get("max_label_len", 0)
            out[str(idx)] = (f"полноэкранная ключевая метрика, заголовок скромнее, "
                             f"подпись до {label} символов мелким капсом")
    return out


def build_brief(spec: dict, profile: dict) -> dict:
    rhythm = pick_rhythm(spec, profile)
    signature = pick_signature(spec, profile)
    return {
        "rhythm": rhythm,
        "signature_move": signature,
        "climax_treatment": climax_treatment(spec, profile),
        "avoid": ["одинаковая структура на каждом bullets-слайде",
                  "декоративные элементы на climax-слайдах"],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("spec", help="deck.json")
    ap.add_argument("--profile", default="content_profile.json")
    ap.add_argument("-o", "--out", default="creative_brief.json")
    ap.add_argument("--llm", action="store_true", help="уточнить бриф через LLM")
    args = ap.parse_args()
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    profile = {}
    if Path(args.profile).exists():
        profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    brief = build_brief(spec, profile)
    Path(args.out).write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(brief, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
