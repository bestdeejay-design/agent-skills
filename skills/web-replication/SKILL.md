---
name: web-replication
description: >
  Frontend visual replication skill. Explores a target website's publicly visible pages
  via Playwright MCP, captures screenshots and layout information, then generates a
  static or client-side frontend replica that approximates the original's visual
  appearance and page structure. Replicates FRONTEND PRESENTATION ONLY — no backend,
  databases, or non-public content.

  ⚠️ Authorization gate: Before starting, the agent MUST confirm with the user that
  they have the legal right to replicate the target site.

  Triggers: 'web replication', 'реплика сайта', 'скопируй сайт', 'replicate website',
  'clone website', 'визуальная копия', 'сделай как этот сайт', 'copy this site design'.
license: MIT
metadata:
  author: best
  version: 1.0.0
  adapted_from: zai-org/GLM-skills/glmv-web-replication
when_to_use: "Replicate a website's frontend visual design. Triggers: 'web replication', 'реплика сайта', 'скопируй сайт', 'replicate website', 'clone this site'."
---

# Website Frontend Visual Replication

**Origin**: Adapted from `zai-org/GLM-skills/glmv-web-replication` (Apache 2.0).
Agent-browser replaced with Playwright MCP (built into OpenCode).

## Prerequisites

This workflow uses **Playwright MCP** (built into OpenCode via `playwright_browser_*` tools).
No external dependencies needed.

## Authorization Gate (MUST execute first)

Before proceeding, **MUST** ask the user:

> "Do you own this website, or do you have explicit written permission from the owner to replicate it? Unauthorized replication may violate copyright, terms of service, or applicable law."

- If confirmed → proceed
- If cannot confirm → **STOP**. Suggest building an original design instead.

## Scope & Limitations

| Included | NOT Included |
|----------|-------------|
| Page layout & visual styling | Backend / server-side logic |
| Navigation structure | Databases & data stores |
| Publicly visible text & images | Authentication systems |
| CSS/design tokens | API business logic |
| Client-side interaction patterns | Non-public content |
| Static asset files (images, fonts) | Credentials, secrets |

**Data handling rules:**
1. Never scrape behind a login wall
2. Never collect credentials, API keys, or PII
3. Never reproduce copyrighted content verbatim unless user holds rights
4. Respect robots.txt and rate limits

## Core Idea

1. Recursively explore every **public** page, record visual content, interactions, and assets
   into a structured "blueprint" with nested folders representing navigation relationships.
2. Build a **frontend visual replica** based on that blueprint.
3. Visually compare and revise.

## Blueprint Structure

```text
blueprint/
├── _meta.md                      # Site metadata
├── _sitemap.md                   # Sitemap
├── _assets/                      # Global assets (fonts, favicon)
├── _navigation_graph.md          # Navigation graph (Mermaid)
├── home/                         # Homepage
│   ├── _page.md                  # Page blueprint
│   ├── _full.png                 # Full-page screenshot
│   ├── _scroll_00.png ~ N.png    # Scroll sequence
│   ├── _interactions.md          # Interaction records
│   ├── _interactions/            # Interaction state screenshots
│   ├── _assets/                  # Page-specific assets
│   ├── products/                 # Child pages (reachable from here)
│   │   ├── _page.md
│   │   ├── _full.png
│   │   └── ...
│   └── about/
│       └── ...
```

## Replication Workflow

### Step 1: Initialize

```bash
mkdir -p blueprint/_assets
```

Open the target site with Playwright:
```
playwright_browser_navigate url="<target URL>"
playwright_browser_resize width=1920 height=1080
playwright_browser_wait_for time=3
```

Write `blueprint/_meta.md`:
```markdown
# Website Replication Blueprint
- Target website: <URL>
- Exploration date: <date>
- Viewport size: 1920×1080
```

### Step 2: Recursively collect pages

For every page, execute this procedure:

#### 2.1: Capture and analyze

```
playwright_browser_take_screenshot fullPage=true filename="blueprint/<page>/_full.png"
playwright_browser_snapshot    ← get interactive elements
```

#### 2.2: Download assets

Collect all image/video/font URLs from the page snapshot, download with curl:
```bash
curl -o blueprint/<page>/_assets/image.jpg "<image_url>"
```

#### 2.3: Traverse interactions

For each interactive element found in the snapshot:

```
# Hover
playwright_browser_hover target="<element>"
playwright_browser_take_screenshot filename="blueprint/<page>/_interactions/hover.png"

# Click (may trigger navigation)
playwright_browser_click target="<element>"
playwright_browser_wait_for time=2
playwright_browser_take_screenshot filename="blueprint/<page>/_interactions/click.png"

# If navigation happened, capture the new page as a child
playwright_browser_snapshot   ← check if URL changed

# Go back
playwright_browser_navigate_back
```

#### 2.4: Scroll and repeat

```
playwright_browser_press_key key="PageDown"
playwright_browser_wait_for time=1
playwright_browser_take_screenshot filename="blueprint/<page>/_scroll_N.png"
```

Continue until bottom of page.

#### 2.5: Document the page

Write `blueprint/<page>/_page.md`:
```markdown
# <Page Name>
- URL: <path>
- Source: <how we got here>

## Section Structure
| No. | Section Name | Layout Pattern | Content Type |
|------|--------------|----------------|--------------|
| 1 | ... | ... | ... |

## Screenshots
- Full: !_full.png
- Scrolls: !_scroll_00.png ... !_scroll_N.png

## Outbound Navigation
| Trigger | Method | Target | Child Folder |
|---------|--------|--------|--------------|
| ... | click | /path | ./child/ |

## Assets
| File | Purpose |
|------|---------|
| _assets/img.jpg | ... |
```

Write `blueprint/<page>/_interactions.md`:
```markdown
# Interactions

| Element | Trigger | Behavior | Navigation | Screenshot |
|---------|---------|----------|------------|------------|
| ... | click | ... | Yes → ./child/ | ![](_interactions/click.png) |
```

### Step 3: Generate summaries

After all pages collected:

#### `blueprint/_sitemap.md`
```markdown
# Sitemap
home/                          # /
├── products/                  # /products
│   ├── product-detail/        # /products/:id
│   └── category/              # /products/category/:slug
├── about/                     # /about
└── blog/                      # /blog
    └── blog-post/             # /blog/:slug
```

#### `blueprint/_navigation_graph.md`
```markdown
# Navigation Graph
graph LR
    Home["home /"] -->|Nav - Products| Products["products /products"]
    Home -->|Nav - About| About["about /about"]
    Products -->|Card click| Detail["product-detail /products/:id"]
```

### Step 4: Frontend Visual Replication

Based on the blueprint, build a frontend replica:
- Match layout, colors, typography, spacing from screenshots
- Implement navigation between pages
- Use downloaded assets
- Match interaction patterns (hover states, filters, etc.)

Recommended stack: HTML + CSS + vanilla JS, or React/Tailwind if complex.

### Step 5: Visual Comparison & Revision

1. Start the replica locally
2. Open both original and replica side by side (two browser tabs)
3. Compare page by page: layout, colors, typography, navigation
4. Fix discrepancies
5. Repeat until satisfied

## Key Rules

1. **Authorization first** — never start without user confirmation
2. **Public pages only** — no login-protected areas
3. **No credential handling** — redact any found credentials
4. **Frontend only** — no backend replication
5. **Folders = navigation** — if page A links to page B, B is a subfolder of A
6. **Every folder needs**: `_page.md`, `_full.png`, `_interactions.md`, `_interactions/`, `_assets/`
7. **Screenshots from real site** — never describe from memory
8. **Interactions genuinely triggered** — hover, click, focus, one by one
9. **Download assets** — curl for images, Playwright eval for SVGs
10. **Record only** — document results without quality judgments
11. **Keep files updated** — real-time updates after each page exploration
12. **Visible elements** — scroll into view before interacting
13. **One action per Playwright call** — no combining multiple commands
14. **External links** — record URL + trigger element, don't deep-explore
15. **Both full and scroll screenshots** — overall + detail reference
