---
name: frontend-perfection
description: "Audit and polish frontend (static HTML/CSS/JS or built SPA) to measurable perfection: real-Chrome Lighthouse >=13 runs (mobile+desktop, no Playwright internals), SEO meta layer, WCAG contrast by computed luminance, heading order, design tokens (zero raw hex outside tokens), adaptive checks, and OG-image generation with a crop-safe layout. Runner audit.js uses chrome-launcher + Lighthouse Node API with .default fallback and self-resolved deps; meta_audit.py is pure Python stdlib, offline. Triggers: 'frontend audit', 'perfect the layout', 'lighthouse check', 'make it 100/100/100/100', 'проверь вёрстку', 'довести фронтенд до идеала', 'og-image для соцсетей', 'SEO-мета слой', 'контраст цветов', 'дизайн-токены'."
---

# frontend-perfection

Audit and polish a frontend — static HTML/CSS/JS or a built SPA — towards
verifiable perfection. The skill exists because production web perf tooling
commonly breaks when it pokes at private APIs (Playwright internals, old
Lighthouse signatures, unisolated global deps). This skill runs on STABLE
apis only, computes exactly (luminance, not eyeballs), and demands a
before/after report bound to audit ids.

## When to use

- User asks to "make the layout perfect", "fix performance", "reach
  100/100/100/100", "check the frontend", "audit the page".
- User wants an OG image or social share meta for a homepage.
- User reports contrast problems, missing SEO tags, broken anchors under a
  fixed header, colors duplicated as raw hex.

## Workflow

1. **Locate the project** — static files (index.html + css/) or built SPA.
2. **Serve it locally** if needed: `python3 -m http.server 8377` (or the
   project's dev server). Static files are fine over http://localhost.
3. **Run audit.js** (Lighthouse, real Chrome):
   ```bash
   node scripts/audit.js --url http://localhost:8377/ --mobile --out lh-mobile.json
   node scripts/audit.js --url http://localhost:8377/ --desktop --out lh-desktop.json
   ```
   Default threshold is 100; exit 0 only when every measured category is
   at or above it. Add `--only <category>` to iterate on one category.
4. **Run meta_audit.py** (SEO/contrast/headings/tokens, offline):
   ```bash
   python3 scripts/meta_audit.py --html index.html --css main.css css/demo.css --out meta.json
   ```
   Exit 0 = no violations; exit 1 = violations found.
5. **Fix by audit id** — every fix must reference the audit it closes
   (e.g. `audit.js` `color-contrast`, `meta_audit.py` `meta:description`).
6. **Re-audit until green** on both form factors. Only then call it done.
7. **Write the before/after report** in the showcase format: input paths,
   exact commands, real output, interpretation. Explicitly list what was
   deliberately NOT done.

## audit.js — Lighthouse runner (stable API)

- Real Chrome via **chrome-launcher** (default channel = installed Chrome;
  `--no-headless` to watch). No Playwright dependency, no private fields,
  no `_ws_url` transport hacks. CDP port comes from `chrome.port` (public).
- **Lighthouse >= 13 support**: module may export a namespace; the script
  falls back to `require("lighthouse").default` automatically.
- **Dependency isolation**: modules resolve local `node_modules` → `NODE_PATH`
  → `npm root -g`. The script *explains* how to install instead of dying with
  `Cannot find module`:
  ```bash
  npm i lighthouse chrome-launcher     # in the script's dir
  # or globally:
  npm i -g lighthouse chrome-launcher && export NODE_PATH=$(npm root -g)
  ```
- Output: compact JSON (`--out`) with per-category scores and only the
  **failed weighted audits** (id, title, score, weight) — no 4000-line dump.
- Exit codes: `0` all categories ≥ threshold, `1` below threshold, `2` runner error.

## meta_audit.py — static audit (Python stdlib, offline)

Checks and their ids:

| id | what it verifies |
|---|---|
| `meta:title` / `meta:title-length` | title present, ≤ 60 chars |
| `meta:description` / `meta:description-length` | description present, ≤ 160 chars |
| `meta:canonical` | canonical link |
| `meta:og:*`, `meta:og:size` | OG tags; image must declare 1200×630 (crop-safe) |
| `meta:twitter:card` | twitter card tag |
| `meta:json-ld` | any `application/ld+json` script |
| `meta:robots` | not blocked with noindex/nofollow |
| `meta:sitemap-link` | sitemap referenced |
| `headings:single-h1` | exactly one h1 |
| `headings:order` | h1→h6 sequence, no level skips (h1→h3 is a violation) |
| `tokens:raw-hex` | zero raw hex outside the token block (`:root`/tokens) |
| `contrast:wcag-aa` | computed WCAG relative luminance, fg/bg pairs ≥ 4.5:1 |
| `adaptive:scroll-padding` | fixed header ⇒ `scroll-padding-top` present |
| `adaptive:media-queries` | responsive breakpoints exist for tablet widths |

## Design tokens — "colors as constants"

For static projects WITHOUT a build system (plain HTML/CSS/JS), a minimal
design system still applies:

- Every hex color must be declared **once** in the token block
  (a `:root { --color-*: ...; }` layer or a dedicated `tokens.css`).
- **Zero raw hex** anywhere else — components reference `var(--color-*)`.
- `meta_audit.py` flags any raw hex outside the token block; this is the
  enforceable version of "no hardcoded colors".
- The same idea extends to type scale and spacing (custom properties), but
  the audit enforces colors only.

## OG image generation — crop-safe social share

Social networks crop images differently (WhatsApp square-ish, Facebook
center-crop). The skill's rules, learned the hard way:

1. **Change the file name, never overwrite** — social caches keyed by URL
   will keep showing the old preview forever. New content ⇒ new URL
   (e.g. `og-2026-08-09.png`).
2. **Content must fit the central safe zone** — standard 1200×630 canvas is
   not enough: keep the hero/graphic content within ~600–640px centered
   width so a square/center crop (≈630×630) never clips text or logos.
3. **Force a reflow before the screenshot** — after setting width via inline
   style, the first `screenshot()` may capture the stale layout. Read
   `void element.offsetHeight` (or `getBoundingClientRect()`) to force
   layout sync, then shoot.
4. **Declare exact dimensions** — `og:image:width`/`og:image:height` =
   `1200`/`630` so scrapers don't guess and mis-trim.
5. Re-test in 2+ networks after changing the URL (WhatsApp + Telegram at
   minimum; they cache most aggressively).

## Fixed-header anchoring

If `position: fixed` header exists, anchor jumps hide content underneath.
Fix: `html { scroll-padding-top: <header-height> }` (+ `scroll-margin-top` on
the anchors if needed). `meta_audit.py` reports `adaptive:scroll-padding`
when this is missing.

## Constraints / non-goals

- audit.js opens a **real Chrome**; do not substitute CLI `lighthouse`
  headless-shell in the default call.
- Meta audit is offline and stdlib-only — no PyYAML, no requests.
- Do NOT fix with `!important` spray or target 100 by hiding audits: raise
  the underlying metrics (real fix at the root).
- Do NOT delete or modify user tests/screenshots; artifacts go to `--out`
  files you name.
- Lighthouse scores on `localhost` vs production differ (no CDN, no real
  TLS); state this in the report when it matters.

## Examples

**Full loop on a static site:**
```bash
cd ~/projects/lovii_demo
python3 -m http.server 8377 &
node .../audit.js --url http://localhost:8377/ --mobile --out lh-mobile.json
node .../audit.js --url http://localhost:8377/ --desktop --out lh-desktop.json
python3 .../meta_audit.py --html index.html --css main.css css/demo.css --out meta.json
```

**Iterate on one category until green:**
```bash
node .../audit.js --url http://localhost:8377/ --mobile --only accessibility
```

See `references/canonical-patterns.md` for the canonical sources this skill
is aligned with, and the showcase in `docs/showcase/showcase-frontend-perfection-lovii.md`.