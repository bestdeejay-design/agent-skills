---
name: seo-crawl
description: "Crawlability and site structure for SEO: robots.txt, noindex, canonical, redirect chains, sitemap.xml; internal linking, click depth, orphan pages, URL hierarchy, breadcrumbs; competitor comparison (gaps, overlapping keywords, content gaps). Commands documented in commands/. Triggers: 'seo crawl', 'crawlability', 'robots txt', 'site structure', 'URL structure', 'competitor seo', 'индексация', 'структура сайта', 'конкуренты seo', 'краулинг'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.0.0"
compatibility: "No scripts — agent-driven workflows (commands/)"
---

# SEO Crawl — crawlability, structure & competitors

Use this skill for the **crawl/visibility** layer of SEO: whether search engines
can reach the site, how it is internally linked, and how it compares to
competitors.

## Commands (documented in `commands/`)

| Command | What it does |
|---|---|
| `seo-crawl` | Crawlability: robots.txt, noindex, canonical, redirect chains, sitemap.xml |
| `seo-structure` | Internal linking, click depth, orphan pages, URL hierarchy, breadcrumbs |
| `seo-compare` | Competitor comparison: gaps, overlapping keywords, content gaps (URL mode) |

Modes: **URL** (external sites) and **File** (local projects); `seo-compare` is URL-only.

## When to use

- User asks for "seo crawl", "crawlability", "robots txt", "site structure",
  "URL structure", "competitor seo", "индексация", "структура сайта".
- Indexation, linking structure or competitor gaps are the task.

## Do NOT use

- For the full technical audit / CWV / reports / fixes — that is `seo-audit`.
- For schema.org / meta tags — that is `seo-schema`.
- For content / keywords / headings / images — that is `seo-content`.
