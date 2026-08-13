---
name: deck-html
description: "Build autonomous HTML slides (16:9) from a presentation JSON spec produced by deck-outline: pick a theme + palette, then build_html.py copies templates/slides.html, injects the palette into :root CSS variables and replaces the layout blocks. Mandatory verification gate: verify_slides.py in real Chromium (Playwright) — overflow/text-clipping/layout/NAV checks, exit 0/1 — plus a visual pass and the product-designer review checklist. Triggers: 'сделай слайды', 'слайды html', 'презентация html', 'html slides', '16:9 слайды', 'собрать слайды', 'build slides', 'сверстать презентацию'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.0.0"
compatibility: "Requires python3; verify_slides.py requires Playwright + Chromium"
---

# Deck HTML — slides.html from a JSON spec

Use this skill to **build self-contained HTML slides (16:9)** from the JSON spec
that `deck-outline` produces. Autonomous output: all CSS inlined, zero external
links, opens in any browser, arrow/keyboard/touch navigation.

## When to use

- User asks for "слайды", "html slides", "16:9", "сверстать презентацию".
- The outline/spec exists and a browser-deliverable is needed.

## Do NOT use

- To build slide STRUCTURE — that is `deck-outline`.
- To build the .pptx — that is `deck-pptx`.

## Step 3 — Theme and palette

Themes (each = a layout set + type system). Pick one; `general`/`modern` when
unspecified:

| Theme | Character |
|---|---|
| `general` | minimal, clean, airy |
| `modern` | flat cards, large radii |
| `executive` | strict, business, dark |
| `momentum` | dynamic, accented |
| `swift` | Apple-style, airy, teal |
| `standard` | basic, universal |

Extract the palette (`ThemeData` keys) and write it into the spec so html and
pptx use the SAME palette:

```
primary / background / card / stroke /
background_text / primary_text /
graph_0..graph_4  (up to 5 series)
```

Light theme recommendation: `background: #FFFFFF`, `primary: #007AFF` (or the
theme's accent), dark text `primary_text: #1C1C1E`. Dark theme: `background: #1C1C1E`,
light text.

## Build

```bash
python3 scripts/build_html.py deck.json slides.html
```

The builder copies `templates/slides.html`, replaces the slides with the real
content, fills the `:root` CSS variables with the chosen palette, and removes
unused layout blocks. Each slide is `<section class="slide" data-type="...">`
inside `.deck`. All layouts (`title`, `divider`, `bullets`, `metrics`,
`comparison`, `table`, `chart`, `process`, `closing`) and navigation already
exist in the template.

Icons: `templates/icons/*.svg`, referenced in the spec by name (no extension);
the builder inlines the SVG.

## Verification — mandatory gate before delivery

A deck is NOT done until it passes verification.

1. **Automatic** — `verify_slides.py` in real Chromium (from the project venv
   with Playwright):
   ```bash
   .venv/bin/python scripts/verify_slides.py slides.html --spec deck.json
   ```
   Checks per slide: non-empty title/content, no horizontal overflow of the
   slide, text does not escape card boundaries (metric/step/col/tl/kpi/bullet/
   table-row/badge), no clipped text (`scrollWidth > clientWidth`), navigation
   arrows switch slides, slide count matches the spec.
   **Exit 0 = PASS, 1 = FAIL.** Delivering a FAIL deck is forbidden.
   If Playwright is missing: `.venv/bin/pip install playwright && .venv/bin/playwright install chromium`.

2. **Visual pass** — open `slides.html` and eyeball: air and padding (nothing
   glued to slide edges), large type for metrics/numbers, minimal text per slide,
   one palette across cards/accents/progress, long words wrap instead of
   overflowing, adjacent slides use different layouts.

3. **Product-design review** — run the checklist in `references/product-designer.md`
   as a reviewer; fix and rebuild on any failure, then repeat steps 1–2.

## Handoff

- From `deck-outline` → the JSON spec (shared with `deck-pptx`).
- Design system reference: `references/design-system.md`.
