---
name: frontend-performance
description: "Audit web performance depth beyond Lighthouse: offline network/header + built-asset analysis (HTTP/2-3, text compression, browser caching, HSTS, TTFB, page weight, bundle size, duplicate JS libs, resource hints, service worker, speculation rules, streaming, virtualization) plus a Lighthouse Core Web Vitals runner (LCP/FCP/INP/CLS, critical chains, render-blocking). Maps the Front-End-Checklist Performance category (43 rules). Pure-Python stdlib offline auditor (perf_headers.py) + stable-API Lighthouse runner (audit.js). Invoked by /frontend and mobile-frontend. Triggers: 'performance audit', 'frontend perf', 'lighthouse', 'core web vitals', 'page speed', 'CLS LCP INP', 'optimize loading', 'bundle size', 'проверь производительность', 'perf check'."
license: MIT
metadata:
  author: best
  version: 1.0.0
when_to_use: "Use to audit/polish web performance depth: 'performance audit', 'frontend perf', 'lighthouse', 'core web vitals', 'page speed', 'CLS LCP INP', 'optimize loading', 'bundle size', 'проверь производительность'. Examples: 'audit my page for LCP/FCP/INP/CLS', 'why is my bundle so big', 'check HTTP/2 and compression headers'."
---

# frontend-performance

A performance specialist that goes **beyond** what `frontend-perfection`
already does. `frontend-perfection` runs Lighthouse + a couple of resource-hint
checks and owns contrast/tokens/SEO/a11y. This skill owns **performance depth**:
the network/header and built-asset layer that Lighthouse cannot see offline,
plus a focused Core Web Vitals Lighthouse run.

Two engines, clearly split by what they can measure:

- **`perf_headers.py`** — PURE Python 3 stdlib, **OFFLINE**. Inspects response
  headers + protocol + transfer timing for a URL, and statically analyzes a
  built asset tree (page weight, largest bundles, duplicate libs, missing
  preloads, GIF→video, service worker, speculation rules, streaming,
  virtualization, third-party async). No network needed for the directory mode.
- **`audit.js`** — real Chrome via chrome-launcher + Lighthouse >= 13 (stable
  API, `.default` fallback). Measures the runtime metrics: LCP, FCP, INP, CLS,
  TTFB, critical request chains, render-blocking resources, compression, HTTP/2.

## When to use

- User asks for a "performance audit", "page speed", "core web vitals",
  "bundle size", "optimize loading", "check HTTP/2 / compression / caching".
- User reports slow LCP/CLS/INP or a heavy bundle.
- `frontend-perfection` already passed but the user wants perf depth, or the
  orchestrator (`/frontend`, `mobile-frontend`) delegates the perf slice.

## Composition

- For contrast/tokens/SEO/a11y/OG — load `frontend-perfection` (this skill
  does NOT reimplement those; it owns performance only).
- For SEO-layer breadth — load `seo-toolkit`.
- For a visual direction before building — load `frontend-design-taste`.

## Workflow

1. **Locate the target** — a live URL, or a built asset directory
   (static HTML/CSS/JS or a bundled SPA).
2. **Run the offline auditor** (no Chrome needed):
   ```bash
   python3 scripts/perf_headers.py --url https://example.com --out perf-url.json
   python3 scripts/perf_headers.py --dir ./dist --out perf-dist.json
   ```
   Exit `0` = no `fail` checks; `1` = at least one `fail`; `2` = runner error.
3. **Run the Lighthouse CWV runner** (real Chrome) for the runtime metrics:
   ```bash
   node scripts/audit.js --url https://example.com --mobile --out lh-perf.json
   node scripts/audit.js --url https://example.com --desktop --out lh-perf-d.json
   ```
   Default `--threshold 90` on the performance category; exit `0` only when
   performance ≥ threshold. Add `--only performance` (default) or another
   category if iterating.
4. **Fix by audit id** — every fix references the audit it closes
   (`perf:http2-3`, `perf:page-weight`, `perf:lcp`, `perf:js-bundle-size`, …).
5. **Re-audit until green** on both engines and both form factors.
6. **Write the before/after report** — input paths, exact commands, real
   output, interpretation, and what was deliberately NOT done.

## audit.js — Lighthouse runner (stable API)

- Real Chrome via **chrome-launcher** (default channel = installed Chrome;
  `--no-headless` to watch). No Playwright internals, no private CDP fields.
- **Lighthouse >= 13 support**: falls back to `require("lighthouse").default`.
- **Dependency isolation**: local `node_modules` → `NODE_PATH` → `npm root -g`.
  Install instead of dying:
  ```bash
  npm i lighthouse chrome-launcher          # in the script's dir
  # or globally:
  npm i -g lighthouse chrome-launcher && export NODE_PATH=$(npm root -g)
  ```
- Output: compact JSON (`--out`) with the performance score, a `cwv` block
  (LCP/FCP/INP/CLS/TBT/Speed-Index + key audits with numeric values), and only
  the **failed weighted audits** (id, title, score, weight).
- Exit codes: `0` performance ≥ threshold, `1` below, `2` runner error.
- Default category is `performance`; `--only <category>` to scope.

## perf_headers.py — offline auditor (Python stdlib, no deps)

Checks and their ids. Tag `static` = offline header/asset check,
`lighthouse` = measured by audit.js, `manual` = needs WebPageTest/human.

| id | checklist rule (Performance) | tag | how measured |
|---|---|---|---|
| `perf:http2-3` | Enable HTTP/2 or HTTP/3 | static | response protocol (info if urllib can't confirm — verify in Lighthouse) |
| `perf:text-compression` | Enable text-based compression | static | `content-encoding: gzip\|br` |
| `perf:browser-caching` | Enable browser caching | static | `cache-control` max-age + `etag` |
| `perf:hsts` | (security reused) HSTS | static | `strict-transport-security` |
| `perf:sec:*` | (security reused) CSP/XCTO/XFO/Referrer | static | presence of security headers |
| `perf:content-type` | correct content-type | static | `content-type` present |
| `perf:ttfb` | Reduce TTFB | static | HEAD latency (best-effort) |
| `perf:page-weight` | Keep page weight <1500KB (<500KB ideal) | static | sum of built tree / HTML doc size |
| `perf:js-bundle-size` | Optimize JS bundle size | static | largest `.js` files vs 250KB |
| `perf:css-size` | Optimize CSS file size | static | largest `.css` files vs 100KB |
| `perf:no-dup-js-libs` | Remove duplicate JS libraries | static | md5 content dup + version-stripped name |
| `perf:gif-to-video` | Convert animated GIFs to video | static | `.gif` presence |
| `perf:resource-hints` | Use resource hints (preload/prefetch/preconnect) | static | `<link rel>` hints in HTML |
| `perf:preconnect` | Use preconnect for critical 3p origins | static | `rel=preconnect` |
| `perf:fetchpriority` | Use fetchpriority | static | `fetchpriority` attribute |
| `perf:no-lazy-above-fold` | Disable lazy loading above the fold | static | early `<img loading=lazy>` / missing preload |
| `perf:lazy-offscreen` | Lazy loading for offscreen content | static | `<img loading=lazy>` when 3+ imgs |
| `perf:service-worker` | Register a service worker | static | `serviceWorker` / `sw.js` |
| `perf:speculation-rules` | Speculation Rules API | static | `speculationrules` |
| `perf:stream-html` | Stream HTML to browser | static | `transfer-encoding` / `renderToPipeableStream` |
| `perf:source-maps` | Source maps for debugging | static | `.map` / `sourceMappingURL` |
| `perf:virtualize-lists` | Virtualize long lists/tables | static | >500 `<li>` heuristic |
| `perf:third-party-async` | Optimize third-party script loading | static | external `<script>` async/defer |
| `perf:cdn` | Use a CDN | static | server/via header heuristic |
| `perf:lcp` | Optimize LCP (<2.5s, Critical) | lighthouse | `largest-contentfulpaint` |
| `perf:fcp` | Optimize FCP (<1.8s) | lighthouse | `first-contentful-paint` |
| `perf:inp` | Optimize INP (<200ms) | lighthouse | `interactive` (TBT proxy) |
| `perf:cls` | Minimize CLS (<0.1) | lighthouse | `cumulative-layout-shift` |
| `perf:load-time-3s` | Page load <3s | lighthouse | speed-index / load |
| `perf:critical-chains` | Minimize critical request chains | lighthouse | `critical-request-chains` |
| `perf:no-render-blocking` | Eliminate render-blocking resources | lighthouse | `render-blocking-resources` |
| `perf:min-http-requests` | Minimize HTTP requests | lighthouse | `network-requests` |
| `perf:dom-size` | Reduce DOM size/complexity | lighthouse | `dom-size` |
| `perf:no-legacy-js` | Avoid legacy JS to modern browsers | lighthouse | `legacy-javascript` |
| `perf:no-js-redirects` | Avoid JS-based redirects | lighthouse | `redirects` |
| `perf:font-loading` | Optimize web font loading | lighthouse | `font-display` / `render-blocking` |
| `perf:defer-on-interaction` | Load non-critical code on interaction | lighthouse | `unused-javascript` / TBT |
| `perf:viewport-aware` | Load code when near viewport | lighthouse | `unused-javascript` |
| `perf:bfcache` | Optimize back/forward cache | static | heuristic: no `unload` listeners (manual confirm) |
| `perf:secure-js-libs` | Use secure/up-to-date JS libs | lighthouse | `lighthousec.js-libraries` (best-effort) |
| `perf:webpagetest` | Analyze with WebPageTest | manual | human/WebPageTest run |
| `perf:consent-mode-v2` | Google Consent Mode v2 | manual | privacy/consent config review |
| `perf:gtm-efficient` | Optimize GTM implementation | manual | tag-config review |
| `perf:offline-fallback` | Offline fallback page | static | service worker + offline route (best-effort) |
| `perf:loading-indicators` | Show loading indicators | static | app-code review (best-effort) |

## Constraints / non-goals

- `audit.js` opens a **real Chrome**; do not substitute CLI `lighthouse`
  headless-shell in the default call.
- `perf_headers.py` is offline and stdlib-only — no PyYAML, no requests, no
  third-party packages. Network-dependent checks (URL mode) degrade to `info`
  when the host is unreachable; the directory mode never needs a network.
- HTTP/2 or /3 **cannot be confirmed by urllib** (it speaks HTTP/1.1). The
  `perf:http2-3` check reports the observed protocol and marks itself `info`;
  confirm with Lighthouse / WebPageTest.
- Do NOT reimplement contrast/token/SEO/a11y checks — those belong to
  `frontend-perfection`.
- Do NOT fix by hiding audits: raise the underlying metric at the root.
- Do NOT delete or modify user tests/screenshots; artifacts go to `--out`.

## Examples

**Full loop on a live site:**
```bash
python3 scripts/perf_headers.py --url https://example.com --out perf-url.json
node scripts/audit.js --url https://example.com --mobile --out lh-perf.json
node scripts/audit.js --url https://example.com --desktop --out lh-perf-d.json
```

**Built SPA in ./dist (no network needed):**
```bash
python3 scripts/perf_headers.py --dir ./dist --out perf-dist.json
```

**Iterate on performance until green:**
```bash
node scripts/audit.js --url http://localhost:8377/ --mobile --only performance
```

See `references/canonical-patterns.md` for the canonical Front-End-Checklist
Performance sources this skill is aligned with.
