---
name: deck-outline
description: "Build the slide outline and structure for a presentation from a topic or prompt: parameters (n_slides, language, tone, verbosity), content rules (one idea per slide, no bold/italic, no URLs, no emoji — SVG icons only), layout mapping (content -> title/table/chart/comparison/process/metrics...), auto-layout selection. Output: outline.md + a JSON spec consumed by deck-html and deck-pptx. Triggers: 'план презентации', 'структура слайдов', 'аутлайн презентации', 'раскадровка', 'сценарий презентации', 'outline slides', 'slide structure', 'deck outline', 'составь структуру доклада'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.0.0"
compatibility: "No scripts — pure authoring workflow"
---

# Deck Outline — slide structure from a topic

Use this skill when a presentation needs its **structure built first**: turn a
topic/prompt/content into a slide-by-slide outline with explicit layouts and a
palette note. The output is the single source of truth that `deck-html` (slides)
and `deck-pptx` (PowerPoint) both consume.

## When to use

- User asks for "план презентации", "структура слайдов", "раскадровка", "outline",
  "structure the deck".
- A presentation pipeline starts here: outline → slides → pptx.
- Content exists but slide-by-slide structure does not.

## Do NOT use

- To BUILD slides (`slides.html`) — that is `deck-html`.
- To BUILD the .pptx — that is `deck-pptx`.
- For one-off slide tweaks without a structure pass.

## Step 0 — Parameters (defaults win over content wishes)

| Parameter | Default | Range |
|---|---|---|
| `n_slides` | auto-detect | 1–20 |
| `language` | auto-detect | ru/en |
| `tone` | clear professional | varies |
| `verbosity` | standard | concise≈20 words · standard≈40 · text-heavy≈60 |
| `include_title_slide` | true | true/false |
| `include_table_of_contents` | false | true/false |

Explicit parameters are **authoritative**: if the topic asks for a different
language/count, the parameters win.

## Step 1 — Content rules (critical, from Presenton)

Each slide is Markdown **content** (what the audience actually sees), not a
prompt or a build command.

- Every slide: `## Title` + content (bullets / comparison / table / metrics).
- Volume: `~N words` per verbosity (20/40/60). Less is better.
- Markdown, but **no `**bold**` and no `__italic__`**.
- First slide (title): **only** title + speaker + date + overview.
- **No URLs**, links, quotes, footers, source lists.
- Data stays **consistent** across slides.
- One slide = one goal. An overloaded topic is split into several slides.
- Logical flow intro → conclusion; no filler, no repetition.
- If content says "slide 5: bar chart Q1 10, Q2 20" — write only the table
  `Quarter | Value`, **not** the words "create a bar chart".
- Keep hard facts, numbers, tables and code when present.

### Icons (critical)

- **No emoji as icons** on slides — neither in content nor in the spec.
- Icons come only from the SVG set in `deck-html/templates/icons/`
  (Lucide/Feather style: `stroke="currentColor"`, `stroke-width="2"`,
  viewBox `0 0 24 24`).
- In the spec/outline reference an icon **by name without extension**
  (`"icon": "graduation"`) — the builder inlines the SVG.
- Available: `graduation`, `users`, `presentation`, `building`, `chart`,
  `family`, `bot`, `zap`, `briefcase`, `award`, `arrow-right`.

### Outline format (`outline.md`)

```markdown
# <Title (plain text)>

## Slide 1 — Title
- Title: ...
- Speaker: ...
- Date: ...
- Overview: ...

## Slide 2 — Problem
- Bullet 1
- Bullet 2

## Slide 3 — Data
| Quarter | Value |
|---|---|
| Q1 | 10 |
| Q2 | 20 |
```

## Step 2 — Layout per slide (content → layout mapping)

Pick the **type** for every slide and record it:

| Content / goal | Layout |
|---|---|
| Overall goal / opening / closing | `title` |
| Table with **text** data | `table` |
| Table with **numeric** data | `chart` (n cols → n-1 charts) or `metrics` |
| Comparison/contrast of 2+ things | `comparison` |
| Process / workflow / steps | `process` |
| Concept / idea (not data) | `image` / `image+text` |
| Key metrics | `metrics` |
| TOC (only when content is a TOC) | `table_of_contents` |
| Chapter/divider opening | `divider` |
| Conclusion | `title` or `emphasis` |
| One-sentence takeaway | `quote` |
| Single hero number | `big_number` |
| Feature set (icon+title+desc) | `feature` |
| Partners/brands/clients list | `logos` |
| Plan/agenda at the start | `table_of_contents` |

### Auto-layout (`pick_layout` in deck-html)

The builder can pick layouts itself when the spec says `"type": "auto"` or omits
it. Priority:

1. Explicit `type` always wins.
2. `quote` → quote; `logos` → logos; `toc` → table_of_contents; `features` → feature; `steps` → process.
3. `items` with title/desc → timeline.
4. `columns` → comparison; `metrics` → metrics.
5. `value` (hero number) → big_number.
6. `table`: numeric columns (2+) → chart, text → table.
7. `bullets`: if the previous slide was also bullets and the bullets are
   metric-like (contain `:`, `%`, `млн`, `млрд`, `₽`) → kpi_row, else bullets.

**Selection rules (critical):** tabular content MUST pick `table`/`chart`;
text tables → `table` only (never chart); numeric tables → `chart`, not
`metrics`; image layouts only when content has an image; adjacent slides must
differ (except the title repeat). Variety is good, but meaning beats variety —
never distort content to fit a layout.

## Output

Write `outline.md` and a JSON spec (`deck.json`) with: slide list
(title, type, content blocks, optional icon) + chosen palette. Both `deck-html`
and `deck-pptx` read the same JSON so the deck is consistent everywhere.
