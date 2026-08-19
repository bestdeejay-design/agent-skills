#!/usr/bin/env python3
"""frontend-perfection — static meta/SEO/design-tokens audit (Python stdlib).

Offline, dependency-free check of a static frontend (HTML + CSS):
  - SEO meta layer: title length, meta description, canonical, OG (1200x630
    safe zone awareness), Twitter card, JSON-LD, robots, sitemap reference.
  - Contrast: WCAG 2.x relative luminance computation for color pairs found
    in CSS (`color`/`background-color`) — measured, not eyeballed.
  - Heading order: h1..h6 sequence, exactly one h1.
  - Design tokens: raw hex colors outside the token block (`:root` / tokens
    file) are violations — all colors must live in tokens.
   - Adaptive hints: fixed-header present -> require scroll-padding-top;
     horizontal overflow candidates at tablet widths (media queries with
     min/max-width that don't reflow the container).
   - Accessibility (axe-core rules, offline subset): img-alt (WCAG 1.1.1),
     button-name / link-name (WCAG 4.1.2, 2.4.4), form-label (WCAG 4.1.2,
     3.3.2), aria-valid (WAI-ARIA 1.2), landmark-unique (WCAG 1.3.1).
   - Front-End Checklist-inspired checks: document (doctype/charset/viewport/
     lang/dir/unique-ids/semantics/favicons/manifest/SRI/defer-async),
     images (dimensions/lazy/srcset/format), JS (inline/console),
     CSS quality (focus styles/print/dark-mode/font-display), perf hints
     (preload/preconnect/render-blocking), security (https/noopener),
     privacy & i18n (consent mention/RTL dir).

Usage:
  python3 meta_audit.py --html index.html --css css/main.css [--css css/*.css]
                        [--out report.json] [--json] [--tokens-block ":root"]

Exit codes: 0 = no violations; 1 = at least one violation found.
"""
import argparse
import html.parser
import json
import os
import re
import sys


# ---------------------------------------------------------------- token colors
HEX_RE = re.compile(r"#[\da-fA-F]{3,8}\b")
RGB_RE = re.compile(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)")

# Colors that conventionally live outside the token block without harm:
# base/transparent values. Everything else must be tokenized.
SHADOW_GREYS = {"#000", "#fff"}


def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h)
    if len(h) in (6, 8):
        return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))
    return None


def parse_color(text):
    m = HEX_RE.search(text)
    if m:
        rgb = hex_to_rgb(m.group(0))
        if rgb:
            return rgb
    m = RGB_RE.search(text)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def relative_luminance(rgb):
    """WCAG 2.x relative luminance, 0..1."""
    vals = []
    for c in rgb:
        c = c / 255.0
        vals.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = vals
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a, b):
    la, lb = relative_luminance(a), relative_luminance(b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


# ---------------------------------------------------------------- HTML parsing
class MetaExtractor(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = []
        self.meta = {}          # (attr, name_or_property) -> content
        self.links = []         # (rel, href)
        self.headings = []      # (level, text)
        self.has_jsonld = False
        self._in_title = False
        self._in_script = False
        self._script_tag = None
        # axe-core offline subset: image-alt / button-name / link-name / label / aria-valid-attr / landmark-unique
        self.stack = []            # (tag, attrs, textbuf)
        self.imgs = []
        self.buttons = []
        self.anchors = []
        self.inputs = []
        self.labels_for = []
        self.aria_attrs = []
        self.landmark_main = 0
        self.landmark_navs = []
        self.ids = []
        self.first_top_id = None
        self.top_markers = []
        # Front-End Checklist collectors
        self.html_attrs = {}
        self.link_attrs = []     # {rel, href, integrity, media, as}
        self.scripts = []        # {src, defer, async, type, integrity}
        self.img_details = []    # {src, width, height, loading, srcset}
        self.inline_styles = 0
        self.inline_handlers = 0
        self.style_blocks = 0
        self.http_urls = []
        self.charset = ""
        self.semantic_tags = []
        self.inline_scripts = 0
        self._svg_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.stack.append([tag, attrs, []])
        if tag == "img":
            self.imgs.append("alt" in attrs)
            self.img_details.append({
                "src": attrs.get("src", ""),
                "width": attrs.get("width", ""),
                "height": attrs.get("height", ""),
                "loading": attrs.get("loading", ""),
                "srcset": attrs.get("srcset", ""),
            })
            if attrs.get("src", "").startswith("http://"):
                self.http_urls.append(attrs["src"])
        elif tag == "label":
            self.labels_for.append(attrs.get("for", ""))
        elif tag == "html":
            self.html_attrs = attrs
        elif tag == "main":
            self.landmark_main += 1
        elif tag == "nav":
            self.landmark_navs.append(attrs.get("aria-label") or attrs.get("title") or "")
        elif tag in ("input", "select", "textarea"):
            self.inputs.append({
                "tag": tag,
                "id": attrs.get("id", ""),
                "type": attrs.get("type", ""),
                "aria_label": attrs.get("aria-label"),
                "aria_labelledby": attrs.get("aria-labelledby"),
                "wrapped": any(t == "label" for t, _, _ in self.stack[:-1]),
            })
        for k in attrs:
            if k.startswith("aria-"):
                self.aria_attrs.append(k)
            elif k.startswith("on"):
                self.inline_handlers += 1
        if "style" in attrs:
            self.inline_styles += 1
        if tag == "style":
            self.style_blocks += 1
        aid = attrs.get("id", "")
        if aid:
            self.ids.append(aid)
        if tag in ("header", "section", "footer", "main", "article", "nav"):
            self.semantic_tags.append(tag)
        if tag in ("section", "header", "main") and self.first_top_id is None and aid:
            self.first_top_id = aid
        if tag != "html":
            cls = (attrs.get("class", "") or "").lower()
            lbl = (attrs.get("aria-label", "") or "").lower()
            if re.search(r"(to-?top|scroll-?top|back-?to-?top|totop|^top$)", cls + " " + aid) or re.search(r"(back to top|to top|наверх|вверх)", lbl):
                self.top_markers.append(tag)
        if tag == "title":
            self._in_title = True
        elif tag == "svg":
            self._svg_depth += 1
        elif tag == "meta":
            key = attrs.get("name") or attrs.get("property") or attrs.get("http-equiv") or attrs.get("itemprop")
            if key:
                self.meta[key.lower()] = attrs.get("content", "")
            if attrs.get("charset"):
                self.charset = attrs["charset"]
        elif tag == "link":
            rel = (attrs.get("rel") or "").lower()
            self.links.append((rel, attrs.get("href", "")))
            self.link_attrs.append({
                "rel": rel,
                "href": attrs.get("href", ""),
                "integrity": attrs.get("integrity", ""),
                "media": attrs.get("media", ""),
                "as": attrs.get("as", ""),
            })
            if attrs.get("href", "").startswith("http://"):
                self.http_urls.append(attrs["href"])
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append((tag, ""))
            self._cur_heading = tag
        elif tag == "script":
            t = (attrs.get("type") or "").lower()
            self._script_tag = (t, attrs.get("id", ""))
            self._in_script = True
            self.scripts.append({
                "src": attrs.get("src", ""),
                "defer": "defer" in attrs,
                "async": "async" in attrs,
                "type": t,
                "integrity": attrs.get("integrity", ""),
            })
            if not attrs.get("src") and t not in ("application/ld+json", "application/json"):
                self.inline_scripts += 1
            if attrs.get("src", "").startswith("http://"):
                self.http_urls.append(attrs["src"])
        elif tag == "html":
            pass

    def handle_endtag(self, tag):
        if self.stack:
            popped = self.stack.pop()
            ptag, pattrs, buf = popped
            text = " ".join("".join(buf).split())
            if self.stack:
                self.stack[-1][2].append(text)
            if ptag == "button":
                self.buttons.append({"name": text, "aria": pattrs.get("aria-label") or pattrs.get("aria-labelledby")})
            elif ptag == "a":
                self.anchors.append({
                    "name": text,
                    "aria": pattrs.get("aria-label") or pattrs.get("aria-labelledby") or pattrs.get("title"),
                    "href": pattrs.get("href", ""),
                    "target": pattrs.get("target", ""),
                    "rel": pattrs.get("rel", ""),
                })
                if pattrs.get("href", "").startswith("http://"):
                    self.http_urls.append(pattrs["href"])
        if tag == "title":
            self._in_title = False
        elif tag == "svg":
            self._svg_depth = max(0, self._svg_depth - 1)
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._cur_heading = None
        elif tag == "script":
            self._in_script = False
            self._script_tag = None

    def handle_data(self, data):
        if self.stack:
            self.stack[-1][2].append(data)
        if self._in_title and self._svg_depth == 0:
            self.title.append(data)
        elif getattr(self, "_cur_heading", None):
            # accumulate heading text across nested tags
            for i, (t, txt) in enumerate(self.headings):
                if t == self._cur_heading and i == len(self.headings) - 1:
                    self.headings[i] = (t, txt + " " + data.strip())
        if self._in_script and self._script_tag and self._script_tag[0] in ("application/ld+json",):
            self.has_jsonld = True


# ---------------------------------------------------------------- CSS helpers
def token_block_ranges(css):
    """Indices of :root / tokens blocks (CSS custom property definitions)."""
    ranges = []
    for m in re.finditer(r"(:root|\.tokens|\$\{tokens\}|\btokens\b)\s*\{", css):
        start = m.end() - 1
        depth, i = 1, start + 1
        while i < len(css) and depth:
            if css[i] == "{":
                depth += 1
            elif css[i] == "}":
                depth -= 1
            i += 1
        ranges.append((start, i))
    return ranges


def is_inside(pos, ranges):
    return any(s <= pos < e for s, e in ranges)


def extract_pairs(css):
    """(fg, bg) color pairs from rules, approximated: nearest color declarations
    within the same rule block."""
    pairs = []
    for block in re.finditer(r"\{([^{}]*)\}", css):
        body = block.group(1)
        fg = None
        bg = None
        for m in re.finditer(r"(?:color|background-color|background)\s*:\s*([^;}]+)", body):
            val = m.group(1).strip().split()[0] if m.group(1) else ""
            parsed = parse_color(val)
            if parsed is None:
                continue
            if m.group(0).startswith("color"):
                fg = parsed
            elif m.group(0).startswith("background") and m.group(1).strip().startswith("#"):
                bg = parsed
        if fg and bg:
            pairs.append((fg, bg, body.strip()[:80]))
    return pairs


# ---------------------------------------------------------------- audit core
def audit_meta(ext, path):
    checks = []

    def add(name, ok, detail):
        checks.append({"id": "meta:" + name, "ok": ok, "detail": detail})

    title = " ".join(ext.title).strip()
    add("title", bool(title), f"title tag: {title[:80]!r}")
    if title:
        add("title-length", len(title) <= 60, f"title length {len(title)} (limit 60)")

    desc = ext.meta.get("description", "")
    add("description", bool(desc), f"meta description: {desc[:80]!r}")
    if desc:
        add("description-length", len(desc) <= 160, f"description length {len(desc)} (limit 160)")

    canon = next((h for rel, h in ext.links if "canonical" in rel), "")
    add("canonical", bool(canon), f"canonical: {canon or 'MISSING'}")

    og = {k: v for k, v in ext.meta.items() if k.startswith("og:")}
    add("og:title", bool(og.get("og:title")), "og:title " + ("OK" if og.get("og:title") else "MISSING"))
    add("og:image", bool(og.get("og:image")), "og:image " + ("OK" if og.get("og:image") else "MISSING"))
    ogw = og.get("og:image:width")
    ogh = og.get("og:image:height")
    if og.get("og:image") and ogw and ogh:
        add("og:size", (int(ogw), int(ogh)) == (1200, 630), f"og:image {ogw}x{ogh} (standard 1200x630; crop-safe ~640px content zone)")
    else:
        add("og:size", False, "og:image:width/height not declared — social crop not predictable")

    tw = {k: v for k, v in ext.meta.items() if k.startswith("twitter:")}
    add("twitter:card", bool(tw.get("twitter:card")), "twitter:card " + ("OK" if tw.get("twitter:card") else "MISSING"))

    add("json-ld", ext.has_jsonld, "JSON-LD structured data " + ("found" if ext.has_jsonld else "MISSING"))

    robots = next((v for k, v in ext.meta.items() if k == "robots"), "")
    add("robots", "noindex" not in robots and "nofollow" not in robots, f"robots: {robots or 'not set (crawlable)'}")

    sitemap = any("sitemap" in rel or "sitemap" in h for rel, h in ext.links)
    add("sitemap-link", sitemap, "sitemap link " + ("found" if sitemap else "not referenced"))

    return checks


def audit_headings(ext):
    checks = []
    levels = [int(t[0][1]) for t in ext.headings]
    h1s = [t for t in ext.headings if t[0] == "h1"]
    checks.append({"id": "headings:single-h1", "ok": len(h1s) == 1, "detail": f"{len(h1s)} h1 tag(s)"})
    order_ok = all(b >= a for a, b in zip(levels, levels[1:]))
    # Allow +1 increments only (h1 -> h2 -> h2 -> h3, not h1 -> h3)
    for a, b in zip(levels, levels[1:]):
        if b > a + 1:
            order_ok = False
            break
    checks.append({"id": "headings:order", "ok": order_ok, "detail": " → ".join(f"h{l}" for l in levels) or "(no headings)"})
    return checks


def audit_design_tokens(css, tokens_block=True):
    checks = []
    ranges = token_block_ranges(css) if tokens_block else []
    raw_hex = []
    for m in HEX_RE.finditer(css):
        pos = m.start()
        if is_inside(pos, ranges):
            continue
        val = m.group(0).lower()
        if val in SHADOW_GREYS:
            continue
        raw_hex.append((m.group(0), pos))
    if raw_hex:
        preview = ", ".join(f"{c}@{p}" for c, p in raw_hex[:6])
        tail = f" (+{len(raw_hex) - 6} more)" if len(raw_hex) > 6 else ""
        checks.append({"id": "tokens:raw-hex", "ok": False, "detail": f"{len(raw_hex)} raw hex outside token block: {preview}{tail}"})
    else:
        checks.append({"id": "tokens:raw-hex", "ok": True, "detail": "no raw hex outside token block"})
    return checks


def audit_contrast(css):
    checks = []
    pairs = extract_pairs(css)
    checked = 0
    violations = 0
    for fg, bg, snippet in pairs:
        ratio = contrast_ratio(fg, bg)
        checked += 1
        if ratio < 4.5:
            violations += 1
            checks.append({
                "id": "contrast:wcag-aa",
                "ok": False,
                "detail": f"ratio {ratio:.2f}:1 (< 4.5:1) — {snippet!r}",
            })
    if checked == 0:
        checks.append({"id": "contrast:wcag-aa", "ok": True, "detail": "no explicit fg/bg color pairs found (cannot verify)"})
    elif violations == 0:
        checks.append({"id": "contrast:wcag-aa", "ok": True, "detail": f"all {checked} fg/bg pairs >= 4.5:1"})
    return checks


def audit_adaptive(css):
    checks = []

    fixed_header = re.search(r"position\s*:\s*fixed", css) is not None
    if fixed_header:
        has_sp = re.search(r"scroll-padding-top\s*:", css) is not None
        checks.append({
            "id": "adaptive:scroll-padding",
            "ok": has_sp,
            "detail": "position:fixed found — " + ("scroll-padding-top present" if has_sp else "MISSING scroll-padding-top (anchors hide under header)"),
        })
    else:
        checks.append({"id": "adaptive:scroll-padding", "ok": True, "detail": "no fixed header — no scroll-padding needed"})

    # Horizontal overflow candidates: media min-width breakpoints that don't
    # contain a width-reflow (max-width: 100% / width: auto inside blocks).
    mq = re.findall(r"@media[^{]+\{", css)
    checks.append({
        "id": "adaptive:media-queries",
        "ok": bool(mq),
        "detail": f"{len(mq)} media quer{'y' if len(mq) == 1 else 'ies'}" + ("" if mq else " — responsive breakpoints MISSING for tablet widths (768-1024)"),
    })
    return checks


# ---------------------------------------------------------------- a11y (axe-core subset)
VALID_ARIA = {
    "aria-activedescendant", "aria-atomic", "aria-autocomplete", "aria-braillelabel",
    "aria-brailleroledescription", "aria-busy", "aria-checked", "aria-colcount",
    "aria-colindex", "aria-colindextext", "aria-colspan", "aria-controls", "aria-current",
    "aria-describedby", "aria-description", "aria-details", "aria-disabled", "aria-dropeffect",
    "aria-errormessage", "aria-expanded", "aria-flowto", "aria-grabbed", "aria-haspopup",
    "aria-hidden", "aria-invalid", "aria-keyshortcuts", "aria-label", "aria-labelledby",
    "aria-level", "aria-live", "aria-modal", "aria-multiline", "aria-multiselectable",
    "aria-orientation", "aria-owns", "aria-placeholder", "aria-posinset", "aria-pressed",
    "aria-readonly", "aria-relevant", "aria-required", "aria-roledescription",
    "aria-rowcount", "aria-rowindex", "aria-rowindextext", "aria-rowspan", "aria-selected",
    "aria-setsize", "aria-sort", "aria-valuemax", "aria-valuemin", "aria-valuenow",
    "aria-valuetext",
}


def audit_a11y(ext):
    checks = []

    def add(name, ok, detail):
        checks.append({"id": "a11y:" + name, "ok": ok, "detail": detail})

    bad_imgs = [i for i, has_alt in enumerate(ext.imgs) if not has_alt]
    add("img-alt", not bad_imgs,
        f"{len(ext.imgs)} img, {len(bad_imgs)} without alt attribute (WCAG 1.1.1 / axe image-alt)"
        + (" — decorative images may use empty alt=\"\"" if not bad_imgs else ""))

    bad_btns = [b for b in ext.buttons if not (b["name"] or b["aria"])]
    add("button-name", not bad_btns,
        f"{len(ext.buttons)} buttons, {len(bad_btns)} without accessible name (WCAG 4.1.2 / axe button-name)"
        + (" — icon-only buttons need aria-label" if bad_btns else ""))

    bad_links = [a for a in ext.anchors if not (a["name"] or a["aria"])]
    add("link-name", not bad_links,
        f"{len(ext.anchors)} links, {len(bad_links)} without accessible name (WCAG 4.1.2 / axe link-name)"
        + (" — add text or aria-label" if bad_links else ""))

    bad_inputs = [
        i for i in ext.inputs
        if not (i["aria_label"] or i["aria_labelledby"] or i["wrapped"] or i["id"] in ext.labels_for)
    ]
    add("form-label", not bad_inputs,
        f"{len(ext.inputs)} form fields, {len(bad_inputs)} without label (WCAG 4.1.2 / axe label)"
        + (" — add <label for> or aria-label" if bad_inputs else ""))

    bad_aria = sorted({a for a in ext.aria_attrs if a not in VALID_ARIA})
    add("aria-valid", not bad_aria,
        f"{len(ext.aria_attrs)} aria attributes"
        + (f", invalid: {bad_aria[:5]} (WAI-ARIA 1.2 / axe aria-valid-attr)" if bad_aria
           else " — all valid names (WAI-ARIA 1.2 / axe aria-valid-attr)"))

    lm = []
    if ext.landmark_main > 1:
        lm.append(f"{ext.landmark_main} <main> elements")
    unlabeled_navs = [l for l in ext.landmark_navs if not l]
    if len(unlabeled_navs) > 1:
        lm.append(f"{len(unlabeled_navs)} <nav> without distinct aria-label")
    add("landmark-unique", not lm,
        "; ".join(lm) if lm
        else f"{ext.landmark_main} <main>, {len(ext.landmark_navs)} <nav> — unique (WCAG 1.3.1 / axe landmark-unique)")

    return checks


# ---------------------------------------------------------------- Front-End Checklist extensions
RTL_LANGS = ("ar", "he", "fa", "ur", "yi")
RASTER_EXT = (".jpg", ".jpeg", ".png")
MODERN_EXT = (".webp", ".avif")


def audit_document(ext, html_src):
    checks = []

    def add(name, ok, detail):
        checks.append({"id": "html:" + name, "ok": ok, "detail": detail})

    has_doctype = re.search(r"^\s*<!doctype\s+html", html_src, re.IGNORECASE) is not None
    add("doctype", has_doctype, "HTML5 doctype first line " + ("OK" if has_doctype else "MISSING"))

    add("charset", bool(ext.charset.lower() == "utf-8"),
        f"charset: {ext.charset or 'MISSING'} (expected utf-8)")

    viewport = ext.meta.get("viewport", "")
    add("viewport", bool(viewport), "viewport meta " + ("OK" if viewport else "MISSING (responsive design)"))

    lang = ext.html_attrs.get("lang", "")
    add("lang", bool(lang), f"<html lang>={lang or 'MISSING'} (BCP 47 needed for a11y/SEO)")

    if lang[:2] in RTL_LANGS:
        add("dir-rtl", ext.html_attrs.get("dir") == "rtl",
            f"lang={lang} requires dir=\"rtl\" — " + ("OK" if ext.html_attrs.get("dir") == "rtl" else "MISSING"))
    else:
        add("dir-rtl", True, "no RTL language — dir attribute not required")

    dup_ids = [i for i in set(ext.ids) if ext.ids.count(i) > 1]
    add("unique-id", not dup_ids,
        f"{len(ext.ids)} ids" + (f", duplicates: {dup_ids[:5]}" if dup_ids else " — all unique"))

    sem = set(ext.semantic_tags)
    missing_sem = [t for t in ("header", "main", "footer") if t not in sem]
    add("semantic", not missing_sem,
        f"semantic elements found: {', '.join(sorted(sem)) or 'NONE'}"
        + (f" — missing: {', '.join(missing_sem)}" if missing_sem else ""))

    fav = any("icon" in l["rel"] for l in ext.link_attrs)
    add("favicons", fav, "favicon link " + ("OK" if fav else "MISSING"))

    manifest = any("manifest" in l["rel"] for l in ext.link_attrs)
    add("web-app-manifest", manifest, "manifest.json link " + ("found" if manifest else "not referenced (PWA)"))

    ext_scripts = [s for s in ext.scripts if s["src"]]
    cdn_scripts = [s for s in ext_scripts if s["src"].startswith(("http://", "https://"))]
    no_sri = [s["src"] for s in cdn_scripts if not s["integrity"]]
    add("sri", not no_sri,
        f"{len(cdn_scripts)} CDN scripts"
        + (f", {len(no_sri)} without SRI integrity (CDN tamper protection)" if no_sri else " — SRI present (local scripts exempt)"))

    blocking = [s["src"] for s in ext_scripts if not (s["defer"] or s["async"] or s["type"] == "module")]
    add("defer-async", not blocking,
        f"{len(ext_scripts)} external scripts"
        + (f", {len(blocking)} render-blocking without defer/async/module" if blocking else " — all async/defer/module"))

    untyped = [i for i in ext.inputs if i["tag"] == "input" and not i["type"]]
    add("input-types", not untyped,
        f"{len(ext.inputs)} form fields"
        + (f", {len(untyped)} inputs without type (defaults to text)" if untyped else " — types set"))

    return checks


def audit_images(ext):
    checks = []

    def add(name, ok, detail):
        checks.append({"id": "images:" + name, "ok": ok, "detail": detail})

    imgs = [i for i in ext.img_details if i["src"]]
    no_dim = [i["src"] for i in imgs if not (i["width"] and i["height"])]
    add("dimensions", not no_dim,
        f"{len(imgs)} img" + (f", {len(no_dim)} without width/height (CLS risk)" if no_dim else " — dimensions set"))

    add("lazy-loading", any(i["loading"] == "lazy" for i in imgs) or len(imgs) < 3,
        f"loading=lazy on {sum(1 for i in imgs if i['loading'] == 'lazy')}/{len(imgs)} img — 3+ images should lazy load offscreen content")

    add("srcset", any(i["srcset"] for i in imgs) or len(imgs) < 2,
        "responsive srcset " + ("found" if any(i["srcset"] for i in imgs) else "not used — fixed-size images on varying viewports"))

    raster = [i["src"] for i in imgs if i["src"].lower().endswith(RASTER_EXT)]
    modern = [i["src"] for i in imgs if i["src"].lower().endswith(MODERN_EXT)]
    add("modern-format", not raster or modern,
        f"{len(raster)} raster (jpg/png), {len(modern)} modern (webp/avif)"
        + (" — convert raster to webp/avif" if raster and not modern else ""))

    return checks


def audit_js(ext, html_src):
    checks = []

    def add(name, ok, detail):
        checks.append({"id": "js:" + name, "ok": ok, "detail": detail})

    add("no-inline", ext.inline_handlers == 0 and ext.inline_scripts == 0,
        f"inline JS: {ext.inline_handlers} handler attrs (onclick=…), {ext.inline_scripts} inline <script> blocks — keep JS in external files")

    console_hits = len(re.findall(r"console\.(?:log|debug|warn)\s*\(", html_src))
    add("no-console", console_hits == 0,
        f"{console_hits} console.{'log/debug/warn'} call(s) in HTML — remove before production")

    return checks


def audit_css_quality(css):
    checks = []

    def add(name, ok, detail):
        checks.append({"id": "css:" + name, "ok": ok, "detail": detail})

    add("focus-visible", re.search(r":focus(-visible)?\s*\{", css) is not None,
        "visible focus indicator rule " + ("found" if re.search(r":focus(-visible)?\s*\{", css) else "MISSING — keyboard users need :focus-visible styles"))

    add("print", re.search(r"@media\s+print", css) is not None,
        "print stylesheet (@media print) " + ("found" if re.search(r"@media\s+print", css) else "MISSING"))

    add("dark-mode", re.search(r"prefers-color-scheme", css) is not None,
        "dark mode (prefers-color-scheme) " + ("supported" if re.search(r"prefers-color-scheme", css) else "not implemented"))

    add("font-display", re.search(r"font-display\s*:\s*swap", css) is not None,
        "font-display: swap " + ("set" if re.search(r"font-display\s*:\s*swap", css) else "MISSING — text invisible while webfont loads (FOIT)"))

    return checks


def audit_perf_hints(ext):
    checks = []
    hints = {l["rel"]: l["href"] for l in ext.link_attrs if l["rel"] in ("preload", "preconnect", "dns-prefetch", "prefetch")}
    checks.append({
        "id": "perf:resource-hints",
        "ok": bool(hints),
        "detail": f"resource hints: {', '.join(hints) or 'NONE — add preload/preconnect for critical origins (LCP)'}",
    })
    return checks


def audit_security(ext):
    checks = []

    def add(name, ok, detail):
        checks.append({"id": "security:" + name, "ok": ok, "detail": detail})

    add("https", not ext.http_urls,
        f"{len(ext.http_urls)} http:// URL(s) in src/href" + (" — use https" if ext.http_urls else " — all https"))

    blank = [a["href"] for a in ext.anchors if a["target"] == "_blank" and "noopener" not in (a["rel"] or "")]
    add("noopener", not blank,
        f"{len(blank)} target=_blank link(s) without rel=noopener" + (" — add rel=\"noopener noreferrer\"" if blank else " — ok"))

    return checks


def audit_privacy_i18n(ext, html_src):
    checks = []
    low = html_src.lower()
    consent = any(k in low for k in ("cookie", "consent", "gdpr", "152-фз", "согласие"))
    checks.append({
        "id": "privacy:consent",
        "ok": consent,
        "detail": ("cookie/consent mention found — banner or policy present" if consent
                   else "no cookie/consent mention — check GDPR / 152-ФЗ compliance"),
    })
    return checks


def audit_nav(ext):
    checks = []
    top_ids = {"top", "cover", "hero", "home", "main"}
    if ext.first_top_id:
        top_ids.add(ext.first_top_id)
    has_link = any(
        a.get("href") in ("#", "#top") or a.get("href") == "#" + tid
        for tid in top_ids for a in ext.anchors
    )
    has_btn = bool(ext.top_markers)
    ok = has_link or has_btn
    checks.append({
        "id": "nav:back-to-top",
        "ok": ok,
        "detail": ("back-to-top present (logo link or scroll button)" if ok
                   else "MISSING back-to-top: long pages need a way back — logo links to top and/or a floating scroll-to-top button (arrow in a circle, bottom-right, aria-label, appears after scroll)"),
    })
    return checks

def main():
    ap = argparse.ArgumentParser(description="Static frontend meta/SEO/design-tokens/a11y audit")
    ap.add_argument("--html", required=True, help="Path to index.html")
    ap.add_argument("--css", nargs="+", required=True, help="CSS file(s) — globs expanded by shell")
    ap.add_argument("--out", help="Write JSON report to file")
    ap.add_argument("--json", action="store_true", help="Print report as JSON to stdout")
    args = ap.parse_args()

    if not os.path.isfile(args.html):
        print(f"ERROR: HTML file not found: {args.html}")
        sys.exit(2)

    css_all = []
    for c in args.css:
        if not os.path.isfile(c):
            print(f"ERROR: CSS file not found: {c}")
            sys.exit(2)
        with open(c, encoding="utf-8", errors="replace") as f:
            css_all.append(f.read())
    css = "\n".join(css_all)

    with open(args.html, encoding="utf-8", errors="replace") as f:
        html_src = f.read()

    ext = MetaExtractor()
    ext.feed(html_src)

    checks = []
    checks += audit_meta(ext, args.html)
    checks += audit_headings(ext)
    checks += audit_design_tokens(css, tokens_block=True)
    checks += audit_contrast(css)
    checks += audit_adaptive(css)



    checks += audit_a11y(ext)
    checks += audit_document(ext, html_src)
    checks += audit_images(ext)
    checks += audit_js(ext, html_src)
    checks += audit_css_quality(css)
    checks += audit_perf_hints(ext)
    checks += audit_security(ext)
    checks += audit_privacy_i18n(ext, html_src)
    checks += audit_nav(ext)

    violations = [c for c in checks if not c["ok"]]
    report = {
        "tool": "frontend-perfection/meta_audit",
        "html": args.html,
        "css": args.css,
        "checks": checks,
        "summary": {
            "total": len(checks),
            "passed": len(checks) - len(violations),
            "violations": len(violations),
        },
    }

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"Report written to {args.out}")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"\n[frontend-perfection] meta audit of {args.html}")
        print(f"  checks: {len(checks)}, passed: {report['summary']['passed']}, violations: {len(violations)}")
        for c in checks:
            flag = "✅" if c["ok"] else "❌"
            print(f"  {flag} {c['id']}: {c['detail']}")

    sys.exit(0 if not violations else 1)


if __name__ == "__main__":
    main()