---
name: seo-toolkit
description: "13 SEO commands for AI agents: technical audit, Core Web Vitals, crawlability, schema.org, keywords, meta tags, content analysis, images, reports, competitor comparison, and autonomous fixes. Works in URL mode (fetch external sites) and file mode (analyze local project). Canonical patterns: weighted scoring, P1-P5 prioritization, diff-before-apply safety, dual URL/FS modes."
license: MIT
metadata:
  author: skills-sh
  version: "1.0.0"
  compatibility: "Requires Python 3, curl, jq. Network access for URL mode."
---

# SEO Toolkit — 13 SEO Commands for AI Agents

Load this skill whenever you need to run **any SEO task**: technical audit, Core
Web Vitals analysis, crawlability checks, schema.org validation, keywords, meta
tags, content, images, reports, competitor comparison, or autonomous fixes.

The skill works in **two modes**:
- **URL mode** — fetch external site + `robots.txt` + `sitemap.xml` + key pages
- **File mode** — analyze a local project (`pages/`, `app/`, `public/`, framework configs)

---

## Commands (13 slash-commands)

| Command | Description | Mode | Triggers |
|---|---|---|---|
| [`seo-audit`](commands/seo-audit.md) | Full technical audit: meta, headings, alt, broken links, sitemap, robots.txt, canonical, URL structure | URL / File | `/seo-audit`, `seo audit`, `technical audit` |
| [`seo-speed`](commands/seo-speed.md) | Core Web Vitals (LCP/CLS/INP), blocking resources, unused CSS/JS, caching | URL / File | `/seo-speed`, `core web vitals`, `site speed` |
| [`seo-structure`](commands/seo-structure.md) | Internal linking, click depth, orphan pages, URL hierarchy, breadcrumbs | URL / File | `/seo-structure`, `site structure`, `URL structure` |
| [`seo-crawl`](commands/seo-crawl.md) | Crawlability: robots.txt, noindex, canonical, redirect chains, sitemap.xml | URL / File | `/seo-crawl`, `crawlability`, `robots txt` |
| [`seo-schema`](commands/seo-schema.md) | JSON-LD schema.org: Product, Article, Organization, Breadcrumb, FAQ, validation | URL / File | `/seo-schema`, `json-ld`, `schema org`, `structured data` |
| [`seo-keywords`](commands/seo-keywords.md) | Keyword density, cannibalization, LSI, long-tail, intent mapping | URL / File | `/seo-keywords`, `keywords`, `keyword research` |
| [`seo-meta`](commands/seo-meta.md) | Title/description generation: lengths, uniqueness, CTR, Open Graph, Twitter Cards | URL / File | `/seo-meta`, `meta tags`, `title description` |
| [`seo-headings`](commands/seo-headings.md) | H1-H6 hierarchy, order, keywords in headings, accessibility | URL / File | `/seo-headings`, `headings`, `h1 h2 h3` |
| [`seo-content`](commands/seo-content.md) | Thin content, duplicates, readability (Flesch-Kincaid), E-E-A-T signals | URL / File | `/seo-content`, `content audit`, `content analysis` |
| [`seo-images`](commands/seo-images.md) | Alt text, WebP/AVIF, lazy loading, dimensions, srcset | URL / File | `/seo-images`, `image seo`, `image optimization` |
| [`seo-report`](commands/seo-report.md) | Comprehensive scored report (7 dimensions, weights 100%), weekly action plan | URL / File | `/seo-report`, `seo report`, `SEO summary` |
| [`seo-compare`](commands/seo-compare.md) | Competitor comparison: gaps, overlapping keywords, content gaps | URL | `/seo-compare`, `competitor seo`, `competitor analysis` |
| [`seo-fix`](commands/seo-fix.md) | Autonomous fix agent: P1-P5 prioritization, diff-before-apply, safety rules | File | `/seo-fix`, `seo fix`, `automated seo fixes` |

---

## Operating modes

### URL Mode (default for external sites)
```
User: /seo-audit https://lovii.ru
Agent: fetch https://lovii.ru + robots.txt + sitemap.xml + key internal pages → run the audit
```

### File Mode (for local projects)
```
User: /seo-audit file:///path/to/project
Agent: analyze files in pages/, app/, public/, configs like next.config.js, astro.config.mjs, .htaccess
```

---

## Canonical patterns (for development/enrichment)

Full deep-dive — in `references/canonical-patterns.md`. Key canons:

- **Dual URL/FS mode** — every command works in both modes: by URL (`https://...`) or local files (`file:///path`), like Playwright test fixtures
- **Weighted scoring** — 7 dimensions with weights (seo-report): Meta 20%, Content 20%, Crawl 15%, Images 15%, Schema 10%, Perf 10%, Links 10% (Google Lighthouse model)
- **P1–P5 prioritization** — autonomous fixes prioritized by impact (like security advisories)
- **Diff-before-apply** — mandatory diff display before applying changes (like GitHub PR review)
- **Safety rules** — never change URLs, delete content, or touch logic without confirmation

---

## Usage examples

```bash
# Full audit of lovii.ru
/seo-audit https://lovii.ru

# Core Web Vitals for a local Next.js project
/seo-speed file:///path/to/lovii_demo

# JSON-LD schema.org validation on a page
/seo-schema https://lovii.ru

# Keywords + cannibalization
/seo-keywords https://lovii.ru

# Comprehensive report with an action plan
/seo-report https://lovii.ru

# Compare with a competitor
/seo-compare https://lovii.ru https://competitor.com

# Autonomous fixes (file mode only)
/seo-fix file:///path/to/lovii_demo
```

---

## Canonical analogues

Full deep-dive — in `references/canonical-patterns.md`. Key canons:

- **Google Lighthouse / PageSpeed Insights** — Core Web Vitals thresholds (LCP ≤ 2.5s, CLS ≤ 0.1, INP ≤ 200ms), scoring weights
- **Google Search Central / Search Console** — crawlability rules, sitemap.xml, robots.txt, canonical, rich snippets
- **schema.org** — JSON-LD vocabulary (Product, Article, Organization, Breadcrumb, FAQ) and required properties
- **Playwright Test** — dual-mode fixtures: URL + file system
- **Screaming Frog / Ahrefs / Semrush** — crawl patterns, keyword cannibalization detection, content gaps
- **GitHub Security Advisories** — P1–P5 prioritization and diff-before-apply safety

---

## Files

- `SKILL.md` — this file
- `skill.json` — manifest
- `references/canonical-patterns.md` — canonical patterns deep dive
- `commands/seo-audit.md` — full technical audit
- `commands/seo-speed.md` — Core Web Vitals
- `commands/seo-structure.md` — site structure & internal linking
- `commands/seo-crawl.md` — crawlability & robots.txt
- `commands/seo-schema.md` — JSON-LD schema.org
- `commands/seo-keywords.md` — keywords, density, cannibalization
- `commands/seo-meta.md` — title/description/OG/Twitter
- `commands/seo-headings.md` — H1-H6 hierarchy
- `commands/seo-content.md` — thin content, duplicates, readability
- `commands/seo-images.md` — alt, WebP/AVIF, lazy loading
- `commands/seo-report.md` — weighted scoring report
- `commands/seo-compare.md` — competitor comparison
- `commands/seo-fix.md` — autonomous fix agent
- `scripts/seo_toolkit.py` — helper script (HTML parser, keyword density counter, JSON-LD validator)

---

## Installation

```bash
# For opencode
cp -r skills/seo-toolkit ~/.config/opencode/skills/

# For other agents
# Copy the skill folder to your skills directory
```