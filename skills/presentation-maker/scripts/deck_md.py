#!/usr/bin/env python3
"""Parse an authoring Markdown file (deck.md) into the normalized deck.json spec.

Pipeline (цель консолидации deck-outline + deck-html + deck-pptx):
    deck.md  --(deck_md.py)-->  deck.json  --(build_html.py)-->  slides.html
                                                  --(build_pptx.py)--> deck.pdf

Использование:
    python3 deck_md.py deck.md [--out deck.json]

Формат deck.md
==============
1) Лидирующий frontmatter между строками `---`:
       ---
       title: Название деки
       goal: pitch            # pitch|consulting|keynote|report|edu
       audience: инвесторы SaaS
       language: ru           # ru|en
       theme: swift           # имя темы (general/modern/executive/momentum/
                              #   swift/standard/dynamic) ИЛИ mood
                              #   (swiss/editorial/flat/glass/dark)
       density: concise       # concise|standard|text-heavy
       topic: выход на рынок
       ---

2) Блоки слайдов, разделённые строкой, содержащей ТОЛЬКО `---`.
   Каждый блок начинается с `# Заголовок` (assertion-headline слайда),
   далее тело. Соглашения по телу (прагматично, при неоднозначности -> bullets):

     * `- пункт`                     -> bullets
     * `> цитата`  / `> — автор`     -> quote (след. строка `> — ` = attribution)
     * таблица Markdown `| a | b |`  -> table
     * `columns:` + `### Кол A`      -> comparison (подзаголовки + буллеты)
     * `metrics:` список `знач — подпись` -> metrics
     * `steps:` нумерованные пункты  -> process
     * `image: путь`                 -> image_showcase
     * `presenter:` / `date:`        -> title (или closing, если последний)
     * только `subtitle:`            -> divider
     * `type: <slide_type>`          -> явное переопределение лейаута

Выходная схема deck.json СТРОГО совпадает с ожиданиями build_html.py
(см. RENDERERS / _theme / pal_vars). После разбора вызывается
strategy.select_strategy(), чтобы заполнить goal/theme.mood/strategy, если они
не заданы во frontmatter.

Чистый stdlib. Без PyYAML.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Чтобы `import strategy` работал независимо от cwd при запуске скрипта.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import strategy  # noqa: E402

# Валидные типы слайдов (зеркалят RENDERERS в build_html.py).
VALID_SLIDE_TYPES = {
    "title", "divider", "bullets", "comparison", "table", "chart", "process",
    "metrics", "feature", "big_number", "quote", "table_of_contents", "timeline",
    "image_showcase", "centered_header", "kpi_row", "logos", "closing",
}

# Имена файлов тем (skills/presentation-maker/templates/themes/*.json).
THEME_NAMES = {"general", "modern", "executive", "momentum", "swift", "standard", "dynamic"}

# Путь к темам (skills/presentation-maker/templates/themes).
_THEMES_DIR = (
    Path(__file__).resolve().parent.parent / "templates" / "themes"
)

# Ключи палитры, принимаемые build_html.py (функция _theme / pal_vars).
_PALETTE_KEYS = (
    "primary", "background", "card", "stroke", "background_text", "primary_text",
    "muted", "accent_soft", "accent", "font", "font_display", "font_url", "mood",
    "radius", "radius_sm", "eyebrow_track",
)


# --------------------------------------------------------------------------- #
# Frontmatter
# --------------------------------------------------------------------------- #
def parse_frontmatter(text: str) -> dict:
    """Минимальный парсер `key: value` (без PyYAML).

    Устойчив к лидирующим пробелам в ключах (YAML-подобный стиль).
    Поддерживает один уровень вложенности для `palette:` (опционально).
    """
    fm: dict = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", stripped)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val == "":
            # Возможный вложенный блок (строки с отступом).
            nested: dict = {}
            j = i + 1
            while j < len(lines) and (lines[j].startswith("  ") or lines[j].startswith("\t")):
                nm = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", lines[j].strip())
                if nm:
                    nested[nm.group(1)] = nm.group(2).strip()
                j += 1
            fm[key] = nested if nested else ""
            i = j
            continue
        fm[key] = val
        i += 1
    return fm


# --------------------------------------------------------------------------- #
# Утилиты разбора тела слайда
# --------------------------------------------------------------------------- #
def _meta(body: list[str], key: str) -> str | None:
    """Найти строку `key: value` в теле слайда."""
    for line in body:
        m = re.match(rf"^\s*{key}:\s*(.*)$", line)
        if m:
            return m.group(1).strip()
    return None


def _collect_bullets(body: list[str]) -> list[str]:
    out = []
    for line in body:
        s = line.strip()
        if s.startswith("- "):
            out.append(s[2:].strip())
    return out


def _is_assertion(title: str) -> bool:
    """Заголовок-вывод (assertion headline): полное предложение с точкой/!?."""
    t = title.strip()
    return bool(t) and t[-1] in ".!?" and len(t.split()) >= 4


def _has_table(body: list[str]) -> bool:
    table_lines = [l for l in body if l.strip().startswith("|")]
    if len(table_lines) < 2:
        return False
    sep = any(re.match(r"^\s*\|[\s:|-]+\|\s*$", l) for l in table_lines)
    return sep


def _split_row(line: str) -> list[str]:
    return [p.strip() for p in line.strip().strip("|").split("|")]


# --------------------------------------------------------------------------- #
# Парсеры конкретных лейаутов
# --------------------------------------------------------------------------- #
def _parse_table(title: str, body: list[str]) -> dict:
    rows_raw = [l.strip() for l in body if l.strip().startswith("|")]
    headers = _split_row(rows_raw[0])
    data_rows: list[list[str]] = []
    for l in rows_raw[1:]:
        # пропускаем сепаратор | --- | --- |
        inner = l.strip().strip("|").replace("|", "")
        if set(inner) <= set("-: "):
            continue
        data_rows.append(_split_row(l))
    return {
        "type": "table",
        "title": title,
        "table": {"headers": headers, "rows": data_rows},
    }


def _parse_quote(title: str, body: list[str]) -> dict:
    quote = ""
    attrib = None
    for line in body:
        s = line.strip()
        if not s.startswith("> "):
            continue
        content = s[2:].strip()
        if content[:1] in ("—", "–") or content.startswith("--"):
            attrib = content.lstrip("—–- ").strip()
        else:
            quote = content
    slide: dict = {"type": "quote", "title": title, "quote": quote}
    if attrib:
        slide["attribution"] = attrib
    return slide


def _parse_columns(title: str, body: list[str]) -> dict:
    columns: list[dict] = []
    cur_heading: str | None = None
    cur_points: list[str] = []
    started = False
    for line in body:
        if "columns:" in line:
            started = True
            continue
        if not started:
            continue
        m = re.match(r"^#{2,4}\s+(.*)$", line)  # ### Колонка A
        if m:
            if cur_heading is not None:
                columns.append({"heading": cur_heading, "points": cur_points})
            cur_heading = m.group(1).strip()
            cur_points = []
        else:
            s = line.strip()
            if s.startswith("- "):
                cur_points.append(s[2:].strip())
            elif s and cur_heading is not None and cur_points:
                cur_points[-1] += " " + s
    if cur_heading is not None:
        columns.append({"heading": cur_heading, "points": cur_points})
    return {"type": "comparison", "title": title, "columns": columns}


def _parse_metrics(title: str, body: list[str]) -> dict:
    metrics: list[dict] = []
    started = False
    for line in body:
        if "metrics:" in line:
            started = True
            continue
        if not started:
            continue
        s = line.strip()
        if not s:
            continue
        item = re.sub(r"^\d+\.\s+", "", s).lstrip("- ").strip()
        parts = re.split(r"\s+[—–]\s+|\s+-\s+", item)
        if len(parts) >= 2:
            value, label = parts[0].strip(), " — ".join(parts[1:]).strip()
        else:
            value, label = item, ""
        accent = value.endswith("*")
        if accent:
            value = value[:-1].strip()
        metrics.append({"value": value, "label": label, **({"accent": True} if accent else {})})
    return {"type": "metrics", "title": title, "metrics": metrics}


def _parse_steps(title: str, body: list[str]) -> dict:
    steps: list[str] = []
    started = False
    for line in body:
        if "steps:" in line:
            started = True
            continue
        if not started:
            continue
        s = line.strip()
        if not s:
            continue
        m = re.match(r"^\d+\.\s+(.*)$", s)
        if m:
            steps.append(m.group(1).strip())
        elif s.startswith("- "):
            steps.append(s[2:].strip())
        elif steps:
            steps[-1] += " " + s
    return {"type": "process", "title": title, "steps": steps}


def _parse_block(block: str, index: int, is_last: bool) -> dict:
    """Разобрать один блок слайда в словарь slide-спецификации."""
    lines = block.split("\n")
    title = ""
    body_start = 0
    for idx, line in enumerate(lines):
        if re.match(r"^#\s+\S", line):  # ровно один '#' — заголовок слайда
            title = line[1:].strip()
            body_start = idx + 1
            break
    body = lines[body_start:]

    # Явное переопределение лейаута (прагматичное расширение).
    explicit = _meta(body, "type")
    if explicit and explicit in VALID_SLIDE_TYPES:
        return _build_explicit(explicit, title, body)

    # image_showcase
    img = _meta(body, "image")
    if img:
        slide: dict = {"type": "image_showcase", "title": title, "image": img}
        desc = _meta(body, "desc")
        if desc:
            slide["desc"] = desc
        points = _collect_bullets(body)
        if points:
            slide["points"] = points
        return slide

    # table
    if _has_table(body):
        return _parse_table(title, body)

    # quote
    if any(l.strip().startswith("> ") for l in body):
        return _parse_quote(title, body)

    # comparison
    if any("columns:" in l for l in body):
        return _parse_columns(title, body)

    # metrics
    if any("metrics:" in l for l in body):
        return _parse_metrics(title, body)

    # process
    if any("steps:" in l for l in body):
        return _parse_steps(title, body)

    # title / closing (по мета-полям speaker/date)
    presenter = _meta(body, "presenter")
    date = _meta(body, "date")
    subtitle = _meta(body, "subtitle")
    if presenter or date:
        if is_last:
            return {"type": "closing", "title": title,
                    **({"subtitle": subtitle} if subtitle else {}),
                    **({"presenter": presenter} if presenter else {}),
                    **({"date": date} if date else {})}
        return {"type": "title", "title": title,
                **({"subtitle": subtitle} if subtitle else {}),
                **({"presenter": presenter} if presenter else {}),
                **({"date": date} if date else {})}

    # divider (только subtitle, без буллетов)
    bullets = _collect_bullets(body)
    if subtitle and not bullets:
        return {"type": "divider", "title": title, "subtitle": subtitle}

    # default: bullets
    return {"type": "bullets", "title": title, "bullets": bullets,
            "assertion": _is_assertion(title)}


def _build_explicit(stype: str, title: str, body: list[str]) -> dict:
    """Собрать слайд при явном `type:` — переиспользуем авто-парсеры по смыслу."""
    # Для явно заданных типов пытаемся извлечь осмысленное тело;
    # иначе отдаём минимальный корректный словарь (bullets/title и т.п.).
    if stype == "table" and _has_table(body):
        return _parse_table(title, body)
    if stype == "quote":
        return _parse_quote(title, body)
    if stype == "comparison":
        return _parse_columns(title, body)
    if stype == "metrics":
        return _parse_metrics(title, body)
    if stype == "process":
        return _parse_steps(title, body)
    if stype == "image_showcase":
        img = _meta(body, "image") or ""
        slide = {"type": "image_showcase", "title": title, "image": img}
        desc = _meta(body, "desc")
        if desc:
            slide["desc"] = desc
        points = _collect_bullets(body)
        if points:
            slide["points"] = points
        return slide
    if stype in ("title", "closing"):
        presenter = _meta(body, "presenter")
        date = _meta(body, "date")
        subtitle = _meta(body, "subtitle")
        slide = {"type": stype, "title": title}
        if subtitle:
            slide["subtitle"] = subtitle
        if presenter:
            slide["presenter"] = presenter
        if date:
            slide["date"] = date
        return slide
    if stype == "divider":
        subtitle = _meta(body, "subtitle")
        slide = {"type": "divider", "title": title}
        if subtitle:
            slide["subtitle"] = subtitle
        return slide
    # bullets / feature / big_number / chart / timeline / toc / logos / kpi / centered
    bullets = _collect_bullets(body)
    if bullets:
        return {"type": stype, "title": title, "bullets": bullets}
    return {"type": stype, "title": title}


# --------------------------------------------------------------------------- #
# Тема / палитра
# --------------------------------------------------------------------------- #
def _load_theme_palette(name: str) -> dict:
    """Загрузить палитру из templates/themes/<name>.json (только чтение)."""
    p = _THEMES_DIR / f"{name}.json"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except OSError:
        return {}
    pal: dict = {}
    for k in _PALETTE_KEYS:
        if k in data:
            pal[k] = data[k]
    graphs = data.get("graphs", [])
    for i, g in enumerate(graphs[:5]):
        pal[f"graph_{i}"] = g
    return pal


def _resolve_theme(fm: dict, strat: dict) -> dict:
    """Собрать theme: {name, mood, palette} из frontmatter + стратегии."""
    fm_theme = (fm.get("theme") or "").strip()
    if fm_theme in THEME_NAMES:
        name = fm_theme
        mood = _load_theme_palette(name).get("mood") or strat["mood"]
    elif fm_theme in strategy.VALID_MOODS:
        mood = fm_theme
        name = strategy.DEFAULT_THEMES[fm_theme]
    elif fm_theme and (_THEMES_DIR / f"{fm_theme}.json").exists():
        # Кастомная тема роутера (presentation-craft): любой файл в templates/themes/.
        name = fm_theme
        mood = _load_theme_palette(name).get("mood") or strat["mood"]
    else:
        name = strat["palette_name"]
        mood = strat["mood"]

    palette = _load_theme_palette(name)
    return {"name": name, "mood": mood, "palette": palette}


# --------------------------------------------------------------------------- #
# Валидация
# --------------------------------------------------------------------------- #
def validate(spec: dict) -> list[str]:
    """Вернуть список ошибок (пустой => валидно)."""
    errors: list[str] = []
    if not isinstance(spec.get("title"), str) or not spec.get("title"):
        errors.append("title: обязателен и должен быть непустой строкой")
    if spec.get("goal") not in strategy.VALID_GOALS:
        errors.append(f"goal: должен быть одним из {strategy.VALID_GOALS}")
    slides = spec.get("slides")
    if not isinstance(slides, list) or not slides:
        errors.append("slides: должен быть непустым списком")
    else:
        for i, s in enumerate(slides, start=1):
            if not isinstance(s, dict):
                errors.append(f"slides[{i}]: не словарь")
                continue
            t = s.get("type")
            if t not in VALID_SLIDE_TYPES:
                errors.append(f"slides[{i}].type: '{t}' не валиден")
    return errors


# --------------------------------------------------------------------------- #
# Сборка спецификации
# --------------------------------------------------------------------------- #
def build_spec(md_text: str, overrides: dict | None = None) -> tuple[dict, list[str]]:
    """Разобрать deck.md в (deck.json, warnings).

    *overrides* — необязательный dict CLI-ключей (goal/audience/language/theme/
    tone), которые перекрывают соответствующие поля frontmatter, если заданы.
    """
    warnings: list[str] = []

    # 1) frontmatter
    if not md_text.lstrip().startswith("---"):
        raise ValueError("deck.md должен начинаться с frontmatter (--- ... ---)")
    end = md_text.find("\n---", 3)
    if end == -1:
        raise ValueError("не закрыт frontmatter (второй '---')")
    fm = parse_frontmatter(md_text[3:end])
    body = md_text[end + 4:]

    # CLI-перекрытия frontmatter (только явно заданные ключи).
    if overrides:
        for key in ("goal", "audience", "language", "theme", "tone"):
            if overrides.get(key):
                fm[key] = overrides[key]

    if not fm.get("title"):
        raise ValueError("frontmatter: обязателен 'title'")

    # 2) блоки слайдов
    lines = body.split("\n")
    blocks: list[str] = []
    cur: list[str] = []
    for line in lines:
        if line.strip() == "---":
            if cur:
                blocks.append("\n".join(cur))
                cur = []
        else:
            cur.append(line)
    if cur:
        blocks.append("\n".join(cur))
    blocks = [b for b in blocks if b.strip()]

    if not blocks:
        raise ValueError("нет ни одного блока слайда после frontmatter")

    slides = [_parse_block(b, i, i == len(blocks) - 1)
              for i, b in enumerate(blocks)]

    # 3) стратегия (дозаполняет goal/theme.mood/strategy при необходимости)
    goal = fm.get("goal")
    inferred = strategy._infer_goal(fm.get("audience"), fm.get("topic"))
    if not goal and inferred:
        warnings.append(f"goal не задан во frontmatter; выведен из темы/аудитории: '{inferred}'")
    strat = strategy.select_strategy(
        goal, fm.get("audience"), fm.get("topic"), fm.get("language")
    )

    theme = _resolve_theme(fm, strat)

    strategy_block = {
        "arc": strat["arc"],
        "density": fm.get("density") or strat["density"],
        "layouts": strat["layouts"],
    }

    spec: dict = {
        "title": fm["title"],
        "goal": strat["goal"],
        "theme": theme,
        "strategy": strategy_block,
        "slides": slides,
    }
    if fm.get("topic"):
        spec["topic"] = fm["topic"]
    if fm.get("audience"):
        spec["audience"] = fm["audience"]
    if fm.get("language"):
        spec["language"] = fm["language"]
    if fm.get("tone"):
        spec["tone"] = fm["tone"]
    if fm.get("style"):
        spec["style"] = fm["style"]

    return spec, warnings


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description="Convert deck.md authoring file to deck.json")
    ap.add_argument("md", help="path to deck.md (topic or outline file)")
    ap.add_argument("-o", "--out", default="deck.json", help="output deck.json path")
    ap.add_argument("--goal", default=None, help="pitch|consulting|keynote|report|edu")
    ap.add_argument("--audience", default=None, help="target audience (for strategy inference)")
    ap.add_argument("--tone", default=None, help="tone/voice override (stored as spec.tone)")
    ap.add_argument("--palette", default=None, help="theme name or mood (overrides frontmatter theme)")
    ap.add_argument("--lang", "--language", dest="language", default=None,
                    help="ru|en (overrides frontmatter language)")
    args = ap.parse_args()

    overrides = {
        "goal": args.goal,
        "audience": args.audience,
        "tone": args.tone,
        "theme": args.palette,
        "language": args.language,
    }
    try:
        md_text = Path(args.md).read_text(encoding="utf-8")
        spec, warnings = build_spec(md_text, overrides)
    except (ValueError, OSError) as e:
        print(f"ОШИБКА разбора: {e}", file=sys.stderr)
        return 1

    errors = validate(spec)
    if errors:
        for e in errors:
            print(f"ОШИБКА валидации: {e}", file=sys.stderr)
        return 1

    Path(args.out).write_text(
        json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    for w in warnings:
        print(f"  ! {w}")
    print(f"deck.json записан: {args.out}")
    print(f"  слайдов: {len(spec['slides'])}")
    print(f"  goal:     {spec['goal']}")
    print(f"  mood:     {spec['theme']['mood']} (тема: {spec['theme']['name']})")
    print(f"  arc:      {spec['strategy']['arc']}")
    print(f"  density:  {spec['strategy']['density']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
