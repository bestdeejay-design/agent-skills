---
name: presentation-maker
description: End-to-end presentations from a topic — outline -> JSON spec -> 16:9 HTML slides (with mandatory Playwright verification) and real .pptx (full 14-type design system), plus strategy presets, PDF export, and deck-quality audits. One command per stage.
license: MIT
metadata:
  version: 3.5.0
---

# presentation-maker

Build a complete, on-brand presentation from a single topic or outline file. The
skill is a **pipeline of small, single-purpose scripts** — one command per stage —
so each step is inspectable, debuggable, and composable.

> Russian triggers: `сделай презентацию`, `презентация`, `слайды`, `pptx`,
> `сделай доклад`, `собери слайды`, `структура слайдов`, `аутлайн презентации`,
> `16:9 слайды`, `презентация в powerpoint`.

## Pipeline

```
topic / outline.md
      │  strategy.py            (pick narrative arc + mood + density + layouts)
      ▼
   deck.md  ──(deck_md.py)──▶  deck.json   (normalized spec)
      │                          │
      │                          ├──(build_html.py)──▶ slides.html
      │                          │                        └──(verify_slides.py)──▶ PASS/FAIL  [mandatory Playwright gate]
      │                          ├──(build_pptx.py)──▶ deck.pptx
      │                          │                        └──(qa_pptx.py)──▶ PASS/FAIL  [geometric PPTX gate]
      │                          ├──(build_pdf.py)──▶  deck.pdf   (from slides.html, Playwright)
      │                          └──(deck_audit.py)──▶  quality report (JSON)
```

Every stage reads/writes the same `deck.json` contract, so you can regenerate any
artifact after editing the spec.

## Stage commands

All commands run from the repo root. Scripts live in `scripts/`.

### 1. Strategy (optional but recommended)

```bash
python3 skills/presentation-maker/scripts/strategy.py --goal keynote
python3 skills/presentation-maker/scripts/strategy.py --audience "SaaS investors" --topic "Series A"
python3 skills/presentation-maker/scripts/strategy.py --list          # all presets
python3 skills/presentation-maker/scripts/strategy.py --show pitch    # one preset
```

Flags: `--goal` (`pitch|consulting|keynote|report|edu`), `--audience`, `--topic`,
`--language` (`ru|en`), `--list`, `--show <goal>`. If `goal` is omitted it is
inferred from `audience`/`topic` keywords, else defaults to `pitch`. The chosen
strategy (arc / mood / density / palette_name / layouts) is auto-applied by
`deck_md.py` when the matching frontmatter fields are absent.

### 2. Outline → spec

```bash
python3 skills/presentation-maker/scripts/deck_md.py outline.md -o deck.json
# overrides (take precedence over frontmatter):
python3 skills/presentation-maker/scripts/deck_md.py outline.md -o deck.json \
    --goal keynote --audience "investors" --lang ru --palette swift --tone confident
```

Flags: positional `md` (topic or outline file), `--out` (default `deck.json`),
`--goal`, `--audience`, `--tone`, `--palette` (theme name or mood), `--lang`/`--language`.
The outline format is documented in `references/strategy.md`; in short: a leading
YAML-ish frontmatter (`title`, `goal`, `audience`, `language`, `theme`, `density`,
`topic`) followed by slide blocks separated by a line containing only `---`, each
starting with `# Headline`.

### 3. HTML slides (16:9)

```bash
python3 skills/presentation-maker/scripts/build_html.py deck.json slides.html
```

Takes `templates/slides.html`, injects the palette into `:root` CSS variables, and
replaces the demo `<section class="slide">` blocks with real ones built from the
spec. Output is a self-contained 16:9 deck.

### 4. Verification gate (MANDATORY)

```bash
python3 skills/presentation-maker/scripts/verify_slides.py slides.html --spec deck.json
```

Runs in real Chromium (Playwright) and checks, per slide: a heading + non-empty
content, no horizontal overflow, cards/rows hold their content (no clipping or
spill), text containers do not clip, and keyboard navigation switches slides.
**Exit 0 = pass; exit 1 = fail.** Do not ship `slides.html` without a PASS.

### 5. PowerPoint

```bash
python3 skills/presentation-maker/scripts/build_pptx.py deck.json deck.pptx
```

Draws a real `.pptx` via `python-pptx` on a 1600×900 design canvas (13.333×7.5",
16:9, `PX=7620` EMU/px): all 14 slide types rendered through the shared
**PPTX design system** — eyebrow, ghost page numbers, chrome (logo + page
indicator), decor ovals, tinted "sandwich" bookends, shadowed cards, numbered
step ovals, square bullet markers, oversized metrics/quote/hero numbers.
Fonts are **Arial** (never Inter — LibreOffice substitutes matter for QA).
See "PPTX design system" below for the full element set and contracts.

```bash
# geometric QA gate — run after every build (exit 0 = pass):
python3 skills/presentation-maker/scripts/qa_pptx.py deck.pptx --render
```

Checks per slide: shapes inside canvas, content above `BOTTOM_STOP`, no
text-overlap, tables fit; `--render` additionally exports JPEGs via
LibreOffice → `pdftoppm` for human/vision review. Design elements named
`ghost*`, `decor*`, `chrome-*` are exempt from bounds/content checks.

### 5b. Extern linter gate — `intern` (optional but recommended)

[`intern`](https://github.com/markusz/intern) (MIT) is an open-source CLI
linter for `.pptx`: alignment (`CLOSE_X/CLOSE_Y`), text quality
(`DOUBLE_SPACE`, `EMPTY_TEXTBOX`, `REPEATED_WORD`), margins, font/color
variety. It catches issues our geometric gate does not model — it already
found a real bug (triple spaces around `·` in the footer).

Install once (any of):

```bash
brew install markusz/intern/intern        # macOS
# or prebuilt binary: curl -L https://github.com/markusz/intern/releases/latest/download/intern-$(uname -m|sed s/x86_64/x86_64-apple-darwin/|sed s/arm64/aarch64-apple-darwin/).tar.gz | tar xz
```

Run through our wrapper (it whitelists design-system elements by shape name —
`ghost*`, `decor*`, `chrome-*`, `quote-*`, `process-card`, `step-num`,
`toc-*` — and can drop token rules for token-driven decks):

```bash
python3 skills/presentation-maker/scripts/qa_intern.py deck.pptx --skip-token-rules
# exit 0 = clean after design-filter; 1 = real violations; 2 = intern missing/error
```

`--skip-token-rules` ignores `FONT_SIZE_VARIETY`/`COLOR_VARIETY` — our design
system intentionally uses a token hierarchy (eyebrow 11pt … metrics 64pt,
quote mark 120pt). For non-token decks omit it to keep those checks.

### 6. PDF export

```bash
python3 skills/presentation-maker/scripts/build_pdf.py slides.html deck.pdf
# optional: python3 skills/presentation-maker/scripts/build_pdf.py slides.html deck.pdf --viewport 1600x900
```

Renders the **same themed `slides.html`** into a multi-page 16:9 PDF (one slide per
page) using Playwright — no separate layout/theme is re-implemented, so the PDF is
visually 1:1 with the HTML. See `references/pdf.md`.

### 7. Quality audit

```bash
python3 skills/presentation-maker/scripts/deck_audit.py deck.json --html slides.html
```

Deterministic, browser-free aesthetic gate (exit 0/1). Checks WCAG contrast,
no raw hex outside `:root`, ≤4 accent roles, assertion headlines, words-per-slide
budget, and a single mood across the deck. See `references/audit.md`.

## JSON spec schema (`deck.json`)

```jsonc
{
  "title": "Deck title",
  "goal": "keynote",                 // pitch|consulting|keynote|report|edu
  "topic": "optional topic",
  "audience": "optional audience",
  "language": "ru",                  // ru|en
  "tone": "optional voice note",
  "theme": {
    "name": "swift",                // theme file name (see templates/themes/)
    "mood": "glass",                // swiss|editorial|flat|glass|dark
    "palette": {                    // injected into :root CSS variables
      "primary": "#007AFF",
      "background": "#FFFFFF",
      "card": "#F5F5F7",
      "stroke": "#E5E5EA",
      "background_text": "#FFFFFF",  // text on primary
      "primary_text": "#1C1C1E",
      "muted": "#6E6E73",
      "accent_soft": "#E8F0FE",
      "graph_0": "#007AFF",          // up to graph_4
      "font": "Inter",
      "font_display": "Inter",
      "font_url": "https://...",     // optional web font
      "mood": "glass",
      "radius": "18px",
      "radius_sm": "10px",
      "eyebrow_track": "uppercase"
    }
  },
  "strategy": {
    "arc": "sparkline",
    "density": "concise",            // concise|standard|text-heavy
    "layouts": ["big_number", "quote", "divider"]
  },
  "slides": [ /* slide objects, see below */ ]
}
```

### Slide object (content)

Each slide has a `type` (or `auto`/omitted → inferred from content) plus type-specific
fields. Common types and their key fields:

| type | key fields |
|---|---|
| `title` / `closing` | `title`, `subtitle?`, `presenter?`, `date?` |
| `divider` | `title`, `subtitle?` |
| `bullets` | `title`, `bullets[]` |
| `comparison` | `title`, `columns[]` → `{heading, points[]}` |
| `table` | `title`, `table` → `{headers[], rows[][], highlight_col?}` |
| `chart` | `title`, `chart` → `{categories[], series[]→{name,values[]}, note?}` |
| `process` | `title`, `steps[]` |
| `metrics` | `title`, `metrics[]` → `{value, label, icon?}` |
| `big_number` | `title?`, `value`, `label?`, `subtitle?`, `accent?` |
| `quote` | `title?`, `quote`, `attribution?` |
| `feature` | `title`, `features[]` → `{title, text?, icon?}` |
| `image_showcase` | `title`, `image`, `desc?`, `points?` |
| `timeline` | `title`, `items[]` → `{title, desc?}` |
| `kpi_row` | `title`, `kpis[]` / `metrics[]` |
| `logos` | `title`, `logos[]`, `note?` |
| `table_of_contents` | `title`, `items[]` → `{title, desc?}` |
| `centered_header` | `title`, `subtitle?`, `panel?` |

Valid `type` values: `title, divider, bullets, comparison, table, chart, process,
metrics, feature, big_number, quote, table_of_contents, timeline, image_showcase,
centered_header, kpi_row, logos, closing`.

## Theme + palette model

Themes are JSON files in `templates/themes/` (names: `general, modern, executive,
momentum, swift, standard, dynamic`). Each provides a `palette` (the `:root` CSS
variables above) and a `mood`. A `mood` is one of `swiss | editorial | flat | glass
| dark` and drives the aesthetic regime; `DEFAULT_THEMES` maps each mood to the
nearest theme file (`swiss→executive`, `editorial→standard`, `flat→modern`,
`glass→swift`, `dark→dynamic`). Icons for `metrics`/`feature` slides live in
`templates/icons/` as inline SVG (no emoji).

## Layout families

`build_html.py` and `build_pptx.py` share a `RENDERERS` map keyed by slide `type`.
When `type` is `auto`/missing, `pick_layout()` infers the best fit from content
keys (quote → `quote`, columns → `comparison`, steps → `process`, metrics →
`metrics`, numeric table → `chart`, text table → `table`, features → `feature`,
logos → `logos`, etc.), avoiding repeating the previous slide's type when plausible.

## Generative pattern layer (v3.3.0)

Beyond the fixed `RENDERERS`, each slide gets a **layout pattern** — a
compositional scheme chosen at build time so decks do not look like one template:

- **Patterns** live in `templates/patterns/*.json`. Compositional schemes
  (15): `hero-left`, `editorial-asym`, `swiss-grid`, `z-pattern`, `split-diagonal`,
  `big-type`, `card-dashboard`, `vertical-rail`, `split-frame` (photo/media half),
  `sparkline-metric` (giant number + trend), `before-after` (muted vs accent halves),
  `vertical-stepper` (track + step dots), `zigzag-timeline` (alternating rows),
  `quote-hero` (giant quote mark), `recap-grid` (2×2 summary, one accent cell).
  Each declares `family` (editorial/swiss/fintech/minimal/glass), which content
  types it `fits`, CSS tokens for HTML, and coordinate rules for PPTX.
- **Selector** (`scripts/patterns.py`, shared by both builders): content type →
  matching patterns (`fits`) → variety (never repeat a pattern used on the last 3
  slides) → deck `style.family` narrows candidates → density filter → least-used
  tie-break. Result is a unique mix per deck: the same content can be rendered by
  different patterns on different decks.
- **Style direction** — set in the outline frontmatter to steer the whole deck:

  ```yaml
  style:
    family: fintech        # editorial | swiss | fintech | minimal | glass
    reference: https://…   # optional: case/gallery reference
  ```

  Without `style.family` the selector still varies patterns (variety rule alone),
  so decks differ even with the same theme.
- **Skill memory** — after building, save a deck as a reusable case:

  ```bash
  python3 scripts/build_html.py deck.json slides.html --save-case my-deck
  ```

  This writes `examples/cases/my-deck/{case.json, deck.json, slides.html}`.
  `scripts/cases.py` lists saved cases; future users can reuse a case as a
  reference or extend the pattern library from it — every deck can become a
  template for the next one. `verify_slides.py`, `deck_audit.py`, `qa_pptx.py`
  and `qa_intern.py` gates run unchanged.

## Accent embedding (two brand colors, no mixing)

Decks may carry **two brand accents** (e.g. teal primary + rose accent). They are
never blended in one element, and text on an accent-colored block is always
`on-primary` (white). The accent is woven into individual slides via modes
(`build_html.py` → `pick_accent_mode()`, spread across the deck, never repeated
on adjacent slides):

- **`accent-word`** — first word of the title entirely in the accent color
  (never a lone letter floating away from its word);
- **`accent-underline`** — accent hairline under the title;
- **`accent-icons`** — metric icons + values in the accent color (light cards only).

Set the two accents in the theme: `primary` (structure: headings, lines,
markers, gradients, duotones) and `accent` (accent points only). Graphs stay in
the primary family so gradients/duotones never mix the two brands.

## Typography floor (card text)

Body text inside cards must stay readable at 16:9 projection — floor 17px,
labels ≥ 17px, metric values 30–48px, timeline descriptions ≥ 15px. Headings
scale via `--t-*` tokens. `verify_slides.py` re-checks overflow after any
font-size change.

## Anti-template design rules

Summarized from `references/design-system.md` (full rules there). Enforced
mechanically by `deck_audit.py`:

- **≤ 2 typefaces**, **≤ 4 accent roles** (primary + graph colors); keep 60-30-10.
- **One idea per slide**; content < 60% of slide area; generous whitespace.
- **Assertion headlines** — full sentences with a verb (a conclusion, not a topic).
- **WCAG contrast** ≥ 4.5:1 for text, ≥ 3:1 for large/non-text (graph lines, borders).
- **Zero raw hex outside `:root`** — every color is a CSS token.
- **One `mood` per deck**; one radius/stroke language; no emoji icons (SVG only).
- **Words-per-slide budget**: 60 (standard) / 120 (text-heavy); concise ≈ 20.

## PPTX design system (build_pptx.py)

`build_pptx.py` renders every slide on a **1600×900 design canvas**
(13.333×7.5", `PX = 7620` EMU/px). Fixed contracts:

| Constant | Value | Meaning |
|---|---|---|
| `MARGIN_X` | 96 px | horizontal page margin |
| `TITLE_Y` / `TITLE_H` | 56 / 96 px | title band (autofits ≤ 2 lines) |
| `CONTENT_Y` | 180 px | all content starts below the title band |
| `BOTTOM_STOP` | 80 px | nothing may end lower than `H - 80` |
| Font | **Arial** everywhere | LibreOffice-safe; never Inter in PPTX |

### Full element set

| # | Element | Where | Spec |
|---|---|---|---|
| 1 | **eyebrow** | title, divider, toc, quote, closing, content | 12 pt bold, tracking 3.6, `accent_soft` on dark / `primary` on light; y≈88 |
| 2 | **ghost-num** | every slide | huge translucent page number; name `ghost-num` — **exempt from QA bounds** |
| 3 | **chrome** | every slide | logo 30×30 (`chrome-logo`) + `NN / NN` page indicator (`chrome-page`) — exempt |
| 4 | **decor-ovals** | title, divider, closing | translucent ovals (alpha 15–22%) in `graph_1`; name `decor` — exempt |
| 5 | **tinted sandwich** | title / divider / closing | dark `primary` background, light text; content slides use `background` |
| 6 | **cards** | bullets, comparison, metrics, process, timeline, feature, toc | rounded rect + shadow (blur 10 / dist 3 / alpha 9%), stroke `p.stroke` |
| 7 | **step-num / toc-num** | process, timeline, toc | numbered OVAL 36–44 px, `NN`/`01` labels |
| 8 | **square bullet markers** | bullets (`style="cards"`) | `bullet-marker` squares in accent color |
| 9 | **hairline** | comparison | 2 px divider line under column heading |
| 10 | **metric value** | metrics | 64 pt bold (min 30), color cycles `graph_0..7` |
| 11 | **hero number** | big_number | 110 pt bold (min 40) + 30 pt label + 18 pt subtitle |
| 12 | **opening quote** | quote | 120 pt bold `"` (min 80), quote 34 pt, attribution 20 pt muted |
| 13 | **arrow →** | process | 22 pt `→` between step cards |

### Rules

- **eyebrow is mandatory** on title / divider / closing; optional elsewhere.
- ghost/decor/chrome are decorative: `qa_pptx.py` skips names starting
  `ghost*`, `decor*`, `chrome-*` for bounds/content checks, but they must stay
  visually inside the canvas — verify on `--render` JPEGs.
- All 14 types share the same palette tokens and the same visual language
  (cards, ovals, eyebrow) — a deck must read as one system, not 14 templates.
- The same `deck.json` drives HTML and PPTX: keep both builds green
  (`verify_slides.py` + `qa_pptx.py`) before shipping.

## Dependencies

- `python3` (stdlib only for `deck_md.py`, `strategy.py`, `deck_audit.py`).
- `python-pptx` for `build_pptx.py`: `pip install python-pptx`.
- `playwright` for `verify_slides.py` and `build_pdf.py`:
  `pip install playwright && playwright install chromium`.

## References

- `references/strategy.md` — goal → arc/mood/density/layouts table + usage.
- `references/design-system.md` — full anti-template design system (5.x moods, tokens).
- `references/product-designer.md` — narrative arcs and product-design module.
- `references/pdf.md` — PDF export mechanics.
- `references/audit.md` — deck_audit check contract and fixes.
