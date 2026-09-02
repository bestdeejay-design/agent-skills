---
name: prd-to-app
description: >
  Build a complete, production-ready full-stack web application from PRD documents,
  prototype images, and resource files. Handles the entire pipeline: system design,
  database schema, seed data, backend API, frontend UI, visual verification against
  prototypes, and deployment script generation.

  Use this skill whenever the user:
  - Provides a PRD (product requirement document) and wants a working app built
  - Says "build from PRD", "implement this product", "develop this app from requirements"
  - Has prototype images + requirements and wants full-stack implementation
  - Wants to turn product specifications into a running web application

  Triggers: 'prd to app', 'из prd в приложение', 'разработай по prd',
  'сделай приложение по макетам', 'build from prd', 'implement from prd'.
license: MIT
metadata:
  author: best
  version: 1.0.0
  adapted_from: zai-org/GLM-skills/glmv-prd-to-app
when_to_use: "Build a complete web app from PRD + prototype images. Triggers: 'prd to app', 'build from PRD', 'implement this product', 'сделай приложение по макетам', 'разработай по prd'."
---

# PRD-to-App: Full-Stack Application Builder

> **Language**: Respond in the same language the user uses. Code comments should match.

Build a complete, deployed web application from PRD + prototypes + resources.
The result must be fully reproducible via a single `bash start.sh`.

**Origin**: Adapted from `zai-org/GLM-skills/glmv-prd-to-app` (Apache 2.0).
ZHIPU API dependencies removed; replaced with Playwright + look_at for prototype analysis.

---

## Phase 0: Material Discovery & Analysis

Before anything else, understand what you're working with.

### 0a. Locate all inputs

```
./prd.md                    ← Product requirement document
./prototypes/*.jpg|*.png    ← UI prototype images (the visual truth)
./resources/**/*            ← Images, videos, icons, and other assets
```

If the materials are in a different location, adapt accordingly. Read the PRD fully.

### 0b. Deep prototype analysis

For **every** prototype image:

1. **Read the image** using the `look_at` tool (or `Read` tool for images) — examine it directly.
   Extract: page identity, layout structure, component inventory, content inventory,
   color extraction (hex values), typography, interactive states, data patterns.

2. For each image, document:
   - **Page identity**: which page/view this represents
   - **Layout structure**: header, sidebar, main content, footer, modals
   - **Component inventory**: every button, form, card, table, list, nav element
   - **Content inventory**: all visible text, numbers, labels, placeholder content
   - **Color extraction**: primary, secondary, accent, background, text colors (hex values)
   - **Typography**: font sizes, weights, hierarchy observed
   - **Interactive states**: hover effects, active tabs, selected items, toggles
   - **Data patterns**: what data populates lists/tables/cards — this drives seed data

3. Build a **page map** showing navigation flow between prototype pages.

### 0c. Resource inventory

List all files in `./resources/` and map each to where it appears in the prototypes.
Every resource file must be used in the final application where relevant.

---

## Phase 1: System Design Document

Produce a comprehensive design document at `./docs/design.md`.

### 1a. Data Model

For each entity, specify:
- Table/collection name
- All fields with types, constraints, defaults
- Relationships (foreign keys, many-to-many)
- Indexes needed for query patterns
- **Content mapping**: which prototype elements map to which fields

### 1b. API Design

For every page interaction, define an API endpoint:
- Method + path
- Request params/body schema
- Response schema with example
- Which prototype interaction triggers this API
- Error responses

### 1c. Frontend Architecture

- Component hierarchy (tree structure)
- Route definitions mapping to prototype pages
- State management approach
- How each prototype page maps to components

### 1d. Technology Stack

Choose based on PRD complexity:

| Layer | Choice | When to use |
|-------|--------|-------------|
| Frontend | React + TypeScript + Vite | Default for SPAs |
| Frontend | Next.js | If SSR/SEO needed |
| Styling | Tailwind CSS | Default |
| Backend | Node.js + Express | Simple APIs |
| Backend | Python + FastAPI | If PRD mentions Python |
| Database | SQLite | Simple apps, <10 tables |
| Database | PostgreSQL | Complex apps, relationships |
| ORM | Prisma (Node) / SQLAlchemy (Python) | Match backend |

---

## Phase 2: Seed Data Generation

### Rules

1. **Extract from prototypes**: Every piece of visible text, image, number in the prototype
   images must appear in seed data. Re-read each prototype image and transcribe content.
2. **Complete coverage**: Every list/table/card/dropdown must match prototype content exactly.
3. **Use resource files**: Map resource files from `./resources/` to seed data entries.
4. **No placeholders**: No "Lorem ipsum", no "Test Item 1", no placeholder images.
5. **Support all states**: Include data for empty states, loaded states, error scenarios.

---

## Phase 3: Backend Implementation

### 3a. Database schema — migrations with constraints, indexes, foreign keys
### 3b. API endpoints — route handlers, validation, error handling, curl-tested
### 3c. Seed data loading — idempotent re-seeding, dependency order
### 3d. Static file serving — backend serves resource files

---

## Phase 4: Frontend Implementation

### 4a. Global styles and tokens — color variables, typography, spacing from prototypes

### 4b. Page-by-page implementation

For **each prototype image**:
1. Re-read the prototype image
2. Build page component matching layout exactly
3. Wire up API calls
4. Implement all interactions (navigation, forms, search, filter, sort, modals, states)

### 4c. Resource integration — copy from `./resources/`, reference correctly
### 4d. Responsive — match prototype viewport, breakpoints if mobile views shown

---

## Phase 5: Visual Verification Loop

**Repeat for every page. Max 3 iterations.**

### 5a. Render page to screenshot

Start local server, capture with Playwright:

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    page.goto('http://localhost:3000/page-path')
    page.wait_for_load_state('networkidle')
    page.screenshot(path='docs/screenshots/page_name.png', full_page=True)
    browser.close()
"
```

### 5b. Visual comparison

Read prototype image and screenshot side by side. Compare:
- Layout, colors, typography, content, spacing, images, components

### 5c. Fix discrepancies → re-render → re-compare

---

## Phase 6: Integration Testing

### 6a. API health check — curl each endpoint, verify status codes
### 6b. E2E flow — walk through every user flow from PRD
### 6c. Fix issues — CORS, URL mismatches, data format problems

---

## Phase 7: Deployment Script

Generate `./start.sh` — fully self-contained, works from absolute zero.

Requirements: install deps → setup DB → migrations → seed → build frontend → start both → app at :3000

---

## Phase 8: Documentation

- `./docs/design.md` — final architecture, data model, API reference
- `./README.md` — overview, stack, quick start, structure

---

## Deliverables Checklist

- [ ] All PRD features implemented
- [ ] All prototype pages built
- [ ] Visual match verified via screenshots
- [ ] All resources used
- [ ] Seed data matches prototypes
- [ ] All API endpoints working
- [ ] All interactions functional
- [ ] `bash start.sh` works from clean state
- [ ] Documentation complete

---

## Critical Principles

1. **Prototypes are truth** — prototype wins over PRD text for visual/layout decisions
2. **No shortcuts on data** — all visible content from database via APIs
3. **Complete implementation** — every page, feature, interaction
4. **Resources must be used** — matching files from `./resources/`
5. **Reproducibility** — `start.sh` works from absolute zero
6. **Verify, don't assume** — screenshot comparison + API checks + startup test
