---
name: presentation-maker
description: "DEPRECATED meta-skill. Routes to the three focused deck skills that replaced it: deck-outline (slide structure from a topic -> JSON spec), deck-html (autonomous 16:9 slides.html + verification), deck-pptx (PowerPoint from the spec). Load one of the three directly instead. Triggers: 'сделай презентацию', 'presentation', 'слайды', 'pptx', 'сделай доклад'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "2.0.0"
compatibility: "Router only — delegates to deck-outline / deck-html / deck-pptx"
---

# Presentation Maker — DEPRECATED (router)

> **This skill is deprecated.** It was split into three focused skills. Do **not**
> run the old pipeline from this file — load the matching sub-skill directly.

## Routing table

| Need | Load this skill instead |
|---|---|
| Slide structure, outline, layouts, JSON spec from a topic | `deck-outline` |
| Build autonomous HTML slides (16:9) + verification gate | `deck-html` |
| Build the .pptx from the spec | `deck-pptx` |

The old assets moved into the three new skills:

- outline/layout/content rules + `product-designer.md` → `deck-outline`
- `build_html.py`, `verify_slides.py`, `templates/slides.html`, icons, themes,
  `design-system.md`, `product-designer.md` → `deck-html`
- `build_pptx.py` → `deck-pptx`

## Removal plan

Keep this router for one release cycle for backward compatibility, then delete.
