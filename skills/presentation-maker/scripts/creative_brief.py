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
import hashlib
import json
import sys
from pathlib import Path

# Каталог ритмов и сигнатурных приёмов — выбор ограничен смыслом (goal/длина),
# но ВНУТРИ допустимого подмножества варьируется по seed конкретной деки
# (название + тема + аудитория), а не только по goal — иначе любые две деки
# одного goal получают одинаковый бриф (это и была причина "все деки одинаковые").
RHYTHMS = ("dense-punchy", "airy-editorial", "data-forward", "narrative-slow")

SIGNATURE_CATALOG = [
    {
        "move": "climax-single-number",
        "description": "каждый climax-слайд — одна огромная цифра и минимум текста",
        "render_rule": {"climax": "hero-number-only"},
    },
    {
        "move": "climax-rail-number",
        "description": "climax-слайд: цифра прижата к левому краю на всю высоту, подпись справа мелко",
        "render_rule": {"climax": "hero-number-rail"},
    },
    {
        "move": "numbered-sections",
        "description": "номера разделов крупно слева, всё остальное — чисто",
        "render_rule": {"all": "index-num-large"},
    },
    {
        "move": "climax-isolated-card",
        "description": "climax-слайд: единственная карточка по центру, весь остальной холст — пустой",
        "render_rule": {"climax": "hero-number-isolated"},
    },
]


def _seed(spec: dict) -> str:
    """Seed деки для выбора художественных решений — НЕ равен deck_seed()
    из composer.py (тот же принцип, но своя соль), намеренно завязан на
    title+topic+audience, чтобы разные темы получали разные решения даже
    при одинаковом goal и похожем числе слайдов."""
    parts = [spec.get("title", ""), spec.get("topic", ""), spec.get("audience", ""),
             spec.get("goal", "")]
    return "::".join(str(p).strip().lower() for p in parts)


def _h(seed: str, salt: str) -> int:
    return int(hashlib.sha256(f"{seed}::{salt}".encode()).hexdigest(), 16)


def _pick(seed: str, salt: str, options):
    return options[_h(seed, salt) % len(options)]


def pick_rhythm(spec: dict, profile: dict) -> str:
    goal = spec.get("goal", "")
    n = len(spec.get("slides", []))
    seed = _seed(spec)
    # смысловое ограничение (что уместно для goal/длины), выбор внутри — по seed
    if goal == "pitch":
        pool = RHYTHMS if n <= 12 else tuple(r for r in RHYTHMS if r != "dense-punchy")
    elif goal in ("report", "edu"):
        pool = ("data-forward", "narrative-slow")
    else:
        pool = ("airy-editorial", "narrative-slow", "dense-punchy")
    return _pick(seed, "rhythm", pool)


def pick_signature(spec: dict, profile: dict) -> dict:
    """Сигнатурный приём: машинно-читаемое правило рендера + описание.
    Выбор ограничен наличием climax-слайдов, но внутри допустимого набора —
    по seed деки, не всегда один и тот же приём."""
    climaxes = [k for k, v in profile.items() if v.get("emphasis") == "dominant"]
    seed = _seed(spec)
    if climaxes:
        pool = [c for c in SIGNATURE_CATALOG if "climax" in c["move"]]
        chosen = dict(_pick(seed, "signature", pool))
        chosen["applies_to"] = [int(k) for k in climaxes]
        return chosen
    chosen = dict(next(c for c in SIGNATURE_CATALOG if c["move"] == "numbered-sections"))
    chosen["applies_to"] = []
    return chosen


def climax_treatment(spec: dict, profile: dict) -> dict:
    """Инструкция per-slide для climax-слайдов. Читает реальные metrics
    из spec (profile хранит только геометрию, не сырые данные слайда)."""
    slides = spec.get("slides", [])
    out = {}
    for k, v in profile.items():
        if v.get("emphasis") != "dominant":
            continue
        idx = int(k)
        if idx < 1 or idx > len(slides):
            continue
        raw = slides[idx - 1]
        metrics = raw.get("metrics") or []
        if not metrics:
            continue
        label_len = v.get("geometry", {}).get("max_label_len", 0)
        out[str(idx)] = (f"полноэкранная ключевая метрика, заголовок скромнее, "
                         f"подпись до {label_len} символов мелким капсом")
    return out


def build_brief(spec: dict, profile: dict) -> dict:
    seed = _seed(spec)
    rhythm = pick_rhythm(spec, profile)
    signature = pick_signature(spec, profile)
    # избегаемые приёмы тоже варьируются — набор-кандидат минус то, что уже
    # выбрано сигнатурой, чтобы не противоречить самому себе
    avoid_pool = [
        "одинаковая структура на каждом bullets-слайде",
        "декоративные элементы на climax-слайдах",
        "одна и та же интенсивность акцента на соседних слайдах",
        "крупный decor на слайде с длинным заголовком",
    ]
    avoid = [avoid_pool[i] for i in sorted({_h(seed, f"avoid{n}") % len(avoid_pool) for n in range(2)})]
    return {
        "seed": seed,
        "rhythm": rhythm,
        "signature_move": signature,
        "climax_treatment": climax_treatment(spec, profile),
        "avoid": avoid or avoid_pool[:2],
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
