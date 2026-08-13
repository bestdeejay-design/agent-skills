---
name: deck-pptx
description: "Build a real PowerPoint (.pptx) from a presentation JSON spec produced by deck-outline: slide list with types/content + palette. Script build_pptx.py draws layouts via python-pptx — textboxes for titles/bullets, TrueTable tables, CategoryChartData charts, palette-colored backgrounds. Triggers: 'сделай pptx', 'pptx', 'powerpoint', 'презентация в powerpoint', 'собрать pptx', 'build pptx', 'конвертировать в pptx', 'отдать в pptx'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.0.0"
compatibility: "Requires python-pptx (venv)"
---

# Deck PPTX — PowerPoint builder from a JSON spec

Use this skill to **assemble a real `.pptx`** from the presentation JSON spec
that `deck-outline` produces. One focused job: spec → PowerPoint.

## When to use

- User asks for "pptx", "powerpoint", "сделай pptx", "собрать pptx", "отдать в pptx".
- The outline/spec exists and a PowerPoint deliverable is needed.

## Do NOT use

- To build slide STRUCTURE — that is `deck-outline`.
- To build `slides.html` — that is `deck-html`.

## Build

Input: the JSON spec (slide list with types/content + palette).

```bash
python3 scripts/build_pptx.py deck.json deck.pptx
```

What the script draws with python-pptx:
- textboxes for slide titles and bullets;
- `TrueTable` for table layouts;
- `CategoryChartData` charts for numeric data layouts;
- palette-colored backgrounds from the spec's palette.

## Dependencies

python-pptx lives in the project venv:

```bash
python3 -m venv .venv && .venv/bin/pip install python-pptx
.venv/bin/python scripts/build_pptx.py deck.json deck.pptx
```

## Handoff

- From `deck-outline` → the JSON spec.
- `deck-html` builds the browser version from the SAME spec, so html and pptx
  stay consistent (same palette, same content).
