---
name: seo-audit
description: "Technical SEO audit and health: full technical audit (meta, headings, alt, broken links, sitemap, robots.txt, canonical, URL structure), Core Web Vitals (LCP/CLS/INP, blocking resources, unused CSS/JS, caching), a comprehensive scored report (7 dimensions, weighted 100%), and the autonomous fix agent (P1-P5 prioritization, diff-before-apply). Commands documented in commands/. Triggers: 'seo audit', 'technical audit', 'core web vitals', 'site speed', 'seo report', 'seo fix', 'технический аудит', 'проверка seo', 'скорость сайта'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.0.0"
compatibility: "No scripts — agent-driven workflows (commands/)"
when_to_use: "Use for technical SEO health: 'seo audit', 'technical audit', 'core web vitals', 'site speed', 'seo report', 'seo fix', 'технический аудит', 'проверка seo', 'скорость сайта'. Example: 'Audit my site and fix Core Web Vitals' / 'Проверь техническое SEO сайта'."
---

# SEO Audit — technical site health

Use this skill for the **technical** side of SEO: audit the site, measure Core
Web Vitals, produce a scored report, and apply fixes safely. This is the
"measure and fix" layer of SEO.

## Commands (documented in `commands/`)

| Command | What it does |
|---|---|
| `seo-audit` | Full technical audit: meta, headings, alt, broken links, sitemap, robots.txt, canonical, URL structure |
| `seo-speed` | Core Web Vitals (LCP/CLS/INP), blocking resources, unused CSS/JS, caching |
| `seo-report` | Comprehensive scored report — 7 dimensions, weighted 100%, weekly action plan |
| `seo-fix` | Autonomous fix agent: P1–P5 prioritization, diff-before-apply, safety rules |

Modes: **URL** (external sites) and **File** (local projects).

## When to use

- User asks for "seo audit", "technical audit", "core web vitals", "site speed",
  "seo report", "seo fix", "технический аудит", "проверка seo".
- A site's technical health must be measured, scored and fixed.

## Do NOT use

- For structured data / meta tags / OG — that is `seo-schema`.
- For content / keywords / headings / images — that is `seo-content`.
- For crawlability / linking structure / competitors — that is `seo-crawl`.
