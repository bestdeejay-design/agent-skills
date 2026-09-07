#!/usr/bin/env python3
"""Offline validation gate for Bento presentation files (*.bento.html).

A faithful, browser-free Python reimplementation of the STATIC rules in Bento's
own slides/src/validate.ts (https://github.com/nyblnet/bento, MIT). It is the
Bento-format counterpart of qa_pptx.py: same exit-code discipline, same report
shape, same decorative-exemption philosophy.

Check families:
  * document  — format/version/required keys, unknown keys (Bento silently
                ignores them, so a typo means a property quietly does nothing),
                asset refs, collab secrets, font embedding, unescaped '<';
  * slide     — duplicate ids, transition enum, broken stateOf, state
                adjacency, unreachable hidden slides, missing notes;
  * element   — duplicate ids, morph-key collisions, missing base fields,
                canvas bounds, 96px margins, broken links, dangling connectors,
                fx conflicts (enter-on-morph, countup-on-morph, motion-path +
                enter, dash-march without a dashed stroke), enums, emoji,
                disallowed html tags, type-size floor;
  * chart     — charts-lite is NOT ECharts: non-numeric bar/line/scatter data
                (renders as 0), label on non-pie, function formatters, unknown
                option keys, missing axes, empty series;
  * table     — ragged rows, non-positive column weights;
  * design    — no morph anywhere, no motion moment, unstable chrome ids,
                numeric series rendered as bullet text.

measured is reported false: Bento's text-overflow check needs a real DOM and
this gate is deliberately browser-free, so we do not fake it.

Usage:
  python3 qa_bento.py deck.bento.html
  python3 qa_bento.py deck.bento.html.doc.json --strict
  python3 qa_bento.py deck.bento.html --json report.json --codes
Exit codes: 0 = PASS (no errors), 1 = FAIL, 2 = error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

W, H = 1280, 720
MARGIN = 96
RIGHT_EDGE = W - MARGIN          # 1184
CONTENT_BOTTOM = H - MARGIN      # 624
BODY_FLOOR = 17                  # card/body text floor at 16:9 projection

EXEMPT_PREFIXES = ("chrome-", "decor", "ghost")

_DOC_BLOCK = re.compile(
    r'<script([^>]*application/bento\+json[^>]*)>(.*?)</script>', re.DOTALL)

TRANSITIONS = ("none", "fade", "slide", "zoom", "morph")
ALIGNS = ("left", "center", "right")
VALIGNS = ("top", "middle", "bottom")
FITS = ("contain", "cover", "fill")
SHAPES = ("rect", "ellipse", "triangle", "arrow", "line", "path")
STROKE_STYLES = ("solid", "dashed", "dotted")
LINE_ENDINGS = ("none", "arrow", "dot", "bar")
ENTER_FX = ("fade-up", "fade", "fade-down", "slide-left", "slide-right",
            "slide-up", "slide-down")
KEN_DIRS = ("drift", "out", "in")
ROLES = ("title", "subtitle", "body", "kicker")
HOVER_TYPES = ("focus-group", "reveal")
CHART_PRESETS = ("bar", "line", "pie", "scatter")
CARTESIAN = ("bar", "line", "scatter")

ALLOWED_TAGS = {"b", "i", "u", "s", "code", "br", "span", "p", "div",
                "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6"}
_TAG_RE = re.compile(r"</?([a-zA-Z0-9]+)([^>]*)>")
_NUM_IN_LI = re.compile(r"<li[^>]*>(.*?)</li>", re.DOTALL)

EMOJI_RANGES = ((0x1F000, 0x1FAFF), (0x2600, 0x26FF), (0x2700, 0x27BF),
                (0x2B00, 0x2BFF), (0xFE00, 0xFE0F), (0x1F1E6, 0x1F1FF))

SYSTEM_FONTS = ("-apple-system", "blinkmacsystemfont", "segoe ui", "roboto",
                "helvetica", "arial", "sans-serif", "system-ui", "ui-monospace",
                "sfmono-regular", "menlo", "consolas", "monospace", "serif",
                "georgia", "times", "inherit")

DOC_KEYS = {"format", "version", "docId", "title", "size", "theme", "slides",
            "modified", "meta", "present", "assets", "blobs", "fonts",
            "layouts", "collab", "template", "readonly"}
META_KEYS = {"author", "company", "subject", "event", "keywords"}
PRESENT_KEYS = {"numberHidden", "slideNumber", "controls", "progress",
                "morphSeconds"}
THEME_KEYS = {"background", "color", "accent", "fontFamily", "headingFamily",
              "palette", "chartPalette", "table"}
THEME_PAL_KEYS = {"bg2", "tx2", "accent2", "accent3", "accent4", "accent5",
                  "accent6", "hlink", "folHlink"}
SLIDE_KEYS = {"id", "background", "transition", "elements", "notes", "name",
              "stateOf", "hidden", "hover", "comments", "themeRefs"}
HOVER_KEYS = {"type", "dim", "default"}
EL_BASE_KEYS = {"type", "id", "x", "y", "w", "h", "rotation", "opacity",
                "morphId", "shadow", "blur", "blend", "backdropFilter", "fx",
                "link", "group", "groupId", "showOnHover", "role", "themeRefs"}
EL_TYPE_KEYS = {
    "text": {"html", "fontSize", "fontFamily", "fontWeight", "color",
             "colorGradient", "align", "valign", "lineHeight", "letterSpacing",
             "textStroke", "placeholder"},
    "shape": {"shape", "fill", "fillGradient", "stroke", "strokeWidth",
              "radius", "strokeDash", "strokeStyle", "lineStart", "lineEnd",
              "d", "pathBox", "from", "to"},
    "image": {"src", "fit", "radius"},
    "svg": {"asset", "markup", "css"},
    "chart": {"preset", "option", "source"},
    "table": {"columns", "rows", "header", "style"},
    "media": {"kind", "src", "poster", "fit", "radius", "autoplay", "loop",
              "muted", "controls"},
    "code": {"content", "fontSize", "fontFamily", "align", "valign",
             "lineHeight", "color", "grammarAssetId", "grammarName",
             "themeAssetId", "themeName"},
}
FX_KEYS = {"enter", "enterDur", "order", "countUp", "ambient", "ken", "loop"}
KEN_KEYS = {"dir", "scale", "duration"}
LOOP_KEYS = {"type", "distance", "duration", "path", "delay", "ease", "speeds"}
SHADOW_KEYS = {"x", "y", "blur", "color"}
GRADIENT_KEYS = {"angle", "stops"}
TABLE_STYLE_KEYS = {"headerBg", "headerColor", "zebra", "borderColor",
                    "borderWidth", "cellPadX", "cellPadY", "fontSize",
                    "fontFamily", "color", "radius"}
CELL_KEYS = {"html", "align", "color", "bg", "bold"}
CHART_OPTION_KEYS = {"color", "series", "xAxis", "yAxis", "legend", "grid",
                     "tooltip", "textStyle", "dataZoom"}
CHART_SERIES_KEYS = {"type", "name", "data", "yAxisIndex", "itemStyle",
                     "barWidth", "smooth", "symbol", "symbolSize", "lineStyle",
                     "areaStyle", "radius", "label"}
CHART_AXIS_KEYS = {"type", "data", "min", "max", "axisLabel", "axisLine",
                   "splitLine", "name"}
CHART_LEGEND_KEYS = {"show", "top", "bottom", "textStyle", "itemWidth",
                     "itemHeight", "itemGap", "data"}


def _is_emoji(ch: str) -> bool:
    o = ord(ch)
    return any(a <= o <= b for a, b in EMOJI_RANGES)


def _is_exempt(el_id: str) -> bool:
    return str(el_id).startswith(EXEMPT_PREFIXES)


def _full_bleed(e: dict) -> bool:
    return (e.get("x"), e.get("y"), e.get("w"), e.get("h")) == (0, 0, W, H)


# ===========================================================================
# Extraction
# ===========================================================================

def _extract_doc(path: Path):
    """Return (doc|None, fatal_error|None, unescaped_lt|bool)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    stripped = text.lstrip()
    if stripped.startswith("{"):
        try:
            return json.loads(stripped), None, False
        except json.JSONDecodeError as e:
            return None, f"cannot parse document JSON: {e}", False

    hits = [m for m in _DOC_BLOCK.finditer(text) if "bento-doc" in m.group(1)]
    if not hits:
        return None, ("no <script type=\"application/bento+json\" "
                      "id=\"bento-doc\"> block found — is this a Bento file?"), False
    if len(hits) > 1:
        return None, (f"found {len(hits)} #bento-doc blocks, expected exactly "
                      f"one"), False
    raw = hits[0].group(2)
    unescaped = "<" in raw
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as e:
        return None, f"cannot parse the #bento-doc JSON: {e}", unescaped
    if not isinstance(doc, dict):
        return None, "the #bento-doc block is not a JSON object", unescaped
    return doc, None, unescaped


# ===========================================================================
# Findings
# ===========================================================================

class Findings:
    def __init__(self):
        self.items = []

    def add(self, code, severity, message, slide=None, element=None, path=None):
        f = {"code": code, "severity": severity, "message": message}
        if slide is not None:
            f["slide"] = slide
        if element is not None:
            f["element"] = element
        if path is not None:
            f["path"] = path
        self.items.append(f)

    @property
    def errors(self):
        return [f for f in self.items if f["severity"] == "error"]

    @property
    def warnings(self):
        return [f for f in self.items if f["severity"] == "warning"]

    @property
    def infos(self):
        return [f for f in self.items if f["severity"] == "info"]


def _unknown_keys(obj: dict, allowed: set, where: str, f: Findings,
                  slide=None, element=None):
    extra = set(obj) - allowed
    for k in sorted(extra):
        f.add("unknown-key", "warning",
              f"{where} has unknown key '{k}' — Bento silently ignores unknown "
              f"keys, so this property does nothing (typo?)",
              slide=slide, element=element, path=f"{where}.{k}")


# ===========================================================================
# Document-level checks
# ===========================================================================

def _check_doc(doc: dict, f: Findings, unescaped_lt: bool):
    if unescaped_lt:
        f.add("unescaped-lt", "error",
              "raw '<' inside the #bento-doc block — every '<' must be the "
              "literal escape \\u003c or a </script> in an html string "
              "terminates the block and corrupts the file")
    if doc.get("format") != "bento/slides":
        f.add("bad-format", "error",
              f"format is {doc.get('format')!r}, expected \"bento/slides\"")
    if doc.get("version") != 1:
        f.add("bad-version", "error",
              f"version is {doc.get('version')!r}, expected 1")
    for k in ("docId", "title", "size", "theme", "slides", "modified"):
        if k not in doc:
            f.add("missing-required", "error", f"required root key '{k}' absent")
    _unknown_keys(doc, DOC_KEYS, "document", f)

    size = doc.get("size")
    if isinstance(size, dict):
        if not (isinstance(size.get("width"), (int, float)) and size["width"] > 0):
            f.add("bad-enum", "warning", "size.width must be a positive number",
                  path="size.width")
        if not (isinstance(size.get("height"), (int, float)) and size["height"] > 0):
            f.add("bad-enum", "warning", "size.height must be a positive number",
                  path="size.height")

    theme = doc.get("theme")
    if isinstance(theme, dict):
        _unknown_keys(theme, THEME_KEYS, "theme", f)
        if isinstance(theme.get("palette"), dict):
            _unknown_keys(theme["palette"], THEME_PAL_KEYS, "theme.palette", f)
        for i, fam in enumerate(doc.get("fonts") or []):
            if isinstance(fam, dict) and fam.get("asset"):
                if fam["asset"] not in (doc.get("assets") or {}):
                    f.add("missing-asset", "error",
                          f"fonts[{i}].asset '{fam['asset']}' is not in doc.assets",
                          path=f"fonts[{i}].asset")
    collab = doc.get("collab")
    if isinstance(collab, dict) and collab.get("writerPriv"):
        f.add("collab-secrets-present", "info",
              "collab.writerPriv is present — this copy can write to the room; "
              "strip it before sharing")

    present = doc.get("present")
    if isinstance(present, dict):
        _unknown_keys(present, PRESENT_KEYS, "present", f)


# ===========================================================================
# Slide / element checks
# ===========================================================================

def _check_text_html(html, f, slide, eid):
    if not isinstance(html, str):
        return
    if any(_is_emoji(c) for c in html):
        f.add("emoji-in-text", "warning",
              "html contains an emoji/pictographic character — Bento decks use "
              "SVG or shape icons, never emoji", slide=slide, element=eid)
    for m in _TAG_RE.finditer(html):
        tag, attrs = m.group(1).lower(), m.group(2)
        if tag not in ALLOWED_TAGS:
            f.add("disallowed-html-tag", "warning",
                  f"tag <{tag}> is outside Bento's inline-HTML subset "
                  f"({', '.join(sorted(ALLOWED_TAGS))})",
                  slide=slide, element=eid)
        elif attrs.strip():
            f.add("disallowed-html-tag", "warning",
                  f"tag <{tag}> carries an attribute — Bento's html subset is "
                  f"attribute-free", slide=slide, element=eid)


def _check_chart(el, f, slide, eid):
    opt = el.get("option")
    if not isinstance(opt, dict):
        f.add("chart-key-ignored", "warning", "chart.option must be an object",
              slide=slide, element=eid, path="option")
        return
    _unknown_keys(opt, CHART_OPTION_KEYS, "chart.option", f, slide, eid)
    series = opt.get("series")
    if not isinstance(series, list) or not series:
        f.add("chart-empty-series", "warning", "chart has no series",
              slide=slide, element=eid, path="option.series")
        return
    for si, s in enumerate(series):
        if not isinstance(s, dict):
            continue
        p = f"option.series[{si}]"
        _unknown_keys(s, CHART_SERIES_KEYS, p, f, slide, eid)
        kind = s.get("type")
        data = s.get("data")
        if not isinstance(data, list) or not data:
            f.add("chart-empty-series", "warning", f"{p}.data is empty",
                  slide=slide, element=eid, path=f"{p}.data")
        if kind in CARTESIAN:
            for di, v in enumerate(data or []):
                if isinstance(v, dict) or isinstance(v, (str, bool)) or v is None:
                    f.add("chart-nonnumeric-data", "error",
                          f"{p}.data[{di}] is {type(v).__name__}, not a plain "
                          f"number — charts-lite coerces it to 0 (only pie "
                          f"accepts {{name,value}} objects)",
                          slide=slide, element=eid, path=f"{p}.data[{di}]")
            if "label" in s:
                f.add("chart-label-ignored", "warning",
                      f"{p}.label does nothing on {kind} — value labels work on "
                      f"pie only", slide=slide, element=eid, path=f"{p}.label")
        for where, sub in (("label", s.get("label")), ("tooltip", opt.get("tooltip")),
                           ("axisLabel", None)):
            if isinstance(sub, dict):
                for fk, fv in sub.items():
                    if fk == "formatter" and not isinstance(fv, str):
                        f.add("chart-function-formatter", "error",
                              f"{p}.{where}.formatter must be a template string "
                              f"({{b}}, {{c}}, {{d}}), never a function",
                              slide=slide, element=eid, path=f"{p}.{where}.formatter")
    preset = el.get("preset")
    if preset in CARTESIAN and ("xAxis" not in opt or "yAxis" not in opt):
        f.add("chart-missing-axis", "warning",
              f"cartesian preset '{preset}' needs both xAxis and yAxis",
              slide=slide, element=eid, path="option")


def _check_table(el, f, slide, eid):
    cols = el.get("columns")
    rows = el.get("rows")
    ncol = len(cols) if isinstance(cols, list) else 0
    if isinstance(cols, list):
        for ci, c in enumerate(cols):
            w = c.get("w") if isinstance(c, dict) else None
            if not (isinstance(w, (int, float)) and w > 0):
                f.add("table-bad-weight", "warning",
                      f"columns[{ci}].w must be a positive number",
                      slide=slide, element=eid, path=f"columns[{ci}].w")
    if isinstance(rows, list):
        for ri, r in enumerate(rows):
            cells = r.get("cells") if isinstance(r, dict) else None
            if ncol and isinstance(cells, list) and len(cells) != ncol:
                f.add("table-ragged-rows", "warning",
                      f"rows[{ri}] has {len(cells)} cells but the table declares "
                      f"{ncol} columns", slide=slide, element=eid,
                      path=f"rows[{ri}].cells")
    style = el.get("style")
    if isinstance(style, dict):
        _unknown_keys(style, TABLE_STYLE_KEYS, "table.style", f, slide, eid)


def _check_element(e, f, slide, idx, size, prev_morph_keys, arriving_morph):
    eid = e.get("id", "?")
    etype = e.get("type")
    for k in ("id", "x", "y", "w", "h", "rotation", "opacity"):
        if k not in e:
            f.add("missing-element-field", "error",
                  f"element is missing required base field '{k}' — Bento needs "
                  f"the full set id,x,y,w,h,rotation,opacity",
                  slide=slide, element=eid, path=k)
    if not (isinstance(e.get("w"), (int, float)) and e["w"] > 0) or \
       not (isinstance(e.get("h"), (int, float)) and e["h"] > 0):
        f.add("zero-size", "error", f"w/h must be positive (got "
              f"w={e.get('w')}, h={e.get('h')})", slide=slide, element=eid)
    op = e.get("opacity")
    if op is not None and not (isinstance(op, (int, float)) and 0 <= op <= 1):
        f.add("bad-opacity", "warning", f"opacity {op} outside 0..1",
              slide=slide, element=eid)

    x, y = e.get("x", 0), e.get("y", 0)
    w, h = e.get("w", 0), e.get("h", 0)
    if isinstance(x, (int, float)) and isinstance(y, (int, float)) \
            and isinstance(w, (int, float)) and isinstance(h, (int, float)):
        sw, sh = size.get("width", W), size.get("height", H)
        if not _is_exempt(eid) and not _full_bleed(e):
            if x < 0 or y < 0 or x + w > sw or y + h > sh:
                f.add("out-of-canvas", "warning",
                      f"element extends outside the {sw}x{sh} canvas "
                      f"(x={x}, y={y}, w={w}, h={h})", slide=slide, element=eid)
            if etype in ("text", "table") and (
                    x < MARGIN or x + w > RIGHT_EDGE or y + h > CONTENT_BOTTOM):
                f.add("past-margin", "info",
                      f"content crosses the {MARGIN}px margin or ends below "
                      f"y={CONTENT_BOTTOM}", slide=slide, element=eid)

    for field, allowed in (("align", ALIGNS), ("valign", VALIGNS),
                           ("fit", FITS), ("shape", SHAPES),
                           ("strokeStyle", STROKE_STYLES),
                           ("lineStart", LINE_ENDINGS),
                           ("lineEnd", LINE_ENDINGS), ("role", ROLES)):
        v = e.get(field)
        if v is not None and v not in allowed:
            f.add("bad-enum", "warning",
                  f"{field}={v!r} invalid — allowed: {', '.join(allowed)}",
                  slide=slide, element=eid, path=field)

    if etype == "text":
        _check_text_html(e.get("html", ""), f, slide, eid)
        fs = e.get("fontSize")
        # 15px is the caption/timeline-description floor; chrome and decor are
        # intentionally smaller. The stricter 17px body floor is enforced by
        # build_bento.py and deck_audit.py, not here.
        if not _is_exempt(eid) and isinstance(fs, (int, float)) and fs < 15:
            f.add("text-too-small", "warning",
                  f"fontSize {fs} is below the 15px caption floor — illegible "
                  f"at 16:9 projection", slide=slide, element=eid)
    if etype == "table":
        _check_table(e, f, slide, eid)
    if etype == "chart":
        _check_chart(e, f, slide, eid)
    if etype == "svg" and not (e.get("asset") or e.get("markup")):
        f.add("missing-asset", "error", "svg element needs either asset or markup",
              slide=slide, element=eid)
    if etype == "image" and not e.get("src"):
        f.add("missing-asset", "error", "image element needs a src",
              slide=slide, element=eid)

    fx = e.get("fx")
    if isinstance(fx, dict):
        _unknown_keys(fx, FX_KEYS, "fx", f, slide, eid)
        if fx.get("enter") is not None and fx["enter"] not in ENTER_FX:
            f.add("bad-enum", "warning",
                  f"fx.enter={fx['enter']!r} invalid — allowed: "
                  f"{', '.join(ENTER_FX)}", slide=slide, element=eid,
                  path="fx.enter")
        ken = fx.get("ken")
        if isinstance(ken, dict):
            _unknown_keys(ken, KEN_KEYS, "fx.ken", f, slide, eid)
            if ken.get("dir") is not None and ken["dir"] not in KEN_DIRS:
                f.add("bad-enum", "warning",
                      f"fx.ken.dir={ken['dir']!r} invalid — allowed: "
                      f"{', '.join(KEN_DIRS)}", slide=slide, element=eid,
                      path="fx.ken.dir")
        loop = fx.get("loop")
        if isinstance(loop, dict):
            _unknown_keys(loop, LOOP_KEYS, "fx.loop", f, slide, eid)
            lt = loop.get("type")
            if lt == "dash-march" and e.get("strokeStyle") not in ("dashed", "dotted"):
                f.add("dash-march-no-dash", "warning",
                      "dash-march loop on a shape without a dashed/dotted "
                      "stroke — nothing visibly animates",
                      slide=slide, element=eid, path="fx.loop")
            if lt == "motion-path":
                if not loop.get("path"):
                    f.add("bad-enum", "warning", "motion-path loop needs a path",
                          slide=slide, element=eid, path="fx.loop.path")
                if fx.get("enter"):
                    f.add("entrance-on-motion-path", "warning",
                          "fx.enter combined with a motion-path loop — both "
                          "fight over the same CSS transform",
                          slide=slide, element=eid, path="fx")
        if arriving_morph:
            if fx.get("enter"):
                f.add("overridden-enter-fx", "warning",
                      "fx.enter on an element that arrives via morph — Bento "
                      "skips the entrance (the element tweens in instead)",
                      slide=slide, element=eid, path="fx.enter")
            if fx.get("countUp"):
                f.add("inert-countup", "info",
                      "fx.countUp on a morph-arriving element — skipped by "
                      "design, the element already shows its value",
                      slide=slide, element=eid, path="fx.countUp")

    sh = e.get("shadow")
    if isinstance(sh, dict):
        _unknown_keys(sh, SHADOW_KEYS, "shadow", f, slide, eid)
    if isinstance(sh, list):
        for i, s in enumerate(sh):
            if isinstance(s, dict):
                _unknown_keys(s, SHADOW_KEYS, f"shadow[{i}]", f, slide, eid)
    grad = e.get("fillGradient") or e.get("colorGradient")
    if isinstance(grad, dict):
        _unknown_keys(grad, GRADIENT_KEYS, "gradient", f, slide, eid)

    _unknown_keys(e, EL_BASE_KEYS | EL_TYPE_KEYS.get(etype, set()),
                  f"element[{etype}]", f, slide, eid)


def _check_slide(s, f, idx, slide_ids, doc_assets):
    sid = s.get("id", "?")
    for k in ("id", "background", "transition", "elements", "notes"):
        if k not in s:
            f.add("missing-required", "error",
                  f"slide '{sid}' missing required key '{k}'", slide=idx + 1)
    tr = s.get("transition")
    if tr is None or tr not in TRANSITIONS:
        f.add("missing-transition", "warning",
              f"transition={tr!r} invalid — allowed: {', '.join(TRANSITIONS)}",
              slide=idx + 1)
    _unknown_keys(s, SLIDE_KEYS, "slide", f, slide=idx + 1)

    if s.get("stateOf"):
        if s["stateOf"] not in slide_ids:
            f.add("broken-state-parent", "error",
                  f"stateOf references nonexistent slide '{s['stateOf']}'",
                  slide=idx + 1)
    notes = s.get("notes")
    if not (isinstance(notes, str) and notes.strip()):
        f.add("missing-notes", "info",
              "slide has no speaker notes — notes travel inside the file, so "
              "an empty one is a missed opportunity", slide=idx + 1)

    hover = s.get("hover")
    if isinstance(hover, dict):
        _unknown_keys(hover, HOVER_KEYS, "hover", f, slide=idx + 1)
        if hover.get("type") not in HOVER_TYPES:
            f.add("bad-enum", "warning",
                  f"hover.type={hover.get('type')!r} invalid — allowed: "
                  f"{', '.join(HOVER_TYPES)}", slide=idx + 1, path="hover.type")


# ===========================================================================
# Main pass
# ===========================================================================

def _run(doc: dict, unescaped_lt: bool):
    f = Findings()
    _check_doc(doc, f, unescaped_lt)

    slides = doc.get("slides")
    if not isinstance(slides, list):
        f.add("missing-required", "error", "slides must be an array")
        return f, doc
    slide_ids = [s.get("id") for s in slides if isinstance(s, dict)]
    size = doc.get("size") if isinstance(doc.get("size"), dict) else {"width": W, "height": H}
    doc_assets = doc.get("assets") if isinstance(doc.get("assets"), dict) else {}

    seen_slide_ids = set()
    for i, sid in enumerate(slide_ids):
        if sid in seen_slide_ids:
            f.add("duplicate-slide-id", "error", f"slide id '{sid}' used twice",
                  slide=i + 1)
        seen_slide_ids.add(sid)

    inbound_links = set()
    for s in slides:
        if isinstance(s, dict):
            for e in s.get("elements") or []:
                if isinstance(e, dict) and e.get("link"):
                    inbound_links.add(e["link"])

    prev_morph_keys = set()
    prev_transition = None
    for idx, s in enumerate(slides):
        if not isinstance(s, dict):
            continue
        _check_slide(s, f, idx, set(slide_ids), doc_assets)
        sid = s.get("id", "?")
        arriving = (prev_transition == "morph")

        seen, morphs = set(), set()
        cur_morph_keys = set()
        for e in s.get("elements") or []:
            if not isinstance(e, dict):
                continue
            eid = e.get("id", "?")
            if eid in seen:
                f.add("duplicate-id", "error",
                      f"two elements on this slide share id '{eid}'",
                      slide=idx + 1, element=eid)
            seen.add(eid)
            mk = e.get("morphId") or eid
            if mk in morphs:
                f.add("morph-key-collision", "error",
                      f"two elements on this slide share morph key '{mk}' "
                      f"(morph keys must be unique per slide)",
                      slide=idx + 1, element=eid)
            morphs.add(mk)
            cur_morph_keys.add(mk)

            is_arriving = arriving and mk in prev_morph_keys
            _check_element(e, f, idx + 1, idx, size, prev_morph_keys, is_arriving)

            if e.get("link") and e["link"] not in set(slide_ids):
                f.add("broken-link", "error",
                      f"link references nonexistent slide '{e['link']}'",
                      slide=idx + 1, element=eid)
            for key in ("from", "to"):
                ref = e.get(key)
                if isinstance(ref, dict) and ref.get("el") and \
                        ref["el"] not in seen and ref["el"] not in {
                            x.get("id") for x in (s.get("elements") or [])
                            if isinstance(x, dict)}:
                    f.add("dangling-connector", "warning",
                          f"{key}.el references element '{ref['el']}' which is "
                          f"not on this slide", slide=idx + 1, element=eid)
            for src in (e.get("src"), e.get("asset")):
                if isinstance(src, str) and src.startswith("asset:"):
                    key = src[len("asset:"):]
                    if key not in doc_assets:
                        f.add("missing-asset", "error",
                              f"asset ref '{src}' is not in doc.assets",
                              slide=idx + 1, element=eid)
            if e.get("type") == "text":
                fam = e.get("fontFamily")
                if isinstance(fam, str) and fam and fam != "inherit":
                    first = fam.split(",")[0].strip().strip("'\"").lower()
                    if first and first not in SYSTEM_FONTS and not any(
                            (ff.get("family") or "").split(",")[0].strip()
                            .strip("'\"").lower() == first
                            for ff in (doc.get("fonts") or [])
                            if isinstance(ff, dict)):
                        f.add("font-not-embedded", "info",
                              f"fontFamily '{fam}' is neither embedded in "
                              f"doc.fonts nor a system font — it will silently "
                              f"fall back on other machines",
                              slide=idx + 1, element=eid)

        if s.get("hidden") or s.get("stateOf"):
            if sid not in inbound_links:
                f.add("unreachable-hidden-slide", "info",
                      "hidden/state slide has no inbound link — it can never be "
                      "reached", slide=idx + 1)
        if s.get("stateOf"):
            parent_i = slide_ids.index(s["stateOf"]) if s["stateOf"] in slide_ids else -1
            if parent_i != idx - 1:
                f.add("state-not-adjacent", "warning",
                      "state slide is not immediately after its parent — Bento "
                      "expects adjacency", slide=idx + 1)

        prev_morph_keys = cur_morph_keys
        prev_transition = s.get("transition")

    _design_checks(doc, slides, f)
    return f, doc


def _design_checks(doc, slides, f):
    non_state = [s for s in slides if isinstance(s, dict) and not s.get("stateOf")]
    if len(non_state) >= 3 and not any(
            s.get("transition") == "morph" for s in non_state):
        f.add("no-morph-anywhere", "warning",
              "deck has >= 3 slides but not a single transition:\"morph\" — "
              "morph is Bento's signature move and is almost always missed")
    motion = 0
    for s in slides:
        for e in (s.get("elements") or []) if isinstance(s, dict) else []:
            fx = e.get("fx") if isinstance(e, dict) else None
            if isinstance(fx, dict) and (fx.get("countUp") or fx.get("ambient")
                                         or fx.get("loop")):
                motion += 1
    if not motion:
        f.add("no-motion-moment", "warning",
              "no element uses fx.countUp, fx.ambient or fx.loop — covers and "
              "dividers should not be dead static")

    chrome_sets = []
    for s in non_state:
        ids = {e.get("id") for e in (s.get("elements") or [])
               if isinstance(e, dict) and str(e.get("id", "")).startswith("chrome-")}
        chrome_sets.append(frozenset(ids))
    if len(chrome_sets) >= 3:
        common = set.intersection(*[set(c) for c in chrome_sets]) if chrome_sets else set()
        if any(c != chrome_sets[0] for c in chrome_sets) and common:
            f.add("static-chrome", "info",
                  "chrome-* ids are not identical across slides, so chrome pops "
                  "instead of morphing in place")

    for idx, s in enumerate(slides):
        if not isinstance(s, dict):
            continue
        for e in s.get("elements") or []:
            if not isinstance(e, dict) or e.get("type") != "text":
                continue
            html = e.get("html") or ""
            nums = 0
            for li in _NUM_IN_LI.findall(html):
                if re.search(r"\d", li):
                    nums += 1
            if nums >= 4:
                f.add("numbers-as-text", "info",
                      "a numeric series is rendered as bullet text — reach for "
                      "a chart element instead", slide=idx + 1,
                      element=e.get("id"))


# ===========================================================================
# Entry point
# ===========================================================================

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Offline validation gate for Bento decks (*.bento.html)")
    ap.add_argument("bento", help="a .bento.html file or a bare .doc.json document")
    ap.add_argument("--json", default=None, help="write a machine-readable report here")
    ap.add_argument("--strict", action="store_true", help="fail on warnings too")
    ap.add_argument("--max-warnings", type=int, default=-1,
                    help="fail when warnings exceed N (default -1 = unlimited)")
    ap.add_argument("--codes", action="store_true",
                    help="print only sorted unique finding codes")
    ap.add_argument("--quiet", action="store_true", help="print only the verdict line")
    args = ap.parse_args()

    path = Path(args.bento)
    if not path.is_file():
        print(f"error: {path} not found", file=sys.stderr)
        return 2
    try:
        doc, fatal, unescaped = _extract_doc(path)
    except OSError as e:
        print(f"error: cannot read {path}: {e}", file=sys.stderr)
        return 2

    if fatal:
        print(f"error: {fatal}", file=sys.stderr)
        return 2

    f, doc = _run(doc, unescaped)
    errors, warnings, infos = f.errors, f.warnings, f.infos

    verdict = "PASS" if not errors else "FAIL"
    if verdict == "PASS" and args.strict and warnings:
        verdict = "FAIL"
    if verdict == "PASS" and 0 <= args.max_warnings < len(warnings):
        verdict = "FAIL"

    n_slides = len(doc.get("slides") or [])
    n_elements = sum(len(s.get("elements") or []) for s in doc.get("slides") or []
                     if isinstance(s, dict))

    if args.codes:
        for c in sorted({i["code"] for i in f.items}):
            print(c)
    elif not args.quiet:
        print(f"{verdict}  {n_slides} slides, {n_elements} elements — "
              f"{len(errors)} errors, {len(warnings)} warnings, {len(infos)} infos")
        for i in f.items:
            loc = f"[slide {i['slide']}]" if i.get("slide") is not None else "[doc]"
            el = f" {i['element']}:" if i.get("element") else ""
            print(f"  {i['code']:24s} {loc:>12s}{el} {i['message']}")

    report = {
        "deck": str(path),
        "format": doc.get("format"),
        "version": doc.get("version"),
        "slides": n_slides,
        "elements": n_elements,
        "measured": False,
        "findings": f.items,
        "counts": {"errors": len(errors), "warnings": len(warnings),
                   "infos": len(infos), "total": len(f.items)},
        "verdict": verdict,
    }
    if args.json:
        Path(args.json).write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                   encoding="utf-8")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
