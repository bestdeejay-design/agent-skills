---
name: seo-toolkit
description: "DEPRECATED meta-skill. Routes to the four focused SEO skills that replaced it: seo-audit (technical audit + Core Web Vitals + report + fixes), seo-schema (JSON-LD + meta/OG/Twitter), seo-content (content + keywords + headings + images), seo-crawl (crawlability + structure + competitors). Load one of the four directly instead. Triggers: 'seo', 'сео', 'seo toolkit', 'поисковая оптимизация'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "2.0.0"
compatibility: "Router only — delegates to seo-audit / seo-schema / seo-content / seo-crawl"
when_to_use: "DEPRECATED router — use to pick the right SEO sub-skill: 'seo', 'сео', 'seo toolkit', 'поисковая оптимизация'. Example: 'I need SEO help, which skill?' / 'Какой скилл по SEO взять?'. Routes to seo-audit/schema/content/crawl."
---

# SEO Toolkit — DEPRECATED (router)

> **This skill is deprecated.** The 13 commands were split into four focused
> skills. Do **not** run the old 13-command workflow — load the matching
> sub-skill directly.

## Routing table

| Need | Load this skill instead |
|---|---|
| Full technical audit, Core Web Vitals, scored report, autonomous fixes | `seo-audit` |
| JSON-LD schema.org, meta tags, Open Graph, Twitter Cards | `seo-schema` |
| Content quality, keywords, headings, image SEO | `seo-content` |
| Crawlability, internal linking, URL structure, competitors | `seo-crawl` |

The old command docs moved into the four new skills:

- seo-audit / seo-speed / seo-report / seo-fix → `seo-audit`
- seo-schema / seo-meta + `seo_schema.py` (meta, jsonld) → `seo-schema`
- seo-content / seo-keywords / seo-headings / seo-images + `seo_content.py` (density) → `seo-content`
- seo-crawl / seo-structure / seo-compare → `seo-crawl`

## Removal plan

Keep this router for one release cycle for backward compatibility, then delete.
