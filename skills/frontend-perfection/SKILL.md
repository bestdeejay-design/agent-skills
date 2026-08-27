---
name: frontend-perfection
description: "Audit and polish frontend (static HTML/CSS/JS or built SPA) to measurable perfection: real-Chrome Lighthouse >=13 runs (mobile+desktop, no Playwright internals), SEO meta layer, WCAG contrast by computed luminance, heading order, a11y checks (axe-core subset), back-to-top navigation, design tokens (zero raw hex), adaptive checks, OG-image generation, plus Security/Privacy/i18n static coverage (HTTPS/mixed content, CSP, SRI, security headers, noopener, secrets-in-URL, cookie consent, i18n lang/dir/Intl). Front-End Checklist-inspired. Triggers: 'frontend audit', 'perfect the layout', 'lighthouse check', 'make it 100/100/100/100', 'audit the page', 'fix performance', 'contrast check', 'design tokens', 'og image', 'security headers', 'privacy', 'https', 'mixed content', 'CSP', 'SRI', 'i18n', 'internationalization', 'social share meta'."
license: MIT
metadata:
  author: best
  version: 1.5.0
when_to_use: "Use to audit/polish a frontend to measurable perfection: 'frontend audit', 'perfect the layout', 'lighthouse check', 'make it 100/100/100/100', 'audit the page', 'fix performance', 'contrast check', 'design tokens', 'og image', 'social share meta'. Examples: 'audit my page for Lighthouse 100', 'fix contrast and SEO meta on the homepage'."
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

## Composition

- For Core Web Vitals / schema.org / SEO deep-dives — load `seo-toolkit` (this skill
  measures layout, contrast, tokens and a11y; the SEO-layer breadth lives there).
- For a distinctive visual DIRECTION before building — load `frontend-design-taste`
  (palette/type/signature), then run this skill to verify the result.

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
  - **Run security_privacy_audit.py** (Security/Privacy/i18n, offline) — see the
    section below. Exit 0 = no violations; exit 1 = violations found.
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
| `a11y:img-alt` | every `<img>` has an `alt` attribute (decorative may be empty) — WCAG 1.1.1 / axe `image-alt` |
| `a11y:button-name` / `a11y:link-name` | buttons and links have an accessible name (text or aria-label) — WCAG 4.1.2 / axe `button-name`, `link-name` |
| `a11y:form-label` | inputs/selects/textareas have a label (`<label for>`, wrapper, aria-label) — WCAG 4.1.2 / axe `label` |
| `a11y:aria-valid` | every `aria-*` attribute name is in the WAI-ARIA 1.2 set — axe `aria-valid-attr` |
| `a11y:landmark-unique` | at most one `<main>`; multiple `<nav>` need distinct labels — WCAG 1.3.1 / axe `landmark-unique` |
| `html:doctype` | HTML5 doctype on the first line |
| `html:charset` | charset declared as utf-8 |
| `html:viewport` | responsive viewport meta present |
| `html:lang` | `<html lang>` with a BCP 47 code (a11y + SEO) |
| `html:dir-rtl` | RTL languages (ar/he/fa/ur/yi) require `dir="rtl"` |
| `html:unique-id` | no duplicate `id` attributes |
| `html:semantic` | semantic elements used: header, main, footer |
| `html:favicons` | favicon link present |
| `html:web-app-manifest` | manifest.json referenced (PWA) |
| `html:sri` | CDN-hosted scripts carry `integrity` (SRI); local scripts exempt |
| `html:defer-async` | external scripts load with defer/async/type=module (no render-blocking) |
| `html:input-types` | inputs declare a `type` (not defaulting to text) |
| `images:dimensions` | img has width/height (CLS prevention) |
| `images:lazy-loading` | 3+ images lazy-load offscreen content |
| `images:srcset` | responsive srcset used for fixed-size images |
| `images:modern-format` | raster jpg/png converted to webp/avif |
| `js:no-inline` | no inline handlers (`onclick=…`) or inline `<script>` blocks |
| `js:no-console` | no `console.log/debug/warn` in HTML |
| `css:focus-visible` | visible `:focus-visible` indicator for keyboard users |
| `css:print` | `@media print` stylesheet exists |
| `css:dark-mode` | `prefers-color-scheme` dark mode supported |
| `css:font-display` | webfonts use `font-display: swap` (no FOIT) |
| `perf:resource-hints` | preload/preconnect/dns-prefetch hints for critical origins (LCP) |
| `security:https` | no `http://` URLs in src/href |
| `security:noopener` | `target="_blank"` links carry `rel="noopener"` |
| `privacy:consent` | cookie/consent mention present (GDPR / 152-ФЗ) |
| `nav:back-to-top` | long pages have a way back to top — logo links to top and/or a floating scroll-to-top button (bottom-right, aria-label, appears after scroll) — WCAG 2.4.1 / UX pattern |

## Security, Privacy & i18n (static, offline)

`scripts/security_privacy_audit.py` extends the skill with the Front-End-Checklist
**Security** (22), **Privacy** (5) and **Internationalization** (5) categories — the
statically verifiable subset. It is pure Python 3 stdlib (no `requests`/`bs4`/
`PyYAML`), mirrors `meta_audit.py`'s JSON/exit-code conventions, and emits audit ids
prefixed `sec:` / `priv:` / `i18n:`. It does NOT duplicate the dedicated sibling
skills' a11y/perf/testing checks — only Security/Privacy/i18n.

```bash
python3 scripts/security_privacy_audit.py --html index.html --css main.css --js app.js --out sec.json
python3 scripts/security_privacy_audit.py --html a.html b.html --json   # stdout JSON
```

Exit `0` = no violations; `1` = ≥1 violation; `2` = runner error. The report is
**machine-readable JSON only** on stdout (no human summary) — evidence gate.

| id | severity | what it verifies |
|---|---|---|
| `sec:https` | high | no `http://` URLs in href/src (HTTPS everywhere) |
| `sec:mixed-content` | high | no `http://` in CSS `url()`/`@import`/srcset (mixed content) |
| `sec:csp` | medium | Content-Security-Policy present (meta or server header) — OWASP A05 |
| `sec:sri` | high | external `<script>`/`<link>` carry `integrity` (SRI) |
| `sec:security-headers` | low | HSTS/XCTO/XFO/Referrer-Policy/Permissions-Policy (meta; server-side canonical) |
| `sec:noopener` | high | `target="_blank"` carries `rel="noopener noreferrer"` |
| `sec:secrets-in-url` | critical | no tokens/keys in query strings (`token=`/`api_key=`/`secret=`) |
| `sec:localstorage-secrets` | medium | no secret keys in localStorage/sessionStorage |
| `sec:csrf` | medium | state-changing (POST) forms carry a CSRF token |
| `sec:eval` | high | no `eval()`/`new Function()` in JS |
| `sec:deprecated-crypto` | medium | no md5/sha1 in security context |
| `sec:external-origins` | low | external script origins enumerated (info) |
| `sec:internal-leak` | medium | no internal IPs / `.env` references leaked |
| `sec:cookie-flags` | low | `document.cookie` assignments use `Secure` |
| `priv:cookie-consent` | medium | cookie/consent banner before non-essential tracking (GDPR / 152-ФЗ) |
| `priv:tracking-before-consent` | medium | no tracking scripts (GA/GTM/fbq/Metrika) before consent |
| `priv:privacy-policy` | low | privacy policy link present |
| `priv:dnt` | low | Do Not Track / Global Privacy Control respected (info/manual) |
| `priv:third-party-data` | low | no PII sent to third parties without consent (info) |
| `i18n:lang` | medium | `<html lang>` present, valid BCP 47 |
| `i18n:dir` | medium | RTL languages (ar/he/fa/ur/yi) set `dir="rtl"` |
| `i18n:intl-api` | low | `Intl.NumberFormat`/`DateTimeFormat` used for formatting (info) |
| `i18n:charset-early` | medium | `<meta charset>` within first 1024 bytes |
| `i18n:hardcoded-locale` | low | no hardcoded locale-specific strings (info) |

### Static subset only — runtime/header checks are manual

`security_privacy_audit.py` covers the **static** surface. The following require a
live server or manual review and are NOT asserted by the script:
- Real HTTP response headers (Strict-Transport-Security, X-Content-Type-Options,
  X-Frame-Options, Referrer-Policy, Permissions-Policy, CSP as a header) — verify
  with `frontend-performance`'s `perf_headers.py` (`perf:sec:*` / `perf:hsts`) or
  `curl -I`.
- Live cookie flags (Secure/HttpOnly/SameSite on `Set-Cookie`) — inspect response
  headers.
- CSP violation reporting, real mixed-content in dev proxies, screen-reader/locale
  correctness.

### Routing to dedicated skills

For depth beyond this skill's baseline, delegate to the dedicated sibling skills
(same `skills/` dir):
- **Deep accessibility** (95 rules: tables, landmarks, ARIA values, focus traps,
  runtime contrast, screen-reader) → `frontend-a11y` (`scripts/a11y_audit.py`
  static + `a11y_axe.mjs` runtime).
- **Deep performance** (network/headers, Core Web Vitals, bundle size, HTTP/2,
  caching, service worker) → `frontend-performance` (`perf_headers.py` offline +
  `audit.js` Lighthouse).
- **E2E / visual / contract / a11y-in-CI testing** (Playwright, jest-axe, Pact,
  perf-budget CI) → `frontend-testing` (scaffolds configs; does not re-audit).

Do NOT re-implement those domains here — this skill owns layout/perf-SEO/tokens +
the Security/Privacy/i18n static subset above; the siblings own their full
categories.

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