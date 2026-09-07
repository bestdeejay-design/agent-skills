#!/usr/bin/env python3
"""Build a self-contained Bento presentation (*.bento.html) from deck.json.

Bento (https://github.com/nyblnet/bento, MIT) is an office suite in one HTML
file: the .bento.html IS the editor + presenter + document. Its document is
plain JSON in exactly one <script type="application/bento+json" id="bento-doc">
block. This stage is a SIBLING of build_pptx.py — same deck.json in, a
different artifact out — and qa_bento.py is its gate.

We do NOT reimplement Bento's runtime and do NOT build it from source. We fetch
the official prebuilt app shell (pinned version, cached under ~/.cache) and
splice the generated document JSON into that single block, leaving the rest of
the shell byte-identical.

Bento's document model uses ABSOLUTE px on a 1280x720 canvas with 96px margins,
which is what makes its signature morph transition work: elements sharing an
id (morph key) across adjacent slides tween position/size/colour automatically.
Recurring chrome therefore keeps a STABLE id on every slide so it morphs in
place instead of popping.

Fonts are referenced by family stack, not embedded — a family that is neither
embedded in doc.fonts nor a system font will silently fall back on other
machines (qa_bento.py reports this as `font-not-embedded`, info).

Usage:
  python3 build_bento.py deck.json -o deck.bento.html
  python3 build_bento.py deck.json --shell /path/to/Bento_Slides.bento.html
  python3 build_bento.py deck.json --no-download --quiet
Exit codes: 0 = built, 2 = error.
"""
from __future__ import annotations

import argparse
import base64
import datetime as _dt
import json
import mimetypes
import re
import sys
import uuid
from pathlib import Path
from urllib.request import Request, urlopen

# ---- Bento format identity -------------------------------------------------
BENTO_FORMAT = "bento/slides"
BENTO_VERSION = 1

# The app shell is FETCHED at build time and cached, never vendored: Bento is
# MIT (c) 2026 The Bento authors, so we redistribute nothing.
BENTO_SHELL_VERSION = "v1.0.19"
BENTO_SHELL_URL = (
    "https://github.com/nyblnet/bento/releases/download/"
    f"{BENTO_SHELL_VERSION}/Bento_Slides.bento.html"
)
SHELL_MIN_BYTES = 100_000          # an HTML error page must never become a deck
MEDIA_EMBED_BUDGET = 8 * 1024 * 1024   # upstream soft ceiling for data URIs

CACHE_DIR = Path.home() / ".cache" / "presentation-maker" / "bento"

# The ONE editable block in the shell. Tolerates either attribute order.
_DOC_BLOCK = re.compile(
    r'<script([^>]*application/bento\+json[^>]*)>(.*?)</script>',
    re.DOTALL,
)

# ---- Geometry: 1280x720 canvas, 96px margins -------------------------------
W, H = 1280, 720
MARGIN = 96
CONTENT_W = W - 2 * MARGIN          # 1088
RIGHT_EDGE = W - MARGIN             # 1184 — content must not cross this
TITLE_Y, TITLE_H = 72, 84
CONTENT_Y = 208
BOTTOM_STOP = 96                    # content ends no lower than H - 96 = 624
CONTENT_BOTTOM = H - BOTTOM_STOP    # 624
CONTENT_H = CONTENT_BOTTOM - CONTENT_Y   # 416

ACCENT_BAR_Y, ACCENT_BAR_H = 52, 4

# Canonical splits (x positions + widths), gutter included.
COL2 = [(96, 528), (656, 528)]
COL3 = [(96, 340), (470, 340), (844, 340)]
COL4 = [(96, 254), (374, 254), (652, 254), (930, 254)]
SPLIT6040 = [(96, 624), (752, 432)]

# ---- Typography ------------------------------------------------------------
FONT_STACK_TAIL = (
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, "
    "Arial, sans-serif"
)
FS_COVER_TITLE = 76
FS_SLIDE_TITLE = 40
FS_SECTION_TITLE = 56
FS_BODY = 21
FS_LABEL = 17
FS_CAPTION = 15
FS_METRIC = 44
FS_HERO = 128
FS_QUOTE = 34
FS_QUOTE_MARK = 120
BODY_FLOOR = 17          # card/body text floor at 16:9 projection

# ---- Stable chrome ids (morph in place across the whole deck) --------------
ID_CHROME_PAGE = "chrome-page"
ID_CHROME_ACCENT = "chrome-accent"
ID_SLIDE_TITLE = "slide-title"      # content-slide title band
ID_COVER_TITLE = "cover-title"      # cover/divider/closing title band

DARK_SLIDE_TYPES = ("title", "divider", "closing")
ON_DARK_MUTED = "rgba(255,255,255,0.66)"
SCRIM = "rgba(0,0,0,0.45)"

# ---- Slide type set --------------------------------------------------------
SLIDE_TYPES = (
    "title", "divider", "bullets", "comparison", "table", "chart", "process",
    "metrics", "feature", "big_number", "quote", "table_of_contents",
    "timeline", "image_showcase", "centered_header", "kpi_row", "logos",
    "closing",
)


# ===========================================================================
# Small helpers
# ===========================================================================

def _esc(s) -> str:
    """Escape raw text for safe embedding in Bento's inline-HTML subset."""
    return (
        str(s if s is not None else "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


_MD_BOLD = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
_MD_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_MD_UNDER = re.compile(r"(?<!\w)_([^_\n]+)_(?!\w)")
_MD_CODE = re.compile(r"`([^`\n]+)`")


def _md_inline(s) -> str:
    """Escape first, then map the markdown-ish subset Bento's html allows."""
    out = _esc(s)
    out = _MD_BOLD.sub(r"<b>\1</b>", out)
    out = _MD_CODE.sub(r"<code>\1</code>", out)
    out = _MD_ITALIC.sub(r"<i>\1</i>", out)
    out = _MD_UNDER.sub(r"<i>\1</i>", out)
    return out


def _md_block(s) -> str:
    """Inline markdown wrapped in a <p> block."""
    return f"<p>{_md_inline(s)}</p>"


def _bullets_html(items) -> str:
    """A list of strings/dicts -> <ul><li>...</li></ul>."""
    lis = []
    for it in items:
        text = _item_text(it)
        if text:
            lis.append(f"<li>{_md_inline(text)}</li>")
    return f"<ul>{''.join(lis)}</ul>" if lis else ""


def _item_text(it) -> str:
    """Normalise a slide sub-item (str | dict) to its primary text."""
    if it is None:
        return ""
    if isinstance(it, str):
        return it.strip()
    if isinstance(it, dict):
        for key in ("text", "title", "value", "label", "name", "heading", "desc"):
            v = it.get(key)
            if isinstance(v, str) and v.strip():
                return v.strip()
        return ""
    if isinstance(it, (int, float)):
        return str(it)
    return str(it).strip()


def _item_get(it, *keys, default=""):
    """Fetch the first present key from a str|dict sub-item."""
    if isinstance(it, dict):
        for k in keys:
            if k in it and it[k] not in (None, ""):
                return it[k]
    return default


def _as_list(v) -> list:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]


def _label(lang: str, ru: str, en: str) -> str:
    return ru if str(lang).lower().startswith("ru") else en


def _upper(s: str) -> str:
    return str(s or "").strip().upper()


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _cols_for(n: int):
    """Pick the canonical split that best fits n items."""
    if n <= 1:
        return [(MARGIN, CONTENT_W)]
    if n == 2:
        return COL2
    if n == 3:
        return COL3
    return COL4


def _even_cols(n: int, gutter: int = 24):
    """n equal columns inside the content box (for n > 4)."""
    n = max(1, n)
    w = (CONTENT_W - (n - 1) * gutter) / n
    return [(MARGIN + i * (w + gutter), w) for i in range(n)]


# ===========================================================================
# Theme mapping: our palette -> Bento theme
# ===========================================================================

_THEME_META_KEYS = {"name", "description", "mood", "palette"}


def _resolve_palette(theme) -> dict:
    """Accept BOTH flat theme files (swift.json) and nested deck.json
    theme.palette; prefer the nested `palette` when both exist."""
    theme = theme if isinstance(theme, dict) else {}
    flat = {k: v for k, v in theme.items() if k not in _THEME_META_KEYS}
    nested = theme.get("palette") if isinstance(theme.get("palette"), dict) else {}
    pal = {**flat, **nested}

    # graphs[] (theme files) is an alternative to graph_0..graph_4 (deck.json).
    graphs = pal.get("graphs")
    if isinstance(graphs, list) and graphs:
        for i, c in enumerate(graphs[:8]):
            pal.setdefault(f"graph_{i}", c)

    if not pal.get("mood"):
        mood = theme.get("mood")
        if mood:
            pal["mood"] = mood
    return pal


def _bento_theme(pal: dict) -> dict:
    background = pal.get("background") or "#FFFFFF"
    color = pal.get("primary_text") or "#1C1C1E"
    accent = pal.get("accent") or pal.get("primary") or "#007AFF"

    font = pal.get("font_display") or pal.get("font") or "Inter"
    family = font if FONT_STACK_TAIL.split(",")[0] in str(font) else f"{font}, {FONT_STACK_TAIL}"

    chart_palette = [
        pal.get(f"graph_{i}") for i in range(8) if pal.get(f"graph_{i}")
    ] or [accent]

    return {
        "background": background,
        "color": color,
        "accent": accent,
        "fontFamily": family,
        "chartPalette": chart_palette,
        "palette": {
            "bg2": pal.get("card") or "#F5F5F7",
            "tx2": pal.get("muted") or "#6E6E73",
            "accent2": accent,
        },
        "table": {
            "headerBg": pal.get("primary") or accent,
            "headerColor": pal.get("background_text") or "#FFFFFF",
            "borderColor": pal.get("stroke") or "#E5E5EA",
            "borderWidth": 1,
            "zebra": "rgba(0,0,0,0.035)",
            "cellPadX": 16,
            "cellPadY": 11,
            "fontSize": 18,
            "fontFamily": family,
            "color": color,
            "radius": 10,
        },
    }


# ===========================================================================
# Element builders — every element always carries the full base field set
# ===========================================================================

def _el(el_id: str, x, y, w, h, **kw) -> dict:
    base = {
        "id": el_id,
        "x": round(float(x), 2),
        "y": round(float(y), 2),
        "w": round(float(w), 2),
        "h": round(float(h), 2),
        "rotation": 0,
        "opacity": 1,
    }
    base.update(kw)
    return base


def _text(el_id, x, y, w, h, html, *, size=FS_BODY, color="#1C1C1E",
          weight=400, align="left", valign="top", lh=1.35, family=None,
          spacing=None, role=None, fx=None, opacity=1.0, **kw) -> dict:
    d = {
        "type": "text",
        "html": html,
        "fontSize": int(size),
        "fontFamily": family or "inherit",
        "fontWeight": int(weight),
        "color": color,
        "align": align,
        "valign": valign,
        "lineHeight": lh,
    }
    if spacing is not None:
        d["letterSpacing"] = spacing
    if role:
        d["role"] = role
    if fx:
        d["fx"] = fx
    if opacity != 1.0:
        d["opacity"] = opacity
    d.update(kw)
    return _el(el_id, x, y, w, h, **d)


def _shape(el_id, x, y, w, h, *, shape="rect", fill="#007AFF", stroke="none",
           stroke_width=0, radius=0, stroke_style=None, fx=None, opacity=1.0,
           shadow=None, **kw) -> dict:
    d = {
        "type": "shape",
        "shape": shape,
        "fill": fill,
        "stroke": stroke,
        "strokeWidth": stroke_width,
        "radius": radius,
    }
    if stroke_style:
        d["strokeStyle"] = stroke_style
    if fx:
        d["fx"] = fx
    if shadow:
        d["shadow"] = shadow
    if opacity != 1.0:
        d["opacity"] = opacity
    d.update(kw)
    return _el(el_id, x, y, w, h, **d)


def _card_shadow(pal: dict) -> dict:
    return {"x": 0, "y": 3, "blur": 10, "color": "rgba(0,0,0,0.09)"}


def _dashed_ring(el_id, x, y, size, color, *, duration=14.0, opacity=0.45) -> dict:
    """Ambient motion for covers/dividers: a slowly marching dashed ring.
    dash-march REQUIRES a dashed/dotted stroke or nothing visibly animates."""
    return _shape(
        el_id, x, y, size, size, shape="ellipse", fill="transparent",
        stroke=color, stroke_width=2, stroke_style="dashed", opacity=opacity,
        fx={"loop": {"type": "dash-march", "distance": 18, "duration": duration}},
    )


def _countup(order=None) -> dict:
    fx = {"countUp": True}
    if order is not None:
        fx["order"] = order
    return fx


def _enter(order=None, kind="fade-up") -> dict:
    fx = {"enter": kind}
    if order is not None:
        fx["order"] = order
    return fx


# ===========================================================================
# Images
# ===========================================================================

def _image_src(value, deck_dir: Path):
    """Resolve an image reference to something Bento can load, or None.

    Bento needs a data URI, an `asset:<key>` ref, or a URL. A local path is
    embedded as a data URI when it exists and fits the 8MB budget.
    """
    if not value or not isinstance(value, str):
        return None
    v = value.strip()
    if v.startswith("data:") or v.startswith("http://") or v.startswith("https://"):
        return v
    if v.startswith("asset:"):
        return v

    for cand in (Path(v), deck_dir / v):
        try:
            p = cand.expanduser().resolve()
        except Exception:
            continue
        if p.is_file():
            try:
                size = p.stat().st_size
            except OSError:
                continue
            if size > MEDIA_EMBED_BUDGET:
                print(f"warning: image {p.name} is {size // 1024}KB, over the "
                      f"{MEDIA_EMBED_BUDGET // (1024 * 1024)}MB embed budget — skipped",
                      file=sys.stderr)
                return None
            mime = mimetypes.guess_type(p.name)[0] or "image/png"
            try:
                b64 = base64.b64encode(p.read_bytes()).decode("ascii")
            except OSError as e:
                print(f"warning: cannot read image {p}: {e}", file=sys.stderr)
                return None
            return f"data:{mime};base64,{b64}"
    print(f"warning: image not found, slide will use a placeholder: {v}",
          file=sys.stderr)
    return None


# ===========================================================================
# Chrome + slide scaffolding
# ===========================================================================

def _chrome(pal: dict, dark: bool, page_color: str) -> list:
    """Recurring chrome with STABLE ids so it morphs in place, never pops."""
    accent = pal.get("accent") or pal.get("primary") or "#007AFF"
    out = [
        _shape(ID_CHROME_ACCENT, MARGIN, ACCENT_BAR_Y, 44, ACCENT_BAR_H,
               fill=accent, radius=2),
        _text(ID_CHROME_PAGE, RIGHT_EDGE - 120, 664, 120, 28,
              "{{page:2}} / {{pages}}", size=13, color=page_color, weight=500,
              align="right", valign="middle", lh=1.0),
    ]
    return out


def _slide_bg(pal: dict, kind: str) -> str:
    if kind == "dark":
        return pal.get("primary") or "#111827"
    return pal.get("background") or "#FFFFFF"


def _new_slide(slide_id: str, background: str, transition: str, notes: str,
               name: str = "") -> dict:
    return {
        "id": slide_id,
        "background": background,
        "transition": transition,
        "elements": [],
        "notes": notes,
        **({"name": name} if name else {}),
    }


def _notes_for(spec: dict, stype: str, lang: str) -> str:
    """Speaker notes travel in the file — synthesize one when absent."""
    n = spec.get("notes") or spec.get("speaker_notes")
    if isinstance(n, str) and n.strip():
        return n.strip()
    title = _item_text(spec.get("title")) or _item_text(spec.get("quote"))
    if title:
        return _label(lang, f"Слайд «{title}». Одна мысль — не перегружать.",
                      f"Slide: {title}. One idea — do not overload it.")
    return _label(lang, f"Слайд типа {stype}.", f"{stype} slide.")


# ===========================================================================
# Render context
# ===========================================================================

def _ctx(deck: dict, pal: dict) -> dict:
    lang = str(deck.get("language") or "ru").lower()
    accent = pal.get("accent") or pal.get("primary") or "#007AFF"
    return {
        "pal": pal,
        "lang": lang,
        "accent": accent,
        "primary": pal.get("primary") or "#111827",
        "text": pal.get("primary_text") or "#1C1C1E",
        "muted": pal.get("muted") or "#6E6E73",
        "card": pal.get("card") or "#F5F5F7",
        "stroke": pal.get("stroke") or "#E5E5EA",
        "soft": pal.get("accent_soft") or "#E8F0FE",
        "on_dark": pal.get("background_text") or "#FFFFFF",
        "on_dark_muted": ON_DARK_MUTED,
        "radius": 18,
        "radius_sm": 10,
        "chart_palette": [pal.get(f"graph_{i}") for i in range(8)
                          if pal.get(f"graph_{i}")] or [accent],
    }


def _graph(ctx: dict, i: int) -> str:
    cp = ctx["chart_palette"]
    return cp[i % len(cp)] if cp else ctx["accent"]


# ===========================================================================
# Title bands
# ===========================================================================

def _cover_title(spec: dict, ctx: dict, si: int, *, size=FS_COVER_TITLE) -> list:
    """Dark cover/divider/closing: eyebrow + title (+ subtitle + meta)."""
    lang = ctx["lang"]
    els = []
    eyebrow = spec.get("eyebrow") or _cover_eyebrow(spec, ctx)
    if eyebrow:
        els.append(_text(
            f"c{si}-eyebrow", MARGIN, 168, CONTENT_W, 28,
            _esc(_upper(eyebrow)), size=15, color=ctx["accent"], weight=700,
            align="left", valign="middle", lh=1.0, spacing=3, role="kicker",
            fx=_enter(0),
        ))
    els.append(_text(
        ID_COVER_TITLE, MARGIN, 214, CONTENT_W, 210,
        _md_inline(spec.get("title") or ""), size=size, color=ctx["on_dark"],
        weight=800, align="left", valign="top", lh=1.06, role="title",
        fx=_enter(1),
    ))
    sub = _item_text(spec.get("subtitle"))
    if sub:
        els.append(_text(
            f"c{si}-sub", MARGIN, 452, 900, 84, _md_inline(sub), size=25,
            color=ctx["on_dark_muted"], weight=400, align="left", valign="top",
            lh=1.4, role="subtitle", fx=_enter(2),
        ))
    meta = " · ".join(x for x in (
        _item_text(spec.get("presenter")), _item_text(spec.get("date")),
    ) if x)
    if meta:
        els.append(_text(
            f"c{si}-meta", MARGIN, 566, CONTENT_W, 30, _esc(meta), size=FS_LABEL,
            color=ctx["on_dark_muted"], weight=500, align="left",
            valign="middle", lh=1.0, fx=_enter(3),
        ))
    return els


def _cover_eyebrow(spec: dict, ctx: dict) -> str:
    for key in ("eyebrow", "audience", "topic", "goal"):
        v = _item_text(spec.get(key))
        if v:
            return v
    return _label(ctx["lang"], "Презентация", "Presentation")


def _content_title(spec: dict, ctx: dict, si: int) -> list:
    """Content-slide title band. STABLE id -> morphs between content slides."""
    return [_text(
        ID_SLIDE_TITLE, MARGIN, TITLE_Y, CONTENT_W, TITLE_H,
        _md_inline(spec.get("title") or ""), size=FS_SLIDE_TITLE,
        color=ctx["text"], weight=700, align="left", valign="middle", lh=1.12,
        role="title",
    )]


# ===========================================================================
# Dark slides: title / divider / closing
# ===========================================================================

def _render_title(spec: dict, ctx: dict, si: int) -> list:
    els = [
        _dashed_ring(f"decor-ring-{si}", 968, 96, 236, ctx["accent"],
                     duration=16.0, opacity=0.40),
        _dashed_ring(f"decor-ring2-{si}", 1046, 452, 150, ctx["accent"],
                     duration=11.0, opacity=0.28),
    ]
    els += _cover_title(spec, ctx, si)
    return els


def _render_closing(spec: dict, ctx: dict, si: int) -> list:
    spec = dict(spec)
    spec.setdefault("title", _label(ctx["lang"], "Спасибо", "Thank you"))
    els = [
        _dashed_ring(f"decor-ring-{si}", 92, 400, 210, ctx["accent"],
                     duration=15.0, opacity=0.34),
    ]
    els += _cover_title(spec, ctx, si, size=68)
    return els


def _render_divider(spec: dict, ctx: dict, si: int) -> list:
    els = [
        _shape(f"decor-block-{si}", 0, 0, 14, H, fill=ctx["accent"]),
    ]
    eyebrow = spec.get("eyebrow") or _item_text(spec.get("subtitle"))
    els.append(_text(
        f"c{si}-eyebrow", MARGIN, 268, CONTENT_W, 28,
        _esc(_upper(eyebrow or _label(ctx["lang"], "Раздел", "Section"))),
        size=15, color=ctx["accent"], weight=700, align="left",
        valign="middle", lh=1.0, spacing=3, role="kicker", fx=_enter(0),
    ))
    els.append(_text(
        ID_COVER_TITLE, MARGIN, 306, CONTENT_W, 130,
        _md_inline(spec.get("title") or ""), size=62, color=ctx["on_dark"],
        weight=800, align="left", valign="top", lh=1.08, role="title",
        fx=_enter(1),
    ))
    return els


# ===========================================================================
# Content slides
# ===========================================================================

def _render_bullets(spec: dict, ctx: dict, si: int) -> list:
    items = _as_list(spec.get("bullets") or spec.get("points") or spec.get("items"))
    texts = [_item_text(i) for i in items]
    texts = [t for t in texts if t]
    els = _content_title(spec, ctx, si)
    if not texts:
        return els
    n = len(texts)
    box_h = _clamp(34 + n * 46, 120, CONTENT_H)
    els.append(_shape(
        f"b{si}-card", MARGIN, CONTENT_Y, CONTENT_W, box_h, fill=ctx["card"],
        stroke=ctx["stroke"], stroke_width=1, radius=ctx["radius"],
        shadow=_card_shadow(ctx["pal"]), fx=_enter(1),
    ))
    els.append(_text(
        f"b{si}-list", MARGIN + 34, CONTENT_Y + 26, CONTENT_W - 68, box_h - 52,
        _bullets_html(texts), size=max(BODY_FLOOR, FS_BODY), color=ctx["text"],
        weight=400, align="left", valign="top", lh=1.55, role="body",
            fx=_enter(2),
        ))
    return els


# ===========================================================================
# Charts — Bento's charts-lite is NOT ECharts and fails silently
# ===========================================================================

_CHART_PRESETS = ("bar", "line", "pie", "scatter")


def _series_numbers(vals) -> list:
    """bar/line/scatter data MUST be plain numbers: {"value":420} renders 0."""
    out = []
    for v in _as_list(vals):
        if isinstance(v, dict):
            v = v.get("value", v.get("y", 0))
        try:
            f = float(v)
        except (TypeError, ValueError):
            f = 0.0
        out.append(int(f) if f == int(f) else round(f, 4))
    return out


def _chart_option(spec_chart: dict, ctx: dict) -> dict:
    cats = [_item_text(c) for c in _as_list(spec_chart.get("categories"))]
    raw = _as_list(spec_chart.get("series"))

    norm = []
    for s in raw:
        if isinstance(s, dict):
            name = _item_text(s.get("name")) or ""
            vals = s.get("values")
            if vals is None:
                vals = s.get("data")
        else:
            name, vals = "", s
        norm.append((name, _series_numbers(vals)))
    norm = [(n, v) for n, v in norm if v]

    preset = str(spec_chart.get("preset") or spec_chart.get("kind") or "").lower()
    if preset not in _CHART_PRESETS:
        preset = ""

    option = {"color": list(ctx["chart_palette"]), "tooltip": {"trigger": "item"}}

    if not norm:
        option["series"] = []
        return option

    if preset == "pie":
        name, vals = norm[0]
        labels = cats if len(cats) == len(vals) else [
            _item_text(spec_chart.get("series")[0].get("name")) or f"#{i + 1}"
            for i in range(len(vals))
        ]
        option["series"] = [{
            "type": "pie",
            "name": name,
            "radius": ["42%", "70%"],
            "data": [{"name": l or f"#{i + 1}", "value": v}
                     for i, (l, v) in enumerate(zip(labels, vals))],
            "label": {"formatter": "{b}: {d}%"},
            "itemStyle": {"borderColor": "#FFFFFF", "borderWidth": 2},
        }]
        option["legend"] = {"show": True, "bottom": 0}
        return option

    kind = preset or ("line" if len(norm) == 1 else "bar")
    option["xAxis"] = {"type": "category", "data": cats}
    option["yAxis"] = {"type": "value"}
    option["grid"] = {"left": 64, "right": 28, "top": 36, "bottom": 44}
    if len(norm) > 1:
        option["legend"] = {"show": True, "top": 0}

    series = []
    for name, vals in norm:
        s = {"type": kind, "name": name, "data": vals}
        if kind == "line":
            s["smooth"] = True
            s["symbolSize"] = 8
            s["lineStyle"] = {"width": 3}
            s["areaStyle"] = {"color": "rgba(0,122,255,0.10)"}
        elif kind == "bar":
            s["itemStyle"] = {"borderRadius": [6, 6, 0, 0]}
        elif kind == "scatter":
            s["symbolSize"] = 14
        series.append(s)
    option["series"] = series
    return option


def _render_chart(spec: dict, ctx: dict, si: int) -> list:
    els = _content_title(spec, ctx, si)
    cs = spec.get("chart") if isinstance(spec.get("chart"), dict) else spec
    option = _chart_option(cs, ctx)
    preset = option["series"][0]["type"] if option.get("series") else "bar"
    els.append(_el(
        f"ch{si}", MARGIN, CONTENT_Y + 12, CONTENT_W, CONTENT_H - 40,
        type="chart", preset=preset, option=option,
        fx=_enter(1),
    ))
    note = _item_text(cs.get("note"))
    if note:
        els.append(_text(
            f"ch{si}-note", MARGIN, CONTENT_BOTTOM - 22, CONTENT_W, 22,
            _md_inline(note), size=FS_CAPTION, color=ctx["muted"], weight=400,
            align="left", valign="middle", lh=1.0, role="body",
        ))
    return els


# ===========================================================================
# Tables
# ===========================================================================

def _pad(row: list, n: int) -> list:
    row = list(row)
    return row + [""] * (n - len(row)) if len(row) < n else row[:n]


def _render_table(spec: dict, ctx: dict, si: int) -> list:
    els = _content_title(spec, ctx, si)
    ts = spec.get("table") if isinstance(spec.get("table"), dict) else spec
    headers = [_item_text(h) for h in _as_list(ts.get("headers") or ts.get("columns"))]
    rows = [_as_list(r) for r in _as_list(ts.get("rows"))]
    ncol = len(headers) or max((len(r) for r in rows), default=1)
    ncol = max(1, ncol)
    highlight = ts.get("highlight_col")

    out_rows = []
    if headers:
        out_rows.append({"cells": [
            {"html": _md_inline(c), "align": "left"} for c in _pad(headers, ncol)
        ]})
    for r in rows:
        cells = []
        for ci, c in enumerate(_pad(r, ncol)):
            cell = {"html": _md_inline(_item_text(c))}
            if isinstance(highlight, int) and ci == highlight:
                cell["bold"] = True
                cell["color"] = ctx["accent"]
            cells.append(cell)
        out_rows.append({"cells": cells})

    n_rows = len(out_rows)
    box_h = _clamp(48 + n_rows * 40, 120, CONTENT_H - 12)
    els.append(_el(
        f"tb{si}", MARGIN, CONTENT_Y + 8, CONTENT_W, box_h,
        type="table",
        columns=[{"w": 1} for _ in range(ncol)],
        rows=out_rows,
        header=bool(headers),
        style={
            "headerBg": ctx["primary"],
            "headerColor": ctx["on_dark"],
            "zebra": "rgba(0,0,0,0.035)",
            "borderColor": ctx["stroke"],
            "borderWidth": 1,
            "cellPadX": 16,
            "cellPadY": 11,
            "fontSize": 18,
            "color": ctx["text"],
            "radius": ctx["radius_sm"],
        },
        fx=_enter(1),
    ))
    return els


# ===========================================================================
# Metric-style card rows: metrics / kpi_row
# ===========================================================================

def _metric_items(spec: dict) -> list:
    for key in ("metrics", "kpis", "items", "values"):
        v = _as_list(spec.get(key))
        if v:
            return v
    return []


def _render_metric_cards(spec: dict, ctx: dict, si: int, prefix: str) -> list:
    els = _content_title(spec, ctx, si)
    items = _metric_items(spec)[:4]
    if not items:
        return els
    cols = _cols_for(len(items))
    card_y, card_h = 252, 236
    for i, ((cx, cw), it) in enumerate(zip(cols, items)):
        value = _item_text(_item_get(it, "value", "label", "title", default=it))
        label = _item_text(_item_get(it, "label", "title", "name", default=""))
        if isinstance(it, dict) and "value" in it and "label" in it:
            value, label = _item_text(it["value"]), _item_text(it["label"])
        elif not isinstance(it, dict):
            value, label = _item_text(it), ""
        if value == label:
            label = ""
        els.append(_shape(
            f"{prefix}{si}-{i}-card", cx, card_y, cw, card_h, fill=ctx["card"],
            stroke=ctx["stroke"], stroke_width=1, radius=ctx["radius"],
            shadow=_card_shadow(ctx["pal"]), fx=_enter(i + 1),
        ))
        els.append(_shape(
            f"{prefix}{si}-{i}-tick", cx + 28, card_y + 30, 30, 4,
            fill=_graph(ctx, i), radius=2, fx=_enter(i + 1),
        ))
        els.append(_text(
            f"{prefix}{si}-{i}-val", cx + 28, card_y + 56, cw - 56, 86,
            _md_inline(value), size=FS_METRIC, color=_graph(ctx, i), weight=800,
            align="left", valign="middle", lh=1.0, role="body",
            fx=_countup(i + 2),
        ))
        if label:
            els.append(_text(
                f"{prefix}{si}-{i}-lab", cx + 28, card_y + 152, cw - 56, 62,
                _md_inline(label), size=max(BODY_FLOOR, 18), color=ctx["muted"],
                weight=500, align="left", valign="top", lh=1.35, role="body",
                fx=_enter(i + 2),
            ))
    return els


def _render_metrics(spec: dict, ctx: dict, si: int) -> list:
    return _render_metric_cards(spec, ctx, si, "m")


def _render_kpi_row(spec: dict, ctx: dict, si: int) -> list:
    return _render_metric_cards(spec, ctx, si, "k")


# ===========================================================================
# Feature cards, comparison, logos, table of contents
# ===========================================================================

def _render_feature(spec: dict, ctx: dict, si: int) -> list:
    els = _content_title(spec, ctx, si)
    items = _as_list(spec.get("features") or spec.get("items"))[:4]
    if not items:
        return els
    cols = _cols_for(len(items))
    card_y, card_h = 232, 300
    for i, ((cx, cw), it) in enumerate(zip(cols, items)):
        title = _item_text(_item_get(it, "title", "heading", "name", default=it))
        body = _item_text(_item_get(it, "text", "desc", "description", default=""))
        els.append(_shape(
            f"f{si}-{i}-card", cx, card_y, cw, card_h, fill=ctx["card"],
            stroke=ctx["stroke"], stroke_width=1, radius=ctx["radius"],
            shadow=_card_shadow(ctx["pal"]), fx=_enter(i + 1),
        ))
        # Bento decks never use emoji glyphs: an icon becomes an accent shape.
        els.append(_shape(
            f"f{si}-{i}-icon", cx + 28, card_y + 30, 40, 40, fill=_graph(ctx, i),
            radius=10, fx=_enter(i + 1),
        ))
        els.append(_text(
            f"f{si}-{i}-t", cx + 28, card_y + 94, cw - 56, 66, _md_inline(title),
            size=22, color=ctx["text"], weight=700, align="left", valign="top",
            lh=1.22, role="body", fx=_enter(i + 2),
        ))
        if body:
            els.append(_text(
                f"f{si}-{i}-b", cx + 28, card_y + 168, cw - 56, card_h - 196,
                _md_inline(body), size=max(BODY_FLOOR, 18), color=ctx["muted"],
                weight=400, align="left", valign="top", lh=1.45, role="body",
                fx=_enter(i + 2),
            ))
    return els


def _render_comparison(spec: dict, ctx: dict, si: int) -> list:
    els = _content_title(spec, ctx, si)
    cols_in = _as_list(spec.get("columns") or spec.get("cols"))[:2]
    if not cols_in:
        return els
    cols = COL2 if len(cols_in) == 2 else [(MARGIN, CONTENT_W)]
    for i, ((cx, cw), col) in enumerate(zip(cols, cols_in)):
        heading = _item_text(_item_get(col, "heading", "title", "name", default=col))
        points = _as_list(_item_get(col, "points", "bullets", "items", default=[]))
        texts = [t for t in (_item_text(p) for p in points) if t]
        els.append(_shape(
            f"cp{si}-{i}-card", cx, CONTENT_Y, cw, CONTENT_H - 24,
            fill=ctx["card"] if i else ctx["soft"], stroke=ctx["stroke"],
            stroke_width=1, radius=ctx["radius"],
            shadow=_card_shadow(ctx["pal"]), fx=_enter(i + 1),
        ))
        els.append(_text(
            f"cp{si}-{i}-h", cx + 30, CONTENT_Y + 26, cw - 60, 40,
            _md_inline(heading), size=23, color=ctx["primary"] if i else ctx["accent"],
            weight=700, align="left", valign="middle", lh=1.1, role="body",
            fx=_enter(i + 1),
        ))
        els.append(_shape(
            f"cp{si}-{i}-rule", cx + 30, CONTENT_Y + 78, cw - 60, 2,
            fill=ctx["stroke"], radius=1, fx=_enter(i + 1),
        ))
        if texts:
            els.append(_text(
                f"cp{si}-{i}-p", cx + 30, CONTENT_Y + 98, cw - 60,
                CONTENT_H - 140, _bullets_html(texts),
                size=max(BODY_FLOOR, 19), color=ctx["text"], weight=400,
                align="left", valign="top", lh=1.5, role="body",
                fx=_enter(i + 2),
            ))
    return els


def _render_logos(spec: dict, ctx: dict, si: int) -> list:
    els = _content_title(spec, ctx, si)
    items = _as_list(spec.get("logos") or spec.get("items"))[:8]
    if not items:
        return els
    per_row = 4 if len(items) > 4 else len(items)
    cols = _cols_for(per_row)
    chip_h, gap_y = 88, 24
    start_y = CONTENT_Y + 24
    for i, it in enumerate(items):
        name = _item_text(it)
        r, c = divmod(i, per_row)
        cx, cw = cols[c]
        cy = start_y + r * (chip_h + gap_y)
        if cy + chip_h > CONTENT_BOTTOM:
            break
        els.append(_shape(
            f"lg{si}-{i}", cx, cy, cw, chip_h, fill=ctx["card"],
            stroke=ctx["stroke"], stroke_width=1, radius=ctx["radius_sm"],
            fx=_enter(i + 1),
        ))
        els.append(_text(
            f"lg{si}-{i}-t", cx + 18, cy, cw - 36, chip_h, _md_inline(name),
            size=19, color=ctx["muted"], weight=600, align="center",
            valign="middle", lh=1.1, role="body", fx=_enter(i + 1),
        ))
    note = _item_text(spec.get("note"))
    if note:
        els.append(_text(
            f"lg{si}-note", MARGIN, CONTENT_BOTTOM - 26, CONTENT_W, 24,
            _md_inline(note), size=FS_CAPTION, color=ctx["muted"], weight=400,
            align="center", valign="middle", lh=1.0, role="body",
        ))
    return els


def _render_toc(spec: dict, ctx: dict, si: int) -> list:
    els = _content_title(spec, ctx, si)
    items = _as_list(spec.get("items") or spec.get("entries"))[:8]
    if not items:
        return els
    row_h = _clamp(int((CONTENT_H - 24) / len(items)), 52, 84)
    y = CONTENT_Y + 8
    for i, it in enumerate(items):
        title = _item_text(_item_get(it, "title", "heading", "name", default=it))
        desc = _item_text(_item_get(it, "desc", "description", "text", default=""))
        els.append(_text(
            f"toc{si}-{i}-n", MARGIN, y, 56, row_h, f"{i + 1:02d}", size=26,
            color=ctx["accent"], weight=800, align="left", valign="middle",
            lh=1.0, role="body", fx=_enter(i + 1),
        ))
        els.append(_text(
            f"toc{si}-{i}-t", MARGIN + 68, y, 420, row_h, _md_inline(title),
            size=21, color=ctx["text"], weight=600, align="left",
            valign="middle", lh=1.2, role="body", fx=_enter(i + 1),
        ))
        if desc:
            els.append(_text(
                f"toc{si}-{i}-d", MARGIN + 500, y, CONTENT_W - 500, row_h,
                _md_inline(desc), size=FS_LABEL, color=ctx["muted"], weight=400,
                align="left", valign="middle", lh=1.3, role="body",
                fx=_enter(i + 2),
            ))
        els.append(_shape(
            f"toc{si}-{i}-rule", MARGIN, y + row_h - 1, CONTENT_W, 1,
            fill=ctx["stroke"], radius=0, opacity=0.7,
        ))
        y += row_h
    return els


def _render_process(spec: dict, ctx: dict, si: int) -> list:
    els = _content_title(spec, ctx, si)
    steps = _as_list(spec.get("steps") or spec.get("items"))[:5]
    if not steps:
        return els
    n = len(steps)
    gutter = 24 if n > 4 else 32
    cols = _even_cols(n, gutter)
    card_y, card_h = 264, 220
    for i, ((cx, cw), st) in enumerate(zip(cols, steps)):
        title = _item_text(_item_get(st, "title", "text", "name", default=st))
        desc = _item_text(_item_get(st, "desc", "description", "detail", default=""))
        els.append(_shape(
            f"proc-{i}-card", cx, card_y, cw, card_h, fill=ctx["card"],
            stroke=ctx["stroke"], stroke_width=1, radius=ctx["radius"],
            shadow=_card_shadow(ctx["pal"]), fx=_enter(i + 1),
        ))
        els.append(_shape(
            f"proc-{i}-num", cx + 24, card_y + 26, 42, 42, shape="ellipse",
            fill=_graph(ctx, i), radius=21, fx=_enter(i + 1),
        ))
        els.append(_text(
            f"proc-{i}-numt", cx + 24, card_y + 26, 42, 42, f"{i + 1:02d}",
            size=FS_LABEL, color="#FFFFFF", weight=700, align="center",
            valign="middle", lh=1.0, role="body", fx=_enter(i + 1),
        ))
        els.append(_text(
            f"proc-{i}-t", cx + 24, card_y + 88, cw - 48, 54, _md_inline(title),
            size=20, color=ctx["text"], weight=700, align="left", valign="top",
            lh=1.22, role="body", fx=_enter(i + 2),
        ))
        if desc:
            els.append(_text(
                f"proc-{i}-d", cx + 24, card_y + 144, cw - 48, card_h - 168,
                _md_inline(desc), size=max(BODY_FLOOR, 17), color=ctx["muted"],
                weight=400, align="left", valign="top", lh=1.4, role="body",
                fx=_enter(i + 2),
            ))
        if i < n - 1:
            els.append(_shape(
                f"proc-{i}-arrow", cx + cw + 6, card_y + card_h / 2 - 9,
                max(8, gutter - 12), 18, shape="arrow", fill=ctx["accent"],
                opacity=0.75,
            ))
    return els


def _render_timeline(spec: dict, ctx: dict, si: int) -> list:
    els = _content_title(spec, ctx, si)
    items = _as_list(spec.get("items") or spec.get("events"))[:6]
    if not items:
        return els
    n = len(items)
    cols = _even_cols(n, 28)
    line_y = 320
    els.append(_shape(
        f"tl{si}-line", MARGIN, line_y, CONTENT_W, 2, shape="path",
        d=f"M0,0 L{CONTENT_W},0", pathBox=[0, 0, CONTENT_W, 2],
        fill="transparent", stroke=ctx["accent"], stroke_width=2,
        stroke_style="dashed",
        fx={"loop": {"type": "dash-march", "distance": 18, "duration": 6.0}},
    ))
    for i, ((cx, cw), it) in enumerate(zip(cols, items)):
        title = _item_text(_item_get(it, "title", "name", "text", default=it))
        desc = _item_text(_item_get(it, "desc", "description", default=""))
        dot = 22
        els.append(_shape(
            f"tl{si}-{i}-dot", cx + cw / 2 - dot / 2, line_y + 1 - dot / 2,
            dot, dot, shape="ellipse", fill=_graph(ctx, i),
            stroke=ctx["pal"].get("background") or "#FFFFFF", stroke_width=3,
            fx=_enter(i + 1),
        ))
        els.append(_text(
            f"tl{si}-{i}-t", cx, line_y + 40, cw, 48, _md_inline(title),
            size=19, color=ctx["text"], weight=700, align="center", valign="top",
            lh=1.22, role="body", fx=_enter(i + 1),
        ))
        if desc:
            els.append(_text(
                f"tl{si}-{i}-d", cx, line_y + 94, cw, 120, _md_inline(desc),
                size=max(BODY_FLOOR, 17), color=ctx["muted"], weight=400,
                align="center", valign="top", lh=1.4, role="body",
                fx=_enter(i + 2),
            ))
    return els


def _render_image_showcase(spec: dict, ctx: dict, si: int, deck_dir: Path) -> list:
    src = _image_src(spec.get("image") or spec.get("src"), deck_dir)
    if not src:
        return _render_centered_header(spec, ctx, si)
    els = [
        _el(f"im{si}-img", 0, 0, W, H, type="image", src=src, fit="cover",
            radius=0,
            fx={"ambient": "kenburns",
                "ken": {"dir": "drift", "scale": 1.08, "duration": 20}}),
        _shape(f"im{si}-scrim", 0, 0, W, H, fill=SCRIM, stroke="none",
               stroke_width=0, radius=0),
    ]
    els.append(_text(
        f"im{si}-t", MARGIN, 396, CONTENT_W, 110,
        _md_inline(spec.get("title") or ""), size=52, color="#FFFFFF",
        weight=800, align="left", valign="top", lh=1.1, role="title",
        fx=_enter(1),
    ))
    desc = _item_text(spec.get("desc") or spec.get("description"))
    points = [_item_text(p) for p in _as_list(spec.get("points"))]
    points = [p for p in points if p]
    body = desc or (" · ".join(points))
    if body:
        els.append(_text(
            f"im{si}-d", MARGIN, 522, 900, 72, _md_inline(body), size=20,
            color="rgba(255,255,255,0.86)", weight=400, align="left",
            valign="top", lh=1.42, role="body", fx=_enter(2),
        ))
    return els


# ===========================================================================
# Type inference (same idea as pick_layout() in the sibling builders)
# ===========================================================================

def _has_numbers(vals) -> bool:
    for v in _as_list(vals):
        if isinstance(v, dict):
            v = v.get("value", v.get("y"))
        try:
            float(v)
        except (TypeError, ValueError):
            return False
    return bool(_as_list(vals))


def _infer_type(spec: dict) -> str:
    if spec.get("quote"):
        return "quote"
    if spec.get("value") is not None and not spec.get("metrics"):
        return "big_number"
    if spec.get("chart") or spec.get("categories"):
        return "chart"
    if spec.get("table") or (spec.get("headers") and spec.get("rows")):
        return "table"
    if spec.get("steps"):
        return "process"
    if _metric_items(spec):
        return "metrics"
    if spec.get("features"):
        return "feature"
    if spec.get("logos"):
        return "logos"
    if spec.get("columns") or spec.get("cols"):
        return "comparison"
    if spec.get("image") or spec.get("src"):
        return "image_showcase"
    items = _as_list(spec.get("items") or spec.get("entries") or spec.get("events"))
    if items and all(isinstance(i, dict) and (i.get("desc") or i.get("description"))
                     for i in items):
        return "timeline"
    if items:
        return "table_of_contents"
    if spec.get("bullets") or spec.get("points"):
        return "bullets"
    if spec.get("panel"):
        return "centered_header"
    return "bullets"


def _slide_type(spec: dict) -> str:
    t = str(spec.get("type") or "").strip().lower()
    if not t or t == "auto":
        return _infer_type(spec)
    return t if t in SLIDE_TYPES else _infer_type(spec)


# ===========================================================================
# State slides — interactive drill-down branches
# ===========================================================================

def _state_slides(spec: dict, ctx: dict, parent_id: str, si: int) -> list:
    states = _as_list(spec.get("states") or spec.get("drilldown"))
    if not states:
        return []
    out = []
    for k, st in enumerate(states[:4]):
        sid = f"{parent_id}-st{k}"
        title = _item_text(_item_get(st, "title", "heading", "name", default=st))
        points = [_item_text(p) for p in
                  _as_list(_item_get(st, "points", "bullets", "items", default=[]))]
        points = [p for p in points if p]
        els = [_shape(
            f"{sid}-bg", 0, 0, W, H,
            fill=ctx["pal"].get("background") or "#FFFFFF", stroke="none",
            stroke_width=0, radius=0,
        )]
        els.append(_shape(
            f"decor-{sid}-bar", 0, 0, 14, H, fill=ctx["accent"],
        ))
        els.append(_text(
            f"{sid}-eyebrow", MARGIN, 150, CONTENT_W, 28,
            _esc(_upper(_label(ctx["lang"], "Детали", "Detail"))), size=15,
            color=ctx["accent"], weight=700, align="left", valign="middle",
            lh=1.0, spacing=3, role="kicker",
        ))
        els.append(_text(
            ID_SLIDE_TITLE, MARGIN, TITLE_Y + 116, CONTENT_W, TITLE_H,
            _md_inline(title), size=38, color=ctx["text"], weight=700,
            align="left", valign="middle", lh=1.14, role="title",
        ))
        if points:
            els.append(_shape(
                f"{sid}-card", MARGIN, 320, CONTENT_W, 240, fill=ctx["card"],
                stroke=ctx["stroke"], stroke_width=1, radius=ctx["radius"],
                shadow=_card_shadow(ctx["pal"]),
            ))
            els.append(_text(
                f"{sid}-list", MARGIN + 34, 348, CONTENT_W - 68, 184,
                _bullets_html(points), size=max(BODY_FLOOR, 20),
                color=ctx["text"], weight=400, align="left", valign="top",
                lh=1.5, role="body",
            ))
        # Transparent full-canvas hit target: click anywhere returns to parent.
        els.append(_shape(
            f"{sid}-dismiss", 0, 0, W, H, fill="rgba(0,0,0,0)", stroke="none",
            stroke_width=0, radius=0, link=parent_id,
        ))
        out.append({
            "id": sid,
            "background": ctx["pal"].get("background") or "#FFFFFF",
            "transition": "morph",
            "elements": els,
            "notes": _label(ctx["lang"], f"Детали: {title}. Esc или ← — назад.",
                            f"Detail: {title}. Esc or left arrow to go back."),
            "stateOf": parent_id,
            "name": title or f"{_label(ctx['lang'], 'Детали', 'Detail')} {k + 1}",
        })
    return out


def _drill_chip(ctx: dict, si: int, state_id: str) -> list:
    label = _label(ctx["lang"], "Подробнее →", "Details →")
    return [
        _shape(f"dr{si}-chip", RIGHT_EDGE - 186, CONTENT_BOTTOM - 52, 186, 44,
               fill=ctx["accent"], stroke="none", stroke_width=0,
               radius=22, link=state_id),
        _text(f"dr{si}-chipt", RIGHT_EDGE - 186, CONTENT_BOTTOM - 52, 186, 44,
              _esc(label), size=FS_LABEL, color="#FFFFFF", weight=700,
              align="center", valign="middle", lh=1.0, role="body",
              link=state_id),
    ]


# ===========================================================================
# Geometry fit
# ===========================================================================

_EXEMPT_PREFIXES = ("chrome-", "decor", "ghost")


def _is_exempt(el_id: str) -> bool:
    return str(el_id).startswith(_EXEMPT_PREFIXES)


def _fit(els: list, si: int, stype: str, warnings: list) -> list:
    """Clamp content into the guardrails; chrome/decor and full-bleed are exempt."""
    for e in els:
        eid = str(e.get("id", ""))
        if _is_exempt(eid):
            continue
        if (e.get("x"), e.get("y"), e.get("w"), e.get("h")) == (0, 0, W, H):
            continue
        over_w = e["x"] + e["w"] - RIGHT_EDGE
        if over_w > 0:
            e["w"] = round(e["w"] - over_w, 2)
            warnings.append(f"slide {si + 1} ({stype}) `{eid}`: width clamped "
                            f"by {over_w:.0f}px to stay inside x+w<={RIGHT_EDGE}")
        over_h = e["y"] + e["h"] - CONTENT_BOTTOM
        if over_h > 0 and e.get("role") != "title":
            e["h"] = round(e["h"] - over_h, 2)
            warnings.append(f"slide {si + 1} ({stype}) `{eid}`: height clamped "
                            f"by {over_h:.0f}px to end above y={CONTENT_BOTTOM}")
        if e["w"] <= 0 or e["h"] <= 0:
            e["w"], e["h"] = max(1.0, e["w"]), max(1.0, e["h"])
    return els


# ===========================================================================
# Document assembly
# ===========================================================================

def _build_doc(deck: dict, deck_dir: Path, no_morph: bool = False):
    pal = _resolve_palette(deck.get("theme"))
    ctx = _ctx(deck, pal)
    lang = ctx["lang"]
    title = _item_text(deck.get("title")) or _label(lang, "Презентация", "Presentation")
    goal = str(deck.get("goal") or "")

    stats = {"morph": 0, "charts": 0, "tables": 0, "states": 0}
    warnings: list = []
    slides: list = []

    for si, raw in enumerate(_as_list(deck.get("slides"))):
        spec = raw if isinstance(raw, dict) else {"title": _item_text(raw)}
        stype = _slide_type(spec)
        dark = stype in DARK_SLIDE_TYPES
        parent_id = f"s{si}"

        if stype == "title":
            tr = "fade"
        elif no_morph or si == 0 or stype in ("divider", "closing"):
            tr = "fade"
        else:
            tr = "morph"
            stats["morph"] += 1

        if stype == "image_showcase":
            els = _render_image_showcase(spec, ctx, si, deck_dir)
        else:
            els = RENDERERS[stype](spec, ctx, si)

        states = _state_slides(spec, ctx, parent_id, si)
        if states:
            els += _drill_chip(ctx, si, states[0]["id"])
            stats["states"] += len(states)

        for e in els:
            if e.get("type") == "chart":
                stats["charts"] += 1
            elif e.get("type") == "table":
                stats["tables"] += 1

        page_color = (ctx["on_dark_muted"] if dark or stype == "image_showcase"
                      else ctx["muted"])
        els = _fit(els, si, stype, warnings)
        els += _chrome(pal, dark, page_color)

        slides.append(_new_slide(
            parent_id, _slide_bg(pal, "dark" if dark else "light"), tr,
            _notes_for(spec, stype, lang),
            name=(_item_text(spec.get("title")) or stype)[:48],
        ))
        slides[-1]["elements"] = els
        slides.extend(states)

    meta = {}
    for src, dst in (("author", "author"), ("topic", "subject"),
                     ("audience", "event"), ("tone", "keywords")):
        v = _item_text(deck.get(src))
        if v:
            meta[dst] = v

    doc = {
        "format": BENTO_FORMAT,
        "version": BENTO_VERSION,
        "docId": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{title}|{goal}")),
        "title": title,
        "size": {"width": W, "height": H},
        "theme": _bento_theme(pal),
        "present": {
            "slideNumber": True,
            "controls": True,
            "progress": True,
            "morphSeconds": 0.65,
            "numberHidden": False,
        },
        "slides": slides,
        "modified": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
    }
    if meta:
        doc["meta"] = meta
    return doc, stats, warnings


# ===========================================================================
# App shell: fetch (never vendor) + splice the one editable block
# ===========================================================================

def _validate_shell(text: str, origin: str) -> None:
    if len(text) < SHELL_MIN_BYTES:
        raise SystemExit(
            f"error: {origin} is only {len(text)} bytes — expected the Bento app "
            f"shell (>{SHELL_MIN_BYTES} bytes). Refusing to build on a truncated "
            f"or error page.")
    hits = [m for m in _DOC_BLOCK.finditer(text) if "bento-doc" in m.group(1)]
    if not hits:
        raise SystemExit(
            f"error: {origin} has no <script type=\"application/bento+json\" "
            f"id=\"bento-doc\"> block — is it really a Bento app shell?")
    if len(hits) > 1:
        raise SystemExit(
            f"error: {origin} contains {len(hits)} #bento-doc blocks, expected "
            f"exactly one — upstream shell layout may have changed.")


def _get_shell(shell_arg, cache_dir, no_download: bool) -> tuple:
    if shell_arg:
        p = Path(shell_arg).expanduser()
        if not p.is_file():
            raise SystemExit(f"error: --shell file not found: {p}")
        text = p.read_text(encoding="utf-8", errors="replace")
        _validate_shell(text, str(p))
        return text, str(p)

    cdir = Path(cache_dir).expanduser() if cache_dir else CACHE_DIR
    cached = cdir / f"Bento_Slides.{BENTO_SHELL_VERSION}.bento.html"
    if cached.is_file():
        text = cached.read_text(encoding="utf-8", errors="replace")
        try:
            _validate_shell(text, str(cached))
            return text, str(cached)
        except SystemExit:
            print(f"warning: cached shell {cached} is unusable, re-downloading",
                  file=sys.stderr)

    if no_download:
        raise SystemExit(
            "error: no cached Bento app shell and --no-download was given.\n"
            f"  expected cache: {cached}\n"
            f"  pass one explicitly: --shell /path/to/Bento_Slides.bento.html\n"
            f"  upstream: {BENTO_SHELL_URL}")

    print(f"fetching Bento app shell {BENTO_SHELL_VERSION} ...", file=sys.stderr)
    req = Request(BENTO_SHELL_URL, headers={
        "User-Agent": "Mozilla/5.0 (presentation-maker build_bento.py)",
    })
    try:
        with urlopen(req, timeout=60) as resp:
            raw = resp.read()
    except Exception as e:
        raise SystemExit(
            f"error: cannot download the Bento app shell: {e}\n"
            f"  url: {BENTO_SHELL_URL}\n"
            f"  offline? save it manually and pass --shell /path/to/file")
    text = raw.decode("utf-8", errors="replace")
    _validate_shell(text, BENTO_SHELL_URL)
    try:
        cdir.mkdir(parents=True, exist_ok=True)
        cached.write_text(text, encoding="utf-8")
    except OSError as e:
        print(f"warning: could not cache the shell at {cached}: {e}", file=sys.stderr)
    return text, str(cached)


def _serialize(doc: dict) -> str:
    """Every '<' must become the literal escape \\u003c: a raw </script> inside
    an html string would terminate the block and corrupt the whole file."""
    return json.dumps(doc, ensure_ascii=False, separators=(",", ":")).replace(
        "<", "\\u003c")


def _splice(shell: str, payload: str) -> str:
    hits = [m for m in _DOC_BLOCK.finditer(shell) if "bento-doc" in m.group(1)]
    if len(hits) != 1:
        raise SystemExit(
            f"error: expected exactly one #bento-doc block in the shell, found "
            f"{len(hits)}")
    m = hits[0]
    return shell[:m.start(2)] + payload + shell[m.end(2):]


def _roundtrip(out_text: str, doc: dict) -> None:
    hits = [m for m in _DOC_BLOCK.finditer(out_text) if "bento-doc" in m.group(1)]
    if len(hits) != 1:
        raise SystemExit("error: written file does not contain exactly one "
                         "#bento-doc block")
    try:
        back = json.loads(hits[0].group(2))
    except json.JSONDecodeError as e:
        raise SystemExit(f"error: written document does not parse back: {e}")
    if back != doc:
        raise SystemExit("error: round-trip mismatch — the document read back "
                         "from the written file differs from the generated one")


# ===========================================================================
# Entry point
# ===========================================================================

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Build a self-contained Bento deck (*.bento.html) from deck.json")
    ap.add_argument("deck", help="path to deck.json (the shared pipeline contract)")
    ap.add_argument("-o", "--output", default=None,
                    help="output file (default: <deck stem>.bento.html beside input)")
    ap.add_argument("--shell", default=None,
                    help="use this local Bento app shell instead of cache/download")
    ap.add_argument("--cache-dir", default=None,
                    help=f"shell cache dir (default: {CACHE_DIR})")
    ap.add_argument("--no-download", action="store_true",
                    help="offline: use --shell or the cache only, never fetch")
    ap.add_argument("--json", default=None,
                    help="where to write the generated document JSON sidecar "
                         "(default: <output>.doc.json)")
    ap.add_argument("--no-morph", action="store_true",
                    help="force transition:fade on every slide (debug escape hatch)")
    ap.add_argument("--quiet", action="store_true", help="print only errors")
    args = ap.parse_args()

    deck_path = Path(args.deck)
    if not deck_path.is_file():
        print(f"error: deck spec not found: {deck_path}", file=sys.stderr)
        return 2
    try:
        deck = json.loads(deck_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"error: cannot read {deck_path}: {e}", file=sys.stderr)
        return 2
    if not isinstance(deck, dict):
        print(f"error: {deck_path} must contain a JSON object", file=sys.stderr)
        return 2

    out_path = (Path(args.output).expanduser() if args.output
                else deck_path.with_name(deck_path.stem + ".bento.html"))
    sidecar = (Path(args.json).expanduser() if args.json
               else Path(str(out_path) + ".doc.json"))

    try:
        doc, stats, warnings = _build_doc(deck, deck_path.parent, args.no_morph)
    except Exception as e:
        print(f"error: cannot build the Bento document: {e}", file=sys.stderr)
        return 2

    if not doc["slides"]:
        print("error: deck.json has no slides", file=sys.stderr)
        return 2

    try:
        shell, shell_origin = _get_shell(args.shell, args.cache_dir,
                                        args.no_download)
        payload = _serialize(doc)
        final = _splice(shell, payload)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(final, encoding="utf-8")
        _roundtrip(out_path.read_text(encoding="utf-8"), doc)
        sidecar.write_text(json.dumps(doc, ensure_ascii=False, indent=2),
                           encoding="utf-8")
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 2
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    if not args.quiet:
        size_kb = out_path.stat().st_size // 1024
        print(f"PASS  {len(doc['slides'])} slides -> {out_path} "
              f"({size_kb} KB, morph on {stats['morph']}, charts {stats['charts']}, "
              f"tables {stats['tables']}, states {stats['states']})")
        print(f"      shell: {shell_origin}")
        print(f"      doc:   {sidecar}")
        print(f"      gate:  python3 skills/presentation-maker/scripts/"
              f"qa_bento.py {out_path}")
    return 0


def _render_big_number(spec: dict, ctx: dict, si: int) -> list:
    els = _content_title(spec, ctx, si) if _item_text(spec.get("title")) else []
    accent = ctx["accent"] if spec.get("accent") in (None, True, "accent") else (
        spec.get("accent") if isinstance(spec.get("accent"), str)
        and str(spec["accent"]).startswith("#") else ctx["accent"])
    els.append(_text(
        f"n{si}-value", MARGIN, 196, CONTENT_W, 250,
        _md_inline(spec.get("value") or ""), size=FS_HERO, color=accent,
        weight=800, align="center", valign="middle", lh=1.0, role="body",
        fx=_countup(1),
    ))
    label = _item_text(spec.get("label"))
    if label:
        els.append(_text(
            f"n{si}-label", MARGIN, 456, CONTENT_W, 46, _md_inline(label),
            size=26, color=ctx["text"], weight=600, align="center",
            valign="middle", lh=1.2, role="subtitle", fx=_enter(2),
        ))
    sub = _item_text(spec.get("subtitle"))
    if sub:
        els.append(_text(
            f"n{si}-sub", MARGIN + 140, 512, CONTENT_W - 280, 60,
            _md_inline(sub), size=FS_LABEL, color=ctx["muted"], weight=400,
            align="center", valign="top", lh=1.45, role="body", fx=_enter(3),
        ))
    return els


def _render_quote(spec: dict, ctx: dict, si: int) -> list:
    els = []
    title = _item_text(spec.get("title"))
    if title:
        els += _content_title(spec, ctx, si)
    els.append(_text(
        f"q{si}-mark", MARGIN, 150, 160, 170, "&quot;", size=FS_QUOTE_MARK,
        color=ctx["accent"], weight=800, align="left", valign="top", lh=0.9,
        fx=_enter(0),
    ))
    els.append(_text(
        f"q{si}-quote", MARGIN + 24, 268, CONTENT_W - 48, 210,
        _md_inline(spec.get("quote") or ""), size=FS_QUOTE, color=ctx["text"],
        weight=500, align="left", valign="top", lh=1.34, role="body",
        fx=_enter(1),
    ))
    attribution = _item_text(spec.get("attribution") or spec.get("author"))
    if attribution:
        els.append(_shape(
            f"q{si}-rule", MARGIN + 26, 512, 44, 3, fill=ctx["accent"], radius=2,
            fx=_enter(2),
        ))
        els.append(_text(
            f"q{si}-attr", MARGIN + 86, 498, CONTENT_W - 120, 32,
            _md_inline(attribution), size=FS_LABEL, color=ctx["muted"],
            weight=600, align="left", valign="middle", lh=1.0, role="body",
            fx=_enter(2),
        ))
    return els


def _render_centered_header(spec: dict, ctx: dict, si: int) -> list:
    els = []
    if spec.get("panel"):
        els.append(_shape(
            f"h{si}-panel", MARGIN, 216, CONTENT_W, 288, fill=ctx["card"],
            stroke=ctx["stroke"], stroke_width=1, radius=ctx["radius"],
            shadow=_card_shadow(ctx["pal"]), fx=_enter(0),
        ))
    els.append(_text(
        f"h{si}-title", MARGIN, 288, CONTENT_W, 120,
        _md_inline(spec.get("title") or ""), size=FS_SECTION_TITLE,
        color=ctx["text"], weight=800, align="center", valign="middle",
        lh=1.12, role="title", fx=_enter(1),
    ))
    sub = _item_text(spec.get("subtitle"))
    if sub:
        els.append(_text(
            f"h{si}-sub", MARGIN + 120, 414, CONTENT_W - 240, 76,
            _md_inline(sub), size=22, color=ctx["muted"], weight=400,
            align="center", valign="top", lh=1.45, role="subtitle",
            fx=_enter(2),
        ))
    return els


RENDERERS = {
    "title": _render_title,
    "divider": _render_divider,
    "closing": _render_closing,
    "bullets": _render_bullets,
    "big_number": _render_big_number,
    "quote": _render_quote,
    "centered_header": _render_centered_header,
    "chart": _render_chart,
    "table": _render_table,
    "metrics": _render_metrics,
    "kpi_row": _render_kpi_row,
    "feature": _render_feature,
    "comparison": _render_comparison,
    "logos": _render_logos,
    "table_of_contents": _render_toc,
    "process": _render_process,
    "timeline": _render_timeline,
}

if __name__ == "__main__":
    sys.exit(main())
