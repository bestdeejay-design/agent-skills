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
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "templates" / "slides.html"


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
    lis = "".join(f"<li>{esc(b)}</li>" for b in s.get("bullets", []))
    return (
        '<section class="slide">' + _head(s, s.get("_n", 0))
        + f'<h2>{esc(s.get("title", ""))}</h2>'
        + f'<ul class="bullet-list">{lis}</ul></section>'
    )


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
    n = len(metrics)
    cols = {2: 2, 3: 3, 4: 4, 6: 3, 8: 4, 9: 3}.get(n, 3)
    grid_cls = f" metrics-{cols}"
    compact = any(len(str(m.get("value", ""))) > 7 for m in metrics)
    val_cls = " metric-value-sm" if compact else ""
    cards = []
    for m in metrics:
        svg = _icon(m.get("icon"))
        icon = f'<span class="metric-icon">{svg}</span>' if svg else ""
        cards.append(
            f'<div class="metric-card">{icon}'
            f'<span class="metric-value{val_cls}">{esc(str(m.get("value", "")))}</span>'
            f'<span class="metric-label">{esc(str(m.get("label", "")))}</span></div>'
        )
    return (
        '<section class="slide">' + _head(s, s.get("_n", 0))
        + f'<h2>{esc(s.get("title", ""))}</h2>'
        + f'<div class="metrics-grid{grid_cls}">{"".join(cards)}</div></section>'
    )


def render_comparison(s) -> str:
    cols = "".join(
        f'<div class="col-card"><h3>{esc(c.get("heading", ""))}</h3><ul>'
        + "".join(f"<li>{esc(p)}</li>" for p in c.get("points", []))
        + "</ul></div>"
        for c in s.get("columns", [])
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


def build(spec: dict, out_path: Path) -> Path:
    template = TEMPLATE.read_text(encoding="utf-8")
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

    font_url = palette.get("font_url") or theme.get("font_url")
    if font_url:
        link = f'<link rel="stylesheet" href="{esc(font_url)}">'
        template = template.replace("<!--FONT_LINK-->", link)
    else:
        template = template.replace("<!--FONT_LINK-->", "")

    slides = []
    used_types = []
    for i, s in enumerate(spec.get("slides", []), start=1):
        s = dict(s)
        s["_n"] = i
        layout = pick_layout(s, used_types)
        used_types.append(layout)
        renderer = RENDERERS.get(layout, render_bullets)
        slides.append(renderer(s))

    slides_html = "\n\n  " + "\n\n  ".join(slides)
    template = _replace_deck(template, slides_html)
    mood = pal_vars.get("--mood", "")
    if mood:
        template = template.replace('<div class="deck" id="deck">',
                                    f'<div class="deck" id="deck" data-mood="{esc(mood)}">')
    # fresh title
    template = template.replace("<title>Презентация</title>",
                                f"<title>{esc(spec.get('title', 'Презентация'))}</title>")
    out_path.write_text(template, encoding="utf-8")
    return out_path


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
    args = ap.parse_args()
    if not args.spec or not args.out:
        ap.print_help()
        return 2
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    out = build(spec, Path(args.out))
    print(f"Slides written: {out} ({len(spec.get('slides', []))} slides)")
    return 0


if __name__ == "__main__":
    sys.exit(main())