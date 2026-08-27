# Canonical patterns — frontend-performance

This skill is aligned with the **Front-End-Checklist "Performance"** category
(43 rules) and the Core Web Vitals definitions from web.dev / Google.

## Core Web Vitals thresholds (Google)

| Metric | Good | Needs improvement | Poor |
|---|---|---|---|
| LCP (Largest Contentful Paint) | ≤ 2.5s | 2.5s–4.0s | > 4.0s |
| INP (Interaction to Next Paint) | ≤ 200ms | 200ms–500ms | > 500ms |
| CLS (Cumulative Layout Shift) | ≤ 0.1 | 0.1–0.25 | > 0.25 |

Supporting: FCP ≤ 1.8s, TTFB ≤ 800ms, page load ≤ 3s, page weight < 1500KB
(ideal < 500KB).

## Offline vs measured split

- **Offline (`perf_headers.py`, static):** headers, protocol, caching, HSTS,
  page weight, bundle size, duplicate libs, resource hints, service worker,
  speculation rules, streaming, virtualization, third-party async, GIF→video.
- **Measured (`audit.js`, lighthouse):** LCP, FCP, INP (TBT proxy), CLS,
  critical chains, render-blocking, compression, HTTP/2, legacy JS, redirects,
  DOM size, unused JS.
- **Manual (`perf:webpagetest`, `perf:consent-mode-v2`, `perf:gtm-efficient`,
  `perf:loading-indicators`, `perf:bfcache` confirm):** require WebPageTest or
  human/config review beyond what the two engines capture.

## Why two engines

Lighthouse cannot see raw response headers, CDN signatures, duplicate library
copies, or static build structure without a full render. The offline auditor
covers that layer; Lighthouse covers runtime. Together they close the 43-rule
Performance category without external MCP servers or third-party Python deps.
