#!/usr/bin/env python3
"""Build autonomous slides.html from a JSON spec + the skill's HTML template.

Usage:
    python build_html.py deck.json slides.html
    python build_html.py --demo demo.html

Takes the template at <skill>/templates/slides.html, injects the palette into
:root and replaces the demo <section class="slide"> blocks with real ones built
from the spec (same shape as build_pptx.py).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from patterns import PATTERNS, FALLBACK_PATTERN, pick_pattern  # generative layout layer
from composer import compose_slide, deck_seed
import content_profile as _cp   # Слой 1: роли/вес/геометрия слайдов
import creative_brief as _cb    # Слой 2: художественное направление деки
import fit_solver as _fs        # Слой 3: геометрическая проверка до финализации


def _wrap_title_word(html: str) -> str:
    """Wrap the first word of every h1/h2 title in <span class="accent-word">.

    The accent color marks a whole word (never a lone letter floating away
    from its word), so the title keeps its rhythm and the accent stays
    readable. Used only for slides with the accent-word mode.
    """
    import re

    def repl(m):
        tag, content = m.group(1), m.group(2)
        words = content.split(" ", 1)
        if not words:
            return m.group(0)
        first = esc(words[0])
        rest = esc(words[1]) if len(words) > 1 else ""
        inner = f'<span class="accent-word">{first}</span>' + (f" {rest}" if rest else "")
        return f"<{tag}>{inner}</{tag}>"

    return re.sub(r"<(h[12])>([^<]*)</\1>", repl, html)


def pick_accent_mode(layout: str, used: list) -> str:
    """Spread the second brand color (var(--accent)) across the deck.

    Three ways to embed the accent without mixing it with primary:
    word (first title word in accent), underline (hairline under title),
    icons (metric icons + values). Rotates modes, never repeats the
    mode used on the previous slide, and skips accent-icons unless
    the slide actually renders metric cards.
    """
    if not used:
        return "accent-word"
    prev = used[-1] if used else None
    if layout == "metrics" or layout == "big_number":
        pool = ("accent-icons", "accent-word")
    else:
        pool = ("accent-word", "accent-underline")
    for m in pool:
        if m != prev:
            return m
    return pool[0]

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "templates" / "base.html"
PATTERN_CSS_DIR = SKILL_DIR / "templates" / "pattern-css"


def esc(t: str) -> str:
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _head(spec: dict, idx: int) -> str:
    return (
        f'<div class="slide-head">'
        f'<span class="logo">●</span>'
        f'<span class="page-ind">{idx:02d}</span></div>'
    )


def render_title(s) -> str:
    meta = " · ".join(x for x in [s.get("presenter"), s.get("date")] if x)
    return (
        '<section class="slide title"><h1>' + esc(s.get("title", "")) + "</h1>"
        + ('<p class="subtitle">' + esc(s.get("subtitle", "")) + "</p>" if s.get("subtitle") else "")
        + (f'<p class="meta-line">{esc(meta)}</p>' if meta else "")
        + "</section>"
    )


def render_divider(s) -> str:
    return (
        '<section class="slide divider"><h2>' + esc(s.get("title", "")) + "</h2>"
        + ('<p class="subtitle">' + esc(s.get("subtitle", "")) + "</p>" if s.get("subtitle") else "")
        + "</section>"
    )


def render_bullets(s) -> str:
    bullets = s.get("bullets", [])
    structure = s.get("_comp", {}).get("structure", "list")
    title = f'<h2>{esc(s.get("title", ""))}</h2>'
    head = _head(s, s.get("_n", 0))

    if structure == "columns":
        # двухколоночный разворот: номера продолжаются сквозным счётом через
        # обе колонки (было: каждая колонка нумеровалась с 01 заново)
        half = (len(bullets) + 1) // 2
        def col(items, start):
            return "".join(
                f'<div class="col-item" data-num="{i:02d}"><span class="col-num">{i:02d}</span>'
                f'<span class="col-text">{esc(b)}</span></div>'
                for i, b in enumerate(items, start)
            )
        body = (f'<div class="spread-grid"><div class="spread-col">{col(bullets[:half], 1)}</div>'
                f'<div class="spread-col">{col(bullets[half:], half + 1)}</div></div>')
    elif structure == "bars":
        # горизонтальные полосы с заполнением
        bars = "".join(
            f'<div class="bar-row" style="--fill:{max(15, 92 - idx * 14)}%">'
            f'<span class="bar-label">{esc(b)}</span>'
            f'<span class="bar-track"><span class="bar-fill"></span></span></div>'
            for idx, b in enumerate(bullets)
        )
        body = f'<div class="bars-block">{bars}</div>'
    elif structure == "grid":
        # сетка карточек 2×2
        cards = "".join(
            f'<div class="fact-card" data-num="{i:02d}"><span class="fact-num">{i:02d}</span>'
            f'<span class="fact-text">{esc(b)}</span></div>'
            for i, b in enumerate(bullets, 1)
        )
        body = f'<div class="fact-grid">{cards}</div>'
    else:
        # list — классический список
        lis = "".join(
            f'<li data-num="{idx + 1:02d}"><span class="bullet-text">{esc(b)}</span>'
            f'<span class="bullet-arrow">→</span></li>'
            for idx, b in enumerate(bullets)
        )
        body = f'<ul class="bullet-list">{lis}</ul>'

    return f'<section class="slide">{head}{title}{body}</section>'


def _metric_num(value) -> float:
    """Числовое значение метрики для сортировки (лестница роста)."""
    s = str(value).replace(" ", "").replace(",", ".")
    m = re.search(r"-?\d+(\.\d+)?", s)
    return float(m.group(0)) if m else 0.0


def _icon(name) -> str:
    """Return inline SVG from templates/icons/<name>.svg, or '' if missing."""
    if not name:
        return ""
    p = Path(SKILL_DIR) / "templates" / "icons" / f"{name}.svg"
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        print(f"  ! иконка не найдена: templates/icons/{name}.svg")
        return ""


def render_metrics(s) -> str:
    metrics = s.get("metrics", [])
    structure = s.get("_comp", {}).get("structure", "grid")
    n = len(metrics)
    cols = {2: 2, 3: 3, 4: 4, 6: 3, 8: 4, 9: 3}.get(n, 3)
    head = _head(s, s.get("_n", 0))

    climax_mode = s.get("_climax_mode", "")
    if climax_mode and metrics:
        # Слой 2 (creative_brief): climax-слайд — акцентная метрика (или первая,
        # если ни одна не помечена accent) занимает почти весь холст, заголовок
        # уходит в скромный eyebrow, остальные метрики не показываются вовсе —
        # это физическая смена темпа, а не просто "крупный шрифт".
        hero = next((m for m in metrics if m.get("accent")), metrics[0])
        eyebrow = f'<h2 class="climax-eyebrow">{esc(s.get("title", ""))}</h2>'
        if climax_mode == "hero-number-rail":
            body = (f'<div class="climax-rail">'
                    f'<span class="climax-value">{esc(str(hero.get("value", "")))}</span>'
                    f'<span class="climax-label">{esc(str(hero.get("label", "")))}</span></div>')
        elif climax_mode == "hero-number-isolated":
            body = (f'<div class="climax-isolated"><div class="climax-card">'
                    f'<span class="climax-value">{esc(str(hero.get("value", "")))}</span>'
                    f'<span class="climax-label">{esc(str(hero.get("label", "")))}</span></div></div>')
        else:  # hero-number-only
            body = (f'<div class="climax-hero">'
                    f'<span class="climax-value">{esc(str(hero.get("value", "")))}</span>'
                    f'<span class="climax-label">{esc(str(hero.get("label", "")))}</span></div>')
        return f'<section class="slide climax-slide">{head}{eyebrow}{body}</section>'

    title = f'<h2>{esc(s.get("title", ""))}</h2>'

    if structure == "menu":
        # «меню»: горизонтальные строки — крупная цифра слева, описание справа
        rows = "".join(
            f'<div class="menu-row"><span class="menu-value">{esc(str(m.get("value", "")))}</span>'
            f'<span class="menu-dash"></span>'
            f'<span class="menu-label">{esc(str(m.get("label", "")))}</span></div>'
            for m in metrics
        )
        body = f'<div class="menu-block">{rows}</div>'
    elif structure == "ladder":
        # «лестница роста»: по возрастанию значения, визуальные ступени
        items = sorted(metrics, key=lambda m: _metric_num(m.get("value", "")))
        steps = "".join(
            f'<div class="ladder-step" style="--step:{max(12, 90 - idx * 18)}%">'
            f'<span class="ladder-value">{esc(str(m.get("value", "")))}</span>'
            f'<span class="ladder-label">{esc(str(m.get("label", "")))}</span></div>'
            for idx, m in enumerate(items)
        )
        body = f'<div class="ladder-block">{steps}</div>'
    elif structure == "stats":
        # инлайн-статистика: значения в строку с разделителями
        stats = "".join(
            f'<div class="stat-item"><span class="stat-value">{esc(str(m.get("value", "")))}</span>'
            f'<span class="stat-label">{esc(str(m.get("label", "")))}</span></div>'
            for m in metrics
        )
        body = f'<div class="stats-block">{stats}</div>'
    else:
        # grid — классическая сетка плиток
        compact = any(len(str(m.get("value", ""))) > 7 for m in metrics)
        val_cls = " metric-value-sm" if compact else ""
        cards = []
        for m in metrics:
            svg = _icon(m.get("icon"))
            icon = f'<span class="metric-icon">{svg}</span>' if svg else ""
            accent_cls = " metric-color-accent" if m.get("accent") else ""
            cards.append(
                f'<div class="metric-card">{icon}'
                f'<span class="metric-value{val_cls}{accent_cls}">{esc(str(m.get("value", "")))}</span>'
                f'<span class="metric-label">{esc(str(m.get("label", "")))}</span></div>'
            )
        body = f'<div class="metrics-grid metrics-{cols}">{"".join(cards)}</div>'

    return f'<section class="slide">{head}{title}{body}</section>'


def render_comparison(s) -> str:
    cols = "".join(
        f'<div class="col-card" data-num="0{idx + 1}"><h3>{esc(c.get("heading", ""))}</h3><ul>'
        + "".join(f"<li>{esc(p)}</li>" for p in c.get("points", []))
        + "</ul></div>"
        for idx, c in enumerate(s.get("columns", []))
    )
    n = len(s.get("columns", []))
    cls = " columns" + (f" cols-{n}" if n > 2 else "")
    return (
        '<section class="slide">' + _head(s, s.get("_n", 0))
        + f'<h2>{esc(s.get("title", ""))}</h2>'
        + f'<div class="columns{cls}">{cols}</div></section>'
    )


def render_table(s) -> str:
    t = s.get("table", {})
    hl = t.get("highlight_col")
    headers = "".join(_th(i, h, hl) for i, h in enumerate(t.get("headers", [])))
    cols = max(len(t.get("headers", [])), *(len(r) for r in t.get("rows", [])))
    rows = "".join(
        "<tr>" + "".join(_td(j, c, hl) for j, c in enumerate(row + [""] * (cols - len(row)))) + "</tr>"
        for row in t.get("rows", [])
    )
    return (
        '<section class="slide">' + _head(s, s.get("_n", 0))
        + f'<h2>{esc(s.get("title", ""))}</h2>'
        + '<div class="table-wrap"><table>'
        + '<thead><tr>' + headers + "</tr></thead><tbody>" + rows + "</tbody></table></div></section>"
    )


def _th(i, h, hl):
    if i == hl:
        return f'<th class="hl">{esc(h)}</th>'
    return f"<th>{esc(h)}</th>"


def _td(j, c, hl):
    if j == hl:
        return f'<td class="hl">{esc(c)}</td>'
    return f"<td>{esc(c)}</td>"


def _fmt_val(v) -> str:
    if isinstance(v, float):
        return f"{v:g}".replace(".", ",")
    return str(v)


def render_chart(s) -> str:
    ch = s.get("chart", {})
    cats = ch.get("categories", [])
    # single-series support for template bars; multi-series normalized into first series
    series = ch.get("series", [])
    vals = series[0].get("values", []) if series else []
    maxv = max([v for v in vals if v], default=1) or 1
    classes = ["", " bar-2", " bar-3"]
    bars = []
    for i, cat in enumerate(cats):
        val = vals[i] if i < len(vals) else 0
        h = int(val / maxv * 72)
        h = max(3, min(100, h))
        bar_cls = classes[i % len(classes)]
        bars.append(
            f'<div class="bar-col">'
            f'<span class="bar-value">{_fmt_val(val)}</span>'
            f'<div class="bar{bar_cls}" style="height:{h}%"></div>'
            f'<span class="bar-label">{esc(str(cat))}</span></div>'
        )
    note = ch.get("note")
    note_html = f'<p class="chart-note">{esc(str(note))}</p>' if note else ""
    return (
        '<section class="slide">' + _head(s, s.get("_n", 0))
        + f'<h2>{esc(s.get("title", ""))}</h2>'
        + f'<div class="chart-wrap">{"".join(bars)}</div>'
        + note_html + "</section>"
    )


def render_process(s) -> str:
    steps = s.get("steps", [])
    blocks = []
    for i, st in enumerate(steps):
        arrow = f'<span class="step-arrow">→</span>' if i < len(steps) - 1 else ""
        blocks.append(
            f'<div class="step-card"><div class="step-num">{i + 1:02d}</div>'
            f'<div class="step-text">{esc(st)}</div>{arrow}</div>'
        )
    return (
        '<section class="slide">' + _head(s, s.get("_n", 0))
        + f'<h2>{esc(s.get("title", ""))}</h2>'
        + f'<div class="steps">{"".join(blocks)}</div></section>'
    )


def render_timeline(s) -> str:
    items = s.get("items", [])
    blocks = []
    for i, it in enumerate(items):
        title = it.get("title", "")
        desc = it.get("desc", "") or it.get("text", "")
        blocks.append(
            f'<div class="tl-item"><div class="tl-dot">{i + 1}</div>'
            f'<div class="tl-card"><strong>{esc(str(title))}</strong>'
            + (f'<span>{esc(str(desc))}</span>' if desc else "")
            + "</div></div>"
        )
    return (
        '<section class="slide">' + _head(s, s.get("_n", 0))
        + f'<h2>{esc(s.get("title", ""))}</h2>'
        + f'<div class="timeline">{"".join(blocks)}</div></section>'
    )


def render_image_showcase(s) -> str:
    media = ""
    if s.get("image"):
        media = f'<img src="{esc(s["image"])}" alt="">'
    else:
        media = s.get("emoji", "🖼️")
    points = s.get("points", [])
    body = (f'<h2>{esc(s.get("title", ""))}</h2>'
            + (f'<p>{esc(s.get("desc", ""))}</p>' if s.get("desc") else "")
            + (f'<ul class="bullet-list" style="margin-top:18px">'
               + "".join(f"<li>{esc(b)}</li>" for b in points)
               + "</ul>" if points else ""))
    return (
        '<section class="slide">' + _head(s, s.get("_n", 0))
        + '<div class="showcase"><div class="showcase-media">' + media
        + '</div><div class="showcase-body">' + body + "</div></div></section>"
    )


def render_centered_header(s) -> str:
    return (
        '<section class="slide centered-header">' + _head(s, s.get("_n", 0))
        + f'<h1>{esc(s.get("title", ""))}</h1>'
        + (f'<p class="subtitle">{esc(s.get("subtitle", ""))}</p>' if s.get("subtitle") else "")
        + (f'<div class="subtitle-panel">{esc(s.get("panel", ""))}</div>' if s.get("panel") else "")
        + "</section>"
    )


def render_kpi_row(s) -> str:
    items = s.get("kpis", s.get("metrics"))
    if items is None and s.get("bullets"):
        items = [{"value": b.split(":", 1)[0].strip() if ":" in b else b,
                  "label": b.split(":", 1)[1].strip() if ":" in b else ""} for b in s["bullets"]]
    cards = "".join(
        f'<div class="kpi-card"><div class="kpi-value">{esc(str(k.get("value", "")))}</div>'
        f'<div class="kpi-label">{esc(str(k.get("label", "")))}</div></div>'
        for k in (items or [])
    )
    return (
        '<section class="slide">' + _head(s, s.get("_n", 0))
        + f'<h2>{esc(s.get("title", ""))}</h2>'
        + f'<div class="kpi-row">{cards}</div></section>'
    )


def render_quote(s) -> str:
    attrib = s.get("attribution") or s.get("author") or ""
    head = f'<h2>{esc(str(s.get("title", "")))}</h2>' if s.get("title") else ""
    return (
        '<section class="slide quote-slide">' + _head(s, s.get("_n", 0))
        + head
        + '<span class="quote-mark">“</span>'
        + f'<p class="quote-text">{esc(s.get("quote", ""))}</p>'
        + (f'<p class="quote-attrib">{esc(attrib)}</p>' if attrib else "")
        + "</section>"
    )


def render_big_numbers(s) -> str:
    head = (f'<h2>{esc(str(s.get("title", "")))}</h2>' if s.get("title") else "")
    return (
        '<section class="slide hero-num">' + _head(s, s.get("_n", 0))
        + head
        + f'<div class="hero-value{ " hero-value--accent" if s.get("accent") else "" }">'
        + esc(str(s.get("value", ""))) + "</div>"
        + f'<div class="hero-label">{esc(str(s.get("label", "")))}</div>'
        + (f'<div class="hero-sub">{esc(str(s.get("subtitle", "")))}</div>' if s.get("subtitle") else "")
        + "</section>"
    )


def render_feature_grid(s) -> str:
    items = s.get("features", [])
    cards = []
    for f in items:
        svg = _icon(f.get("icon"))
        icon = f'<div class="feature-icon">{svg}</div>' if svg else ""
        cards.append(
            f'<div class="feature-card">{icon}'
            f'<h3>{esc(str(f.get("title", "")))}</h3>'
            + (f'<p>{esc(str(f.get("text", "")))}</p>' if f.get("text") else "")
            + "</div>"
        )
    grid_cls = f" feature-{max(2, min(4, len(items)))}"
    return (
        '<section class="slide">' + _head(s, s.get("_n", 0))
        + f'<h2>{esc(s.get("title", ""))}</h2>'
        + f'<div class="feature-grid{grid_cls}">{"".join(cards)}</div></section>'
    )


def render_logos(s) -> str:
    tiles = "".join(
        f'<div class="logo-tile">{esc(str(x))}</div>' for x in s.get("logos", [])
    )
    return (
        '<section class="slide">' + _head(s, s.get("_n", 0))
        + f'<h2>{esc(s.get("title", ""))}</h2>'
        + f'<div class="logo-grid">{tiles}</div>'
        + (f'<p class="logo-note">{esc(str(s.get("note", "")))}</p>' if s.get("note") else "")
        + "</section>"
    )


def render_table_of_contents(s) -> str:
    items = s.get("items", [])
    blocks = []
    for i, it in enumerate(items):
        blocks.append(
            f'<div class="toc-item"><span class="toc-num">{i + 1:02d}</span><div>'
            f'<div class="toc-title">{esc(str(it.get("title", "")))}</div>'
            + (f'<div class="toc-desc">{esc(str(it.get("desc", "")))}</div>' if it.get("desc") else "")
            + "</div></div>"
        )
    return (
        '<section class="slide">' + _head(s, s.get("_n", 0))
        + f'<h2>{esc(s.get("title", ""))}</h2>'
        + f'<div class="toc-grid">{"".join(blocks)}</div></section>'
    )


def render_closing(s) -> str:
    meta = " · ".join(x for x in [s.get("presenter")] if x)
    return (
        '<section class="slide closing"><h1>' + esc(s.get("title", "Спасибо!")) + "</h1>"
        + ('<p class="subtitle">' + esc(s.get("subtitle", "")) + "</p>" if s.get("subtitle") else "")
        + (f'<p class="meta-line">{esc(meta)}</p>' if meta else "")
        + "</section>"
    )


RENDERERS = {
    "title": render_title,
    "divider": render_divider,
    "bullets": render_bullets,
    "metrics": render_metrics,
    "comparison": render_comparison,
    "table": render_table,
    "chart": render_chart,
    "process": render_process,
    "timeline": render_timeline,
    "image_showcase": render_image_showcase,
    "centered_header": render_centered_header,
    "kpi_row": render_kpi_row,
    "quote": render_quote,
    "big_number": render_big_numbers,
    "feature": render_feature_grid,
    "logos": render_logos,
    "table_of_contents": render_table_of_contents,
    "closing": render_closing,
}


def _theme(spec: dict) -> dict:
    t = spec.get("theme", {}) or {}
    if isinstance(t.get("palette"), dict):
        return t
    return {"palette": t, **{k: v for k, v in t.items() if k != "palette"}}


FALLBACK_FONTS = ('-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, system-ui, sans-serif')
DESIGN_KEYS = (("mood", "--mood"), ("radius", "--radius"),
               ("radius_sm", "--radius-sm"), ("eyebrow_track", "--eyebrow-track"))


def pick_layout(s: dict, used: list) -> str:
    """Best-fit layout for a slide given its content keys + already used types.

    Rules (product-design module):
    - explicit type wins; 'auto'/missing -> infer from content
    - tables of text -> table; numeric tables -> chart/metrics
    - metrics/big numbers -> metrics or big_number (hero)
    - comparison columns -> comparison; steps -> process
    - timeline items with title+desc -> timeline
    - features with icon+title+text -> feature
    - logos list -> logos; quote -> quote; toc items -> table_of_contents
    - fallback: bullets; avoid repeating the previous slide's type when plausible.
    """
    t = s.get("type") or "auto"
    if t != "auto":
        return t
    prev = used[-1] if used else None
    if s.get("quote") and not s.get("columns"):
        return "quote"
    if s.get("logos"):
        return "logos"
    if s.get("toc") or s.get("table_of_contents"):
        return "table_of_contents"
    if s.get("features"):
        return "feature"
    if s.get("steps"):
        return "process"
    if s.get("items") and any("title" in x or "desc" in x for x in s.get("items", [])):
        return "timeline"
    if s.get("columns"):
        return "comparison"
    if s.get("metrics") and not s.get("table"):
        return "metrics"
    if s.get("big_value") or (s.get("value") and not s.get("table")):
        return "big_number"
    if s.get("table"):
        headers = s["table"].get("headers", [])
        has_nums = any(
            any(str(c).replace(",", ".").replace(" ", "").rstrip("%").isdigit() for c in row)
            for row in s["table"].get("rows", [])[:3]
        )
        return "chart" if (has_nums and len(headers) >= 2) else "table"
    if s.get("bullets"):
        if prev == "bullets" and any(
            ":" in b or "%" in b or "млн" in b or "₽" in b or "млрд" in b for b in s.get("bullets", [])
        ):
            return "kpi_row"
        return "bullets"
    return "closing" if s.get("presenter") and not s.get("title") else "bullets"


def _slide_geometry(s: dict) -> dict:
    """Посчитать геометрию текста слайда на лету (fallback для Слоя 3)."""
    title = str(s.get("title", ""))
    bullets = s.get("bullets", []) or []
    metrics = s.get("metrics", []) or []
    steps = s.get("steps", []) or s.get("items", []) or []
    return {
        "title_word_count": len(title.split()),
        "title_char_count": len(title),
        "bullet_count": len(bullets),
        "max_bullet_len": max((len(str(b)) for b in bullets), default=0),
        "metric_count": len(metrics),
        "max_label_len": max((len(str(m.get("label", ""))) for m in metrics), default=0),
        "step_count": len(steps),
        "max_step_len": max(((len(str(x.get("title", x))) if isinstance(x, dict) else len(str(x)))
                             for x in steps), default=0),
    }


def build(spec: dict, out_path: Path, fit_check: bool = True) -> Path:
    template = TEMPLATE.read_text(encoding="utf-8")
    # Слой 1 (content_profile) и Слой 2 (creative_brief) считаются здесь же,
    # не как отдельные ручные шаги — иначе они остаются мёртвым кодом, который
    # никто не вызывает (это и было причиной, что дека не отличалась от
    # предыдущей: бриф генерировался, но не влиял на рендер).
    profile = _cp.build_profile(spec)
    brief = _cb.build_brief(spec, profile)
    sig = brief.get("signature_move", {})
    climax_indices = set(sig.get("applies_to", []))
    climax_render_rule = sig.get("render_rule", {}).get("climax", "")
    # сохраняем рядом с деком — не для рендера (он уже применён), а для
    # прозрачности/отладки и для vision_qa.py (сверка "соответствует брифу?")
    try:
        Path(str(out_path)).with_suffix(".profile.json").write_text(
            json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
        Path(str(out_path)).with_suffix(".brief.json").write_text(
            json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    fit_report = {}
    theme = _theme(spec)
    palette = theme.get("palette", {})
    font_family = palette.get("font") or theme.get("font") or "Inter"
    font_display = palette.get("font_display") or theme.get("font_display") or font_family
    pal_vars = {
        "--primary": palette.get("primary", "#007AFF"),
        "--background": palette.get("background", "#FFFFFF"),
        "--card": palette.get("card", "#F5F5F7"),
        "--stroke": palette.get("stroke", "#E5E5EA"),
        "--on-primary": palette.get("background_text", "#FFFFFF"),
        "--text": palette.get("primary_text", "#1C1C1E"),
        "--muted": palette.get("muted", "#6E6E73"),
        "--accent-soft": palette.get("accent_soft", "#E8F0FE"),
        "--accent": palette.get("accent", palette.get("primary", "#007AFF")),
        "--graph-0": palette.get("graph_0", "#007AFF"),
        "--graph-1": palette.get("graph_1", "#30B0C7"),
        "--graph-2": palette.get("graph_2", "#5E5CE6"),
        "--graph-3": palette.get("graph_3", "#34C759"),
        "--graph-4": palette.get("graph_4", "#FF9500"),
        "--font": f'"{font_family}", {FALLBACK_FONTS}',
        "--font-display": f'"{font_display}", {FALLBACK_FONTS}',
    }
    for src in (palette, theme):
        for tkey, cvar in DESIGN_KEYS:
            if tkey in src:
                pal_vars[cvar] = str(src[tkey])
    template = _merge_root(template, pal_vars)
    comp_css = _composition_css()
    # реальный CSS деки для Слоя 3 (fit_solver) — без него измерения геометрии
    # бессмысленны: карточки/сетки зависят от .metrics-grid/.col-card и т.п.,
    # которые задаёт именно этот CSS, не голые теги.
    _style_m = re.search(r"<style>(.*?)</style>", template, flags=re.S)
    fit_css = (_style_m.group(1) if _style_m else "") + comp_css

    font_url = palette.get("font_url") or theme.get("font_url")
    if font_url:
        link = f'<link rel="stylesheet" href="{esc(font_url)}">'
        template = template.replace("<!--FONT_LINK-->", link)
    else:
        template = template.replace("<!--FONT_LINK-->", "")

    slides = []
    used_types = []
    style = spec.get("style") or {}
    density = style.get("density") or spec.get("density") or "standard"
    title_slide = next((s for s in spec.get("slides", []) if s.get("type") == "title"), {})
    seed = deck_seed(spec.get("title", "deck"),
                     spec.get("date", "") or title_slide.get("date", "")
                     or spec.get("theme", {}).get("name", ""))
    for i, s in enumerate(spec.get("slides", []), start=1):
        s = dict(s)
        s["_n"] = i
        layout = pick_layout(s, used_types)
        used_types.append(layout)
        dark_slide = layout in ("title", "closing", "divider")
        # геометрия текста (Слой 1): из content_profile, посчитанного выше
        geometry = profile.get(str(i), {}).get("geometry", {})
        if not geometry:
            geometry = _slide_geometry(s)
        is_climax = i in climax_indices
        if is_climax and climax_render_rule:
            s["_climax_mode"] = climax_render_rule

        # Слой 3: рендерим с retry — если геометрическая проверка не проходит,
        # пробуем следующую допустимую комбинацию (до 3 попыток), а не тихо
        # публикуем сломанный слайд.
        best_html, best_comp, best_issues = None, None, None
        for attempt in range(3):
            comp = compose_slide(seed, layout, i, density=density,
                                 content_len=len(s.get("bullets", s.get("metrics", []))),
                                 is_dark=dark_slide, geometry=geometry, attempt=attempt)
            if is_climax:
                # бриф требует пустоты вокруг climax-слайда — без декора
                comp["decor"] = "none"
            s["_comp"] = comp
            accent = comp["accent_mode"]
            s["_accent"] = accent
            renderer = RENDERERS.get(layout, render_bullets)
            html = renderer(s)
            if accent == "word":
                html = _wrap_title_word(html)
            css_vars = (
                f"--comp-title-pos:{comp['title_pos']};"
                f"--comp-title-scale:{comp['title_scale']}px;"
                f"--comp-cols:{comp['cols']};"
                f"--comp-content:{comp['content_layout']};"
                f"--comp-accent-level:{comp['accent_level']};"
                f"--comp-radius:{comp['radius']}px;"
                f"--comp-shadow:{comp['shadow']};"
            )
            html = html.replace('<section class="slide',
                                f'<section class="slide pat-{comp["recipe"]} accent-{accent} decor-{comp["decor"]} '
                                f'title-{comp["title_variant"]} marker-{comp["marker_variant"]} '
                                f'card-{comp["card_variant"]} metric-{comp["metric_variant"]}" style="{css_vars}"', 1)
            if not fit_check:
                best_html, best_comp, best_issues = html, comp, []
                break
            ok, issues = _fs.check_slide(html, geometry, is_dominant=is_climax, base_css=fit_css)
            if ok or best_html is None:
                best_html, best_comp, best_issues = html, comp, issues
            if ok:
                break
        fit_report[str(i)] = {"pass": not best_issues, "attempts": attempt + 1, "issues": best_issues}
        slides.append(best_html)

    slides_html = "\n\n  " + "\n\n  ".join(slides)
    template = _replace_deck(template, slides_html)
    mood = pal_vars.get("--mood", "")
    if mood:
        template = template.replace('<div class="deck" id="deck">',
                                    f'<div class="deck" id="deck" data-mood="{esc(mood)}">')
    # fresh title
    template = template.replace("<title>Презентация</title>",
                                f"<title>{esc(spec.get('title', 'Презентация'))}</title>")
    # generate CSS for the composition variables used by every slide
    template = template.replace("<!--PATTERN_CSS-->", comp_css)
    out_path.write_text(template, encoding="utf-8")
    try:
        Path(str(out_path)).with_suffix(".fit_report.json").write_text(
            json.dumps(fit_report, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    failed = {k: v for k, v in fit_report.items() if not v["pass"]}
    if failed:
        print(f"fit_solver: {len(failed)} слайд(ов) не прошли геометрическую проверку "
              f"даже после retry — см. {Path(str(out_path)).with_suffix('.fit_report.json')}",
              file=sys.stderr)
        for k, v in failed.items():
            print(f"  слайд {k}: {v['issues']}", file=sys.stderr)
    return out_path


def _composition_css() -> str:
    """CSS, реализующий параметры композиции (переменные --comp-*).

    Каждая композиция реально перестраивает layout слайда (а не только
    позицию заголовка): row-раскладка «заголовок слева + контент справа»,
    вертикальный заголовок, число колонок контента (grid), plain-контент
    без карточек, скругление и тень. Значения приходят из composer.py
    (детерминированный синтез из seed) — каждая дека уникальна.
    """
    return """
/* ============ Позиция заголовка: полная перестройка layout ============ */
/* Заголовок слева → row: заголовок 38% слева, контент 55% справа */
.slide[style*="--comp-title-pos:left"] { flex-direction: row; justify-content: center; align-items: center; gap: 5%; }
.slide[style*="--comp-title-pos:left"] > h1,
.slide[style*="--comp-title-pos:left"] > h2 {
    width: 34%; flex-shrink: 0; text-align: left; align-self: center; margin: 0;
    font-family: var(--font-display);
}
.slide[style*="--comp-title-pos:left"] > .bullet-list,
.slide[style*="--comp-title-pos:left"] > .metrics-grid,
.slide[style*="--comp-title-pos:left"] > .col-card,
.slide[style*="--comp-title-pos:left"] > .steps-wrap,
.slide[style*="--comp-title-pos:left"] > .tl-wrap,
.slide[style*="--comp-title-pos:left"] > .table-wrap {
    width: 55%; flex-shrink: 0; margin: 0; max-width: none;
}
/* Заголовок по центру → column (базовый), но с явным центрированием */
.slide[style*="--comp-title-pos:center"] > h1,
.slide[style*="--comp-title-pos:center"] > h2 { text-align: center; }
/* Вертикальный заголовок → слева-вертикально, контент справа */
.slide[style*="--comp-title-pos:vertical"] { flex-direction: row; align-items: stretch; gap: 4%; }
.slide[style*="--comp-title-pos:vertical"] > h1,
.slide[style*="--comp-title-pos:vertical"] > h2 {
    writing-mode: vertical-rl; text-align: left; margin: 0;
    width: auto; max-height: 70vh; font-family: var(--font-display);
    align-self: flex-start; padding: 0 8px;
    border-left: 5px solid var(--primary);
}
.slide[style*="--comp-title-pos:vertical"] > .bullet-list,
.slide[style*="--comp-title-pos:vertical"] > .metrics-grid,
.slide[style*="--comp-title-pos:vertical"] > .col-card,
.slide[style*="--comp-title-pos:vertical"] > .steps-wrap,
.slide[style*="--comp-title-pos:vertical"] > .tl-wrap,
.slide[style*="--comp-title-pos:vertical"] > .table-wrap {
    flex: 1; margin: 0; max-width: none;
}
/* Заголовок снизу-слева → журнальный финал */
.slide[style*="--comp-title-pos:bottom-left"] { justify-content: flex-end; align-items: flex-start; }
.slide[style*="--comp-title-pos:bottom-left"] > h1,
.slide[style*="--comp-title-pos:bottom-left"] > h2 {
    text-align: left; margin: 0 0 5vh; max-width: 70%; font-family: var(--font-display);
}
.slide[style*="--comp-title-pos:bottom-left"] > .bullet-list,
.slide[style*="--comp-title-pos:bottom-left"] > .metrics-grid { align-self: flex-start; }

/* ============ Масштаб заголовка ============ */
.slide[style*="--comp-title-scale"] > h1,
.slide[style*="--comp-title-scale"] > h2 { font-size: var(--comp-title-scale); }

/* ============ Число колонок контента (grid) ============ */
.slide[style*="--comp-cols:2"] > .bullet-list,
.slide[style*="--comp-cols:2"] > .metrics-grid,
.slide[style*="--comp-cols:2"] > .steps-wrap { display: grid; grid-template-columns: repeat(2, 1fr); }
.slide[style*="--comp-cols:3"] > .bullet-list,
.slide[style*="--comp-cols:3"] > .metrics-grid,
.slide[style*="--comp-cols:3"] > .steps-wrap { display: grid; grid-template-columns: repeat(3, 1fr); }
.slide[style*="--comp-cols:2"] > .bullet-list, .slide[style*="--comp-cols:3"] > .bullet-list { gap: 16px; }

/* ============ Layout контента ============ */
/* plain: без карточек — чистый список с разделителями */
.slide[style*="--comp-content:plain"] > .bullet-list li,
.slide[style*="--comp-content:plain"] > .metric-card {
    background: transparent; border: none; box-shadow: none; padding: 12px 4px;
    border-bottom: 1px solid var(--stroke); border-radius: 0;
}
/* split: два широких блока (только для 4-5 элементов) */
.slide[style*="--comp-content:split"] > .bullet-list { max-width: 1250px; }

/* ============ Скругление и тень ============ */
.slide[style*="--comp-radius"] > .bullet-list li,
.slide[style*="--comp-radius"] > .metric-card,
.slide[style*="--comp-radius"] > .col-card,
.slide[style*="--comp-radius"] > .step-card,
.slide[style*="--comp-radius"] > .tl-card { border-radius: var(--comp-radius); }
.slide[style*="--comp-shadow:soft"] > .bullet-list li,
.slide[style*="--comp-shadow:soft"] > .metric-card { box-shadow: var(--shadow-soft); }
.slide[style*="--comp-shadow:strong"] > .bullet-list li,
.slide[style*="--comp-shadow:strong"] > .metric-card { box-shadow: var(--shadow-hover); }

/* ============ Climax-режим (Слой 2: creative_brief signature_move) ============ */
/* Единственный акцентный элемент занимает почти весь холст — физическая
   смена темпа на слайде-кульминации, а не просто увеличенный шрифт. */
.slide.climax-slide { justify-content: center; align-items: center; }
.climax-eyebrow {
    position: absolute; top: 64px; left: 50%; transform: translateX(-50%);
    font: 700 13px/1 var(--font); letter-spacing: .12em; text-transform: uppercase;
    color: var(--muted); max-width: 70%; text-align: center;
}
.climax-hero, .climax-isolated { display: flex; flex-direction: column; align-items: center; gap: 12px; }
.climax-value {
    font: 800 clamp(96px, 13vw, 180px)/1 var(--font-display); color: var(--primary);
    letter-spacing: -0.02em;
}
.climax-label { font: 500 22px/1.4 var(--font); color: var(--muted); max-width: 640px; text-align: center; }
.climax-rail {
    display: flex; flex-direction: column; align-items: flex-start; gap: 8px;
    position: absolute; left: 96px; top: 50%; transform: translateY(-50%);
}
.climax-rail .climax-value { font-size: clamp(80px, 11vw, 150px); }
.climax-rail .climax-label { text-align: left; }
.climax-isolated .climax-card {
    background: var(--card); border: 1px solid var(--stroke); border-radius: 28px;
    padding: 64px 96px; box-shadow: var(--shadow-hover);
    display: flex; flex-direction: column; align-items: center; gap: 12px;
}
"""


def palette_vars_ordered(pal_vars: dict):
    items = list(pal_vars.items())
    return items


def _merge_root(template: str, overrides: dict) -> str:
    """Return template with :root block merged: given overrides replace existing
    CSS variable values in-place; new tokens are appended. Never drops the
    design-system tokens baked into the template."""
    import re
    m = re.search(r"(:root\s*)\{([^{}]*)\}", template, flags=re.S)
    if not m:
        return template
    prefix, inner = m.group(1), m.group(2)
    lines_out = []
    covered = set()
    for line in inner.split("\n"):
        var = re.match(r"\s*(--[\w-]+):\s*([^;]+);", line)
        if var:
            name = var.group(1)
            covered.add(name)
            if name in overrides:
                lines_out.append(f"    {name}: {overrides[name]};")
                continue
        lines_out.append(line)
    for name, value in overrides.items():
        if name not in covered:
            lines_out.append(f"    {name}: {value};")
    new_block = prefix + "{\n" + "\n".join(lines_out) + "\n}"
    return template[: m.start()] + new_block + template[m.end() :]


def _replace_deck(template: str, slides_html: str) -> str:
    import re
    # deck opening div then replace everything up to the closing </div> that closes deck.
    # Simpler: split on the closing line right before <div class="nav-hint">
    marker = '<div class="nav-hint">'
    idx = template.index(marker)
    # find the deck open token
    open_token = '<div class="deck" id="deck">'
    oi = template.find(open_token)
    opener_end = oi + len(open_token)
    # keep opener + slides, drop all in-between, keep from marker
    return template[:opener_end] + "\n" + slides_html + "\n" + template[idx:]


def main() -> int:
    ap = argparse.ArgumentParser(description="Build slides.html from presentation spec")
    ap.add_argument("spec", nargs="?", help="JSON spec file")
    ap.add_argument("out", nargs="?", help="output slides.html path")
    ap.add_argument("--save-case", default="", help="имя case для памяти скилла (examples/cases/<name>/)")
    args = ap.parse_args()
    if not args.spec or not args.out:
        ap.print_help()
        return 2
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    out = build(spec, Path(args.out))
    print(f"Slides written: {out} ({len(spec.get('slides', []))} slides)")
    if args.save_case:
        from cases import save_case
        case_dir = save_case(args.save_case, spec, {}, Path(args.out))
        print(f"Case сохранён: {case_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())