"""Layout patterns — единый селектор композиций для build_html.py и build_pptx.py.

Паттерны = композиционные схемы, независимые от типа контента. Один контент
может быть отрисован разными паттернами -> разные композиции. Селектор в момент
сборки выбирает паттерн для каждого слайда: контент (fits) + разнообразие
(не повторять соседние) + тренд деки (style.family) + плотность.
"""
import json
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
PATTERNS_DIR = SKILL_DIR / "templates" / "patterns"
FALLBACK_PATTERN = "swiss-grid"


def load_patterns() -> list:
    out = []
    if not PATTERNS_DIR.is_dir():
        return out
    for f in sorted(PATTERNS_DIR.glob("*.json")):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"  ! паттерн не загружен: {f.name} ({e})")
    return out


PATTERNS = load_patterns()


def get_pattern(pid: str) -> dict:
    for p in PATTERNS:
        if p.get("id") == pid:
            return p
    return {}


def pick_pattern(layout: str, used: list, family: str = "", density: str = "standard") -> str:
    if not PATTERNS:
        return FALLBACK_PATTERN
    cands = [p for p in PATTERNS if layout in p.get("fits", [])]
    if not cands:
        return FALLBACK_PATTERN
    # Variety first: never repeat a pattern used on any of the last 3 slides.
    recent = set(used[-3:])
    fresh = [p for p in cands if p["id"] not in recent]
    pool = fresh or cands
    # Density preference.
    dense = [p for p in pool if density in p.get("density", [])]
    pool = dense or pool
    # Family is a preference, not a hard filter: prefer family patterns but fall
    # back to other families when the requested one can't keep the deck varied.
    if family:
        fam = [p for p in pool if p.get("family") == family]
        if len(fam) >= 2 or not fresh:
            pool = fam
        else:
            fam_id = {p["id"] for p in fam}
            others = [p for p in pool if p["id"] not in fam_id]
            if others:
                pool = others + fam
    counts = {p["id"]: used.count(p["id"]) for p in pool}
    return min(pool, key=lambda p: counts[p["id"]])["id"]


# Паттерны с заголовком слева (для PPTX: меняем позицию заголовка)
LEFT_TITLE_PATTERNS = {"hero-left", "editorial-asym", "swiss-grid", "vertical-rail", "z-pattern",
                       "split-frame", "sparkline-metric", "vertical-stepper", "zigzag-timeline", "recap-grid"}
# Паттерны, где заголовок по центру / внизу
CENTER_TITLE_PATTERNS = {"big-type", "split-diagonal", "card-dashboard"}
