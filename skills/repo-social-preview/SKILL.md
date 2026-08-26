---
name: repo-social-preview
description: "Build the repository social preview (og:image) as a hand-crafted hero-section HTML (1280x640, 40pt crop-safe padding, no self-made SVG), rendered to PNG via headless Chrome. Source of truth: the project website's hero section when one exists - re-typeset it clean, never screenshot it. Triggers: 'social preview', 'og image', 'og:image', 'social share image', 'repo preview png', 'open graph image', 'github social preview'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "2.0.0"
  compatibility: "Requires headless Chrome/Chromium for rendering; python3"
when_to_use: "Use when building the GitHub social preview / og:image: 'social preview', 'og image', 'og:image', 'social share image', 'repo preview png', 'open graph image', 'github social preview'. Example: 'make a social preview PNG for my repo' or 'generate og:image'."
---

# Repo Social Preview — og:image as a typeset hero section

The social preview is **a piece of web design, not a generated raster**. Lay out a
clean hero section in HTML/CSS, render it with headless Chrome, upload the PNG.

## Hard rules

1. **Typeset HTML — never compose pixels.** No Pillow drawing, no self-made SVG
   shapes, no site screenshots. The deliverable is a standalone `hero.html`.
   Existing assets from the site (logo URL, brand fonts) may be referenced; do not
   draw new ones.
2. **Hero only.** No header, nav, footer, badges, cookie bars. One full-bleed
   1280×640 hero section: headline, optional subline/CTA, brand background.
3. **40pt padding on all sides** (`padding: 40pt`). This is the GitHub crop-safe
   hint: essential text and logos must stay inside it — share previews crop edges.
4. **Site is the source of truth.** If the repo has a website with a hero section,
   re-typeset *that* hero: its headline, subline, palette, typeface. Do not invent
   a different design; do not embed an iframe or screenshot of it.
5. **Front-end quality bar.** Build the markup per the `frontend` skill: real
   typography scale, brand tokens as CSS variables, no layout hacks.

## Workflow

1. **Collect source material**
   - Website exists → fetch it, extract the hero: headline, subline, CTA text,
     colors, fonts, logo URL.
   - No website → build from README/description: repo name + one-line value prop.
2. **Lay out `hero.html`** (standalone file, fixed 1280×640 viewport):
   ```html
   <!doctype html>
   <html><head><meta charset="utf-8">
   <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800">
   <style>
     :root { --brand-a:#F64A8A; --brand-b:#0ABAB5; --ink:#1A1A1A; }
     * { margin:0 }
     body { width:1280px; height:640px; overflow:hidden }
     .hero { width:100%; height:100%; box-sizing:border-box; padding:40pt;
             display:flex; flex-direction:column; justify-content:center; gap:16pt;
             background:linear-gradient(90deg, var(--brand-a) 50%, var(--brand-b) 50%); }
   </style></head>
   <body><section class="hero">…</section></body></html>
   ```
   Solid background preferred over transparency; hard color stops are fine,
   keep text contrast ≥ WCAG AA.
3. **Render to PNG**:
   ```bash
   python3 scripts/render_social_preview.py hero.html --out og.png
   ```
   Headless Chrome renders real web layout pixel-perfectly (webfonts included).
4. **Verify**: exactly **1280×640**, **< 1 MB**, nothing clipped at the edges,
   text readable at thumbnail size. Re-render if any check fails.
5. **Upload manually**: Settings → Social preview → Edit → Upload (no API).

## Requirements (GitHub)

- File in root / `docs/` / default branch; format PNG/JPG/GIF; **< 1 MB**;
  minimum **≥ 640×320**, recommended **1280×640**.
- Transparency is supported but a solid background is recommended.
- For GitHub Pages OG tags, see `references/social-preview.md`.

## Anti-patterns

- Drawing the preview with Pillow/composed SVG instead of typesetting HTML.
- Screenshotting the live site (header/footer/badges leak into the shot).
- Content touching the canvas edges (violates the 40pt crop-safe zone).
- Oversized file (> 1 MB) or too small (< 640×320).
- Overwriting an existing preview without explicit request.
