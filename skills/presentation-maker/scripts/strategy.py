#!/usr/bin/env python3
"""Topic -> strategy selector for the presentation-maker pipeline.

Чистый stdlib. Функция select_strategy() превращает цель презентации (goal) в
набор решений уровня «продакт-дизайн»: нарративную дугу (arc), эстетический
режим (mood), плотность контента (density), имя ближайшей темы (palette_name)
и рекомендованный набор лейаутов (layouts).

Рациональность маппинга опирается на references/product-designer.md
(модуль «Продакт-дизайнер»):

  Дуги (product-designer.md, раздел A):
    - Problem->Solution->Proof->CTA : аудитория ещё не знакома с проблемой
      (боль -> решение -> доказательства -> один призыв).
    - Sparkline (Duarte)            : нужно убедить / большая идея,
      чередование «что есть» <-> «что могло бы быть» на протяжении деки.
    - STAR                          : доказать компетенцию кейсом
      (Situation->Task->Action->Result, один слайд = один кейс).
    - S.T.A.R. Moment               : одна шокирующая цифра/поворот.

  Консалтинг vs питч vs кинот (product-designer.md, раздел A):
    - консалтинг — пирамида (Minto) + SCQA, плотные данные, assertion-заголовки,
      аудитория читает сама -> text-heavy, swiss/executive, table/chart/metrics.
    - питч — проблема/решение/рынок/тракция/команда/CTA, 10 минут, метрики ->
      concise, glass/swift, title/metrics/comparison/closing.
    - кинот (keynote) — sparkline, эмоциональная дуга, минимум текста ->
      concise, editorial/dark, big_number/quote/divider.

Эстетические режимы (mood) взяты из references/design-system.md (раздел 5.4):
swiss / editorial / flat / glass / dark. Это и есть валидное перечисление для
поля theme.mood в deck.json. Имена «swift / executive / standard / modern»,
фигурирующие в ТЗ как «mood», на деле являются ИМЕНАМИ файлов тем
(templates/themes/*.json), поэтому они отражены в DEFAULT_THEMES как
palette_name, а не как mood.

Доступные файлы тем (skills/deck-html/templates/themes/):
general, modern, executive, momentum, swift, standard, dynamic.
DEFAULT_THEMES сопоставляет каждый валидный mood с ближайшей по характеру темой.
"""
from __future__ import annotations

import argparse
import json
import sys

# Валидные цели презентации (совпадает с deck.json -> goal).
VALID_GOALS = ("pitch", "consulting", "keynote", "report", "edu")

# Валидные эстетические режимы (design-system.md 5.4; deck.json theme.mood).
VALID_MOODS = ("swiss", "editorial", "flat", "glass", "dark")

# Нарративная дуга по цели (product-designer.md, раздел A).
GOAL_ARC = {
    "pitch": "problem-solution-proof-cta",
    "consulting": "problem-solution-proof-cta",  # пирамида Minto / SCQA
    "keynote": "sparkline",                        # или star-moment
    "report": "problem-solution-proof-cta",
    "edu": "star",                                 # STAR-кейс на слайд
}

# Эстетический режим по цели (design-system.md 5.4).
GOAL_MOOD = {
    "pitch": "glass",       # swift-тема имеет mood "glass"
    "consulting": "swiss",  # executive-тема -> строгая сетка
    "keynote": "editorial", # или dark
    "report": "swiss",      # standard-тема имеет mood "editorial", но отчёт
                            # строже -> swiss; см. DEFAULT_THEMES
    "edu": "flat",          # modern-тема -> ровные карточки/бенто
}

# Плотность контента по цели (deck-outline SKILL.md, verbosity).
GOAL_DENSITY = {
    "pitch": "concise",     # ~20 слов/слайд
    "consulting": "text-heavy",  # аудитория читает сама
    "keynote": "concise",
    "report": "standard",   # ~40 слов/слайд
    "edu": "standard",
}

# Рекомендованный набор лейаутов по цели (зеркалит RENDERERS build_html.py).
GOAL_LAYOUTS = {
    "pitch": ["title", "bullets", "metrics", "comparison", "closing"],
    "consulting": ["table", "chart", "metrics", "bullets"],
    "keynote": ["big_number", "quote", "divider"],
    "report": ["table", "chart", "process"],
    "edu": ["bullets", "process", "feature"],
}

# Ближайшая существующая тема (templates/themes/<name>.json) для каждого mood.
DEFAULT_THEMES = {
    "swiss": "executive",
    "editorial": "standard",
    "flat": "modern",
    "glass": "swift",
    "dark": "dynamic",
}

# Ключевые слова для эвристического вывода цели, если она не задана явно.
_GOAL_KEYWORDS = {
    "pitch": ("pitch", "investor", "инвестор", "стартап", "funding", "раунд", "питч"),
    "consulting": ("consulting", "консалт", "совет", "board", "стратеги", "пирамид", "scqa"),
    "keynote": ("keynote", "конференц", "выступл", "доклад", "тед", "ted"),
    "report": ("report", "отчёт", "отчет", "квартал", "quarterly", "репорт", "дашборд"),
    "edu": ("edu", "обучен", "курс", "урок", "учеб", "lecture", "туториал"),
}


def _infer_goal(audience: str | None, topic: str | None) -> str | None:
    """Эвристический вывод цели по аудитории/теме (только если goal не задан)."""
    hay = " ".join(x for x in (audience, topic) if x).lower()
    if not hay:
        return None
    for goal, kws in _GOAL_KEYWORDS.items():
        if any(kw in hay for kw in kws):
            return goal
    return None


def select_strategy(goal: str | None = None,
                    audience: str | None = None,
                    topic: str | None = None,
                    language: str | None = None) -> dict:
    """Подобрать стратегию презентации по цели.

    Аргументы:
        goal:     одна из VALID_GOALS; если None/неизвестна — выводится по
                  audience/topic, иначе дефолт "pitch".
        audience: описание аудитории (для эвристики и будущих расширений).
        topic:    тема (для эвристики).
        language: "ru"/"en" (пробрасывается в вывод для справки).

    Возвращает dict:
        {
          "goal": str,            # нормализованная цель
          "arc": str,             # нарративная дуга
          "mood": str,            # эстетический режим (из VALID_MOODS)
          "density": str,         # concise|standard|text-heavy
          "palette_name": str,    # имя файла темы (templates/themes/<name>.json)
          "layouts": [str],       # рекомендованные лейауты
        }
    """
    goal = (goal or "").strip().lower()
    if goal not in VALID_GOALS:
        goal = _infer_goal(audience, topic) or "pitch"

    mood = GOAL_MOOD[goal]
    return {
        "goal": goal,
        "arc": GOAL_ARC[goal],
        "mood": mood,
        "density": GOAL_DENSITY[goal],
        "palette_name": DEFAULT_THEMES[mood],
        "layouts": list(GOAL_LAYOUTS[goal]),
        # language пробрасываем отдельно — он не влияет на стратегию,
        # но полезен вызывающей стороне для логов.
        "language": language,
    }


def _preset_row(goal: str) -> dict:
    """One preset summary row for --list / --show."""
    return {
        "goal": goal,
        "arc": GOAL_ARC.get(goal, ""),
        "mood": GOAL_MOOD.get(goal, ""),
        "density": GOAL_DENSITY.get(goal, ""),
        "palette_name": DEFAULT_THEMES.get(GOAL_MOOD.get(goal, ""), ""),
        "layouts": list(GOAL_LAYOUTS.get(goal, [])),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Select presentation strategy by goal")
    ap.add_argument("--goal", default=None, help="pitch|consulting|keynote|report|edu")
    ap.add_argument("--audience", default=None, help="audience description (for inference)")
    ap.add_argument("--topic", default=None, help="topic (for inference)")
    ap.add_argument("--language", default=None, help="ru|en")
    ap.add_argument("--list", action="store_true", help="list all strategy presets")
    ap.add_argument("--show", metavar="GOAL", default=None,
                    help="show one preset in detail (pitch|consulting|keynote|report|edu)")
    args = ap.parse_args()

    if args.list:
        print(json.dumps([_preset_row(g) for g in VALID_GOALS],
                         ensure_ascii=False, indent=2))
        return 0
    if args.show:
        goal = (args.show or "").strip().lower()
        if goal not in VALID_GOALS:
            print(f"unknown goal: {args.show} (valid: {', '.join(VALID_GOALS)})")
            return 2
        print(json.dumps(_preset_row(goal), ensure_ascii=False, indent=2))
        return 0

    strat = select_strategy(args.goal, args.audience, args.topic, args.language)
    print(json.dumps(strat, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
