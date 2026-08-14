#!/usr/bin/env python3
"""presentation-maker — aesthetic-quality gate for a deck spec (deck.json).

Complements the *functional* overflow check in deck-html/scripts/verify_slides.py
(Chromium layout QA) with a *mechanical* aesthetic gate that enforces
"looks coherent / no worse":

  - contrast:wcag     WCAG 2.x relative-luminance contrast for palette pairs
  - tokens:raw-hex    no raw hex outside the :root token block (design-system rule)
  - palette:roles     <=4 accent roles (primary + graph colors)
  - headline:assertion titles are assertions (full sentence w/ verb), not topics
  - density:words     words-per-slide budget (standard / text-heavy)
  - consistency:mood  a single theme.mood across the whole deck

The WCAG relative-luminance + contrast math is REPLICATED INLINE (not imported)
from skills/frontend-perfection/scripts/meta_audit.py — see relative_luminance()
and contrast_ratio() below. The token-block scan (token_block_ranges / is_inside)
reuses the same idea. Attribution: "borrowed from frontend-perfection".

Usage:
    python3 deck_audit.py deck.json [--html slides.html] [--out report.json]

Exit codes:
    0 = no FAIL (warns allowed)
    1 = at least one FAIL
    2 = usage / IO error

Deterministic: same input -> identical report (no randomness, stable ordering).
Pure Python 3 standard library.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

# ----------------------------------------------------------------- WCAG math
# Borrowed from skills/frontend-perfection/scripts/meta_audit.py
# (relative_luminance / contrast_ratio). Replicated inline so this gate has no
# runtime dependency on frontend-perfection.
def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h)
    if len(h) in (6, 8):
        return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))
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


# ----------------------------------------------------------------- helpers
HEX_RE = re.compile(r"#[\da-fA-F]{3,8}\b")
# Colors that conventionally live outside the token block without harm.
SHADOW_GREYS = {"#000", "#fff", "#000000", "#ffffff"}

# Slide types whose title is allowed to be a topic (not an assertion).
NON_ASSERTION_TYPES = {"title", "divider", "closing", "cover", "section"}

# WCAG AA thresholds.
AA_NORMAL = 4.5   # normal text
AA_LARGE = 3.0    # large text / non-text (graph lines, borders)
AAA_NORMAL = 7.0  # stretch goal
AAA_LARGE = 4.5   # stretch goal

# Small EN verb lexicon for the assertion-headline heuristic (advisory only).
EN_VERBS = {
    "is", "are", "was", "were", "be", "been", "being", "am",
    "has", "have", "had", "will", "would", "shall", "should", "can", "could",
    "may", "might", "must", "do", "does", "did", "done",
    "grows", "grew", "growth", "rose", "rises", "fall", "fell", "falls",
    "increased", "increases", "decrease", "decreases", "reduced", "reduces",
    "improves", "improve", "drives", "drive", "shows", "show", "proves",
    "prove", "enables", "enable", "delivers", "deliver", "cuts", "cut",
    "boosts", "boost", "saves", "save", "builds", "build", "creates",
    "create", "leads", "lead", "means", "make", "makes", "turns", "reach",
    "reaches", "hit", "hits", "beats", "beat", "wins", "win", "lose", "loses",
    "needs", "need", "offers", "offer", "provides", "provide", "transforms",
    "transform", "accelerates", "accelerate", "doubles", "double", "triples",
    "triple", "exceeds", "exceed", "surpasses", "surpass", "outperforms",
    "outperform", "generates", "generate", "yields", "yield", "supports",
    "support", "requires", "require", "ensures", "ensure", "guarantees",
    "guarantee", "prevents", "prevent", "eliminates", "eliminate", "solves",
    "solve", "unlocks", "unlock", "powers", "power", "fuels", "fuel",
    "scales", "scale", "declines", "decline", "drops", "drop", "plunges",
    "soars", "climbs", "climb", "jumps", "jump", "shifts", "shift", "changes",
    "change", "moves", "move", "stays", "remains", "remain", "holds", "keep",
    "keeps", "sets", "set", "puts", "put", "helps", "help", "lets", "drives",
    "delivers", "matters", "matter", "works", "work", "fails", "fail",
    "wins", "loses", "gains", "gain", "costs", "cost", "earns", "earn",
}

# RU verb suffixes (heuristic). Advisory only — false positives are acceptable
# because a miss just downgrades a title to "warn".
RU_VERB_SUFFIXES = (
    "ться", "тся", "ешь", "ет", "ем", "ете", "ут", "ют",
    "ишь", "ит", "им", "ите", "ат", "ят",
    "ла", "ло", "ли",  # past tense (after a consonant stem)
    "лся", "лась", "лось", "лись",  # reflexive past tense
)


def looks_like_ru_verb(word):
    w = word.lower()
    if len(w) < 3:
        return False
    for suf in RU_VERB_SUFFIXES:
        if w.endswith(suf):
            return True
    # past tense ending in hard consonant + "л" (e.g. "рос", "вёл" -> "вел")
    if w.endswith("л") and w[-2] not in "аеёиоуыэюя":
        return True
    return False


def detect_verb(word):
    w = word.lower().strip(".,;:!?\"'()")
    if not w:
        return False
    if w in EN_VERBS:
        return True
    if w.endswith("s") and w[:-1] in EN_VERBS:
        return True
    if w.endswith("ed") or w.endswith("ing"):
        # crude English verb inflection marker
        return True
    if looks_like_ru_verb(w):
        return True
    return False


def count_words(text):
    if not text:
        return 0
    return len(re.findall(r"[A-Za-zА-Яа-яЁё0-9']+", text))


# ----------------------------------------------------------------- token scan (borrowed idea from frontend-perfection)
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


# ----------------------------------------------------------------- deck loading
def load_deck(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_palette(deck):
    theme = deck.get("theme", {}) or {}
    pal = dict(theme.get("palette", {}) or {})
    # graph colors: explicit graph_0..graph_4, else theme.graphs array
    graphs = []
    for i in range(5):
        k = f"graph_{i}"
        if k in pal:
            graphs.append(pal[k])
    if not graphs and isinstance(theme.get("graphs"), list):
        graphs = list(theme["graphs"])
    return theme, pal, graphs


def norm_hex(v):
    if not isinstance(v, str):
        return None
    v = v.strip()
    if not v:
        return None
    if v.startswith("#"):
        return v.lower()
    return "#" + v.lower()


# ----------------------------------------------------------------- checks
def check_contrast(theme, pal, graphs):
    """contrast:wcag — WCAG relative-luminance contrast for palette pairs."""
    # defaults mirror deck-html/scripts/build_html.py
    primary_text = norm_hex(pal.get("primary_text", "#1C1C1E"))
    background = norm_hex(pal.get("background", "#FFFFFF"))
    card = norm_hex(pal.get("card", "#F5F5F7"))
    on_primary = norm_hex(pal.get("background_text", "#FFFFFF"))
    primary = norm_hex(pal.get("primary", "#007AFF"))
    muted = norm_hex(pal.get("muted", "#6E6E73"))

    pairs = [
        ("primary_text on background", primary_text, background, AA_NORMAL),
        ("primary_text on card", primary_text, card, AA_NORMAL),
        ("on_primary (background_text) on primary", on_primary, primary, AA_NORMAL),
        ("muted on background", muted, background, AA_NORMAL),
    ]
    for i, g in enumerate(graphs):
        pairs.append((f"graph_{i} on background", norm_hex(g), background, AA_LARGE))

    details = []
    failed = False
    for label, fg_s, bg_s, thr in pairs:
        fg = hex_to_rgb(fg_s) if fg_s else None
        bg = hex_to_rgb(bg_s) if bg_s else None
        if fg is None or bg is None:
            details.append(f"{label}: SKIP (missing/invalid color)")
            continue
        ratio = contrast_ratio(fg, bg)
        ok = ratio >= thr
        if not ok:
            failed = True
        aaa = "AAA" if ratio >= (AAA_NORMAL if thr == AA_NORMAL else AAA_LARGE) else "AA"
        details.append(
            f"{label}: {ratio:.2f}:1 (need >= {thr:g}:1, {aaa} stretch)"
        )
    status = "fail" if failed else "pass"
    return {
        "id": "contrast:wcag",
        "title": "WCAG contrast for palette pairs",
        "status": status,
        "detail": "; ".join(details),
    }


def check_tokens(deck, html_path):
    """tokens:raw-hex — no raw hex outside :root, or valid palette hex."""
    if html_path:
        try:
            with open(html_path, encoding="utf-8", errors="replace") as f:
                css = f.read()
        except OSError as e:
            return {
                "id": "tokens:raw-hex",
                "title": "No raw hex outside token block",
                "status": "fail",
                "detail": f"cannot read HTML: {e}",
            }
        ranges = token_block_ranges(css)
        stray = []
        for m in HEX_RE.finditer(css):
            pos = m.start()
            if is_inside(pos, ranges):
                continue
            val = m.group(0).lower()
            if val in SHADOW_GREYS:
                continue
            stray.append((m.group(0), pos))
        if stray:
            preview = ", ".join(f"{c}@{p}" for c, p in stray[:6])
            tail = f" (+{len(stray) - 6} more)" if len(stray) > 6 else ""
            return {
                "id": "tokens:raw-hex",
                "title": "No raw hex outside token block",
                "status": "fail",
                "detail": f"{len(stray)} raw hex outside :root token block: {preview}{tail}",
            }
        return {
            "id": "tokens:raw-hex",
            "title": "No raw hex outside token block",
            "status": "pass",
            "detail": "no raw hex outside :root token block",
        }
    # no HTML: validate deck.json palette values are valid 6-digit hex
    theme, pal, graphs = get_palette(deck)
    bad = []
    for key in ("primary", "background", "card", "stroke", "background_text",
                "primary_text", "muted", "accent_soft"):
        v = pal.get(key)
        if v is None:
            continue
        nv = norm_hex(v)
        if nv is None or not re.fullmatch(r"#[0-9a-f]{6}", nv):
            bad.append(f"{key}={v!r}")
    for i, g in enumerate(graphs):
        nv = norm_hex(g)
        if nv is None or not re.fullmatch(r"#[0-9a-f]{6}", nv):
            bad.append(f"graph_{i}={g!r}")
    if bad:
        return {
            "id": "tokens:raw-hex",
            "title": "Palette values are valid 6-digit hex",
            "status": "fail",
            "detail": f"invalid palette hex: {', '.join(bad)}",
        }
    return {
        "id": "tokens:raw-hex",
        "title": "Palette values are valid 6-digit hex",
        "status": "pass",
        "detail": "all palette values are valid 6-digit hex",
    }


def check_palette_roles(theme, pal, graphs):
    """palette:roles — <=4 accent roles (primary + graph colors)."""
    accents = []
    p = norm_hex(pal.get("primary"))
    if p:
        accents.append(p)
    for g in graphs:
        ng = norm_hex(g)
        if ng:
            accents.append(ng)
    distinct = []
    for a in accents:
        if a not in distinct:
            distinct.append(a)
    n = len(distinct)
    status = "warn" if n > 4 else "pass"
    return {
        "id": "palette:roles",
        "title": "Accent-role budget (<=4)",
        "status": status,
        "detail": f"{n} distinct accent roles (primary + graphs); limit 4"
        + ("" if n <= 4 else " — reduce accents for a calmer deck"),
    }


def check_headline_assertion(deck):
    """headline:assertion — titles are assertions, not topics (advisory)."""
    slides = deck.get("slides", []) or []
    flagged = []
    for idx, s in enumerate(slides, start=1):
        if not isinstance(s, dict):
            continue
        stype = (s.get("type") or "").lower()
        if stype in NON_ASSERTION_TYPES:
            continue
        title = (s.get("title") or "").strip()
        if not title:
            continue
        words = count_words(title)
        has_verb = any(detect_verb(w) for w in re.findall(r"[A-Za-zА-Яа-яЁё']+", title))
        if words <= 2 or not has_verb:
            flagged.append(f"slide {idx}: {title!r}")
    status = "warn" if flagged else "pass"
    detail = (
        f"{len(flagged)} topic-style title(s) (want assertion headline)"
        + (": " + "; ".join(flagged[:5]) if flagged else "")
    )
    return {
        "id": "headline:assertion",
        "title": "Assertion headlines (conclusion, not topic)",
        "status": status,
        "detail": detail,
    }


def check_density(deck):
    """density:words — words-per-slide budget."""
    strategy = deck.get("strategy", {}) or {}
    density = (strategy.get("density") or "standard").lower()
    limit = 120 if density == "text-heavy" else 60
    slides = deck.get("slides", []) or []
    over = []
    for idx, s in enumerate(slides, start=1):
        if not isinstance(s, dict):
            continue
        text = " ".join(
            [s.get("title") or "", s.get("body") or ""]
            + [str(b) for b in (s.get("bullets") or [])]
        )
        wc = count_words(text)
        if wc > limit:
            over.append(f"slide {idx}: {wc} words")
    status = "warn" if over else "pass"
    detail = (
        f"budget {limit} words/slide ({density}); "
        + (f"{len(over)} over budget: " + "; ".join(over[:5]) if over else "all within budget")
    )
    return {
        "id": "density:words",
        "title": "Words-per-slide budget",
        "status": status,
        "detail": detail,
    }


def check_mood(deck):
    """consistency:mood — single theme.mood across the deck."""
    theme = deck.get("theme", {}) or {}
    moods = []
    if theme.get("mood"):
        moods.append(theme["mood"])
    for s in deck.get("slides", []) or []:
        if isinstance(s, dict) and s.get("mood"):
            moods.append(s["mood"])
    distinct = []
    for m in moods:
        if m not in distinct:
            distinct.append(m)
    status = "fail" if len(distinct) > 1 else "pass"
    detail = (
        f"{len(distinct)} mood(s): {', '.join(distinct) if distinct else '(none set)'}"
        + ("" if len(distinct) <= 1 else " — deck must use a single mood")
    )
    return {
        "id": "consistency:mood",
        "title": "Single mood across deck",
        "status": status,
        "detail": detail,
    }


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Aesthetic-quality gate for a deck spec")
    ap.add_argument("deck", help="path to deck.json")
    ap.add_argument("--html", help="optional slides.html for raw-hex token scan")
    ap.add_argument("--out", help="write JSON report to file")
    args = ap.parse_args()

    if not os.path.isfile(args.deck):
        print(f"ERROR: deck file not found: {args.deck}")
        sys.exit(2)
    if args.html and not os.path.isfile(args.html):
        print(f"ERROR: HTML file not found: {args.html}")
        sys.exit(2)

    try:
        deck = load_deck(args.deck)
    except (OSError, ValueError) as e:
        print(f"ERROR: cannot read deck.json: {e}")
        sys.exit(2)

    theme, pal, graphs = get_palette(deck)

    checks = [
        check_contrast(theme, pal, graphs),
        check_tokens(deck, args.html),
        check_palette_roles(theme, pal, graphs),
        check_headline_assertion(deck),
        check_density(deck),
        check_mood(deck),
    ]

    passed = sum(1 for c in checks if c["status"] == "pass")
    warned = sum(1 for c in checks if c["status"] == "warn")
    failed = sum(1 for c in checks if c["status"] == "fail")

    report = {
        "tool": "presentation-maker/deck_audit",
        "deck": args.deck,
        "html": args.html,
        "checks": checks,
        "summary": {
            "total": len(checks),
            "passed": passed,
            "warned": warned,
            "failed": failed,
        },
    }

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    print(json.dumps(report, ensure_ascii=False, indent=2))

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
