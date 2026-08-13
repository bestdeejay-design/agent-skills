---
name: seo-content
description: "Content and on-page SEO: thin content & duplicates, readability (Flesch-Kincaid), E-E-A-T signals; keyword density, cannibalization, LSI, long-tail, intent mapping; H1-H6 hierarchy and keywords in headings; image SEO (alt text, WebP/AVIF, lazy loading, dimensions, srcset). Script seo_content.py: keyword density + top terms (script/style stripped). Triggers: 'seo content', 'content audit', 'keywords', 'keyword research', 'seo headings', 'image seo', 'контент аудит', 'ключевые слова', 'заголовки h1', 'оптимизация картинок'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.0.0"
compatibility: "Requires python3 (stdlib only)"
---

# SEO Content — on-page content & images

Use this skill for the **content** layer of SEO: on-page text quality, keywords,
headings, and image optimization.

## Commands (documented in `commands/`)

| Command | What it does |
|---|---|
| `seo-content` | Thin content, duplicates, readability (Flesch-Kincaid), E-E-A-T signals |
| `seo-keywords` | Keyword density, cannibalization, LSI, long-tail, intent mapping |
| `seo-headings` | H1–H6 hierarchy, order, keywords in headings, accessibility |
| `seo-images` | Alt text, WebP/AVIF, lazy loading, dimensions, srcset |

## Script

```bash
python3 scripts/seo_content.py --density --file page.html --keyword "fitness"
```

Keyword density + top terms. Script/style content is stripped first so CSS/JS
source does not inflate the word count. Pure Python stdlib; stdin supported.

## When to use

- User asks for "seo content", "content audit", "keywords", "keyword research",
  "seo headings", "image seo", "контент аудит", "ключевые слова".
- On-page content quality, headings hierarchy or image optimization is the task.

## Do NOT use

- For the full technical audit / CWV / reports / fixes — that is `seo-audit`.
- For schema.org / meta tags — that is `seo-schema`.
- For crawlability / linking structure / competitors — that is `seo-crawl`.
