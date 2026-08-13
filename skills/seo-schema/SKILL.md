---
name: seo-schema
description: "Structured data and meta markup for SEO: JSON-LD schema.org (Product, Article, Organization, Breadcrumb, FAQ — extraction + validation) and title/description/OG/Twitter meta generation (lengths, uniqueness, CTR). Script seo_schema.py: --meta (title/description/OG/canonical/h1/img audit) and --jsonld (extract + validate JSON-LD blocks). Triggers: 'seo schema', 'json-ld', 'schema org', 'structured data', 'meta tags', 'title description', 'разметка', 'jsonld', 'структурированные данные', 'meta теги'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.0.0"
compatibility: "Requires python3 (stdlib only)"
---

# SEO Schema — structured data & meta markup

Use this skill for the **markup** layer of SEO: structured data (JSON-LD /
schema.org) and meta tags (title, description, Open Graph, Twitter Cards).

## Commands (documented in `commands/`)

| Command | What it does |
|---|---|
| `seo-schema` | JSON-LD schema.org: Product, Article, Organization, Breadcrumb, FAQ — validation |
| `seo-meta` | Title/description generation: lengths, uniqueness, CTR, Open Graph, Twitter Cards |

## Script

```bash
python3 scripts/seo_schema.py --meta file.html      # title/desc/OG/canonical/h1/img audit
python3 scripts/seo_schema.py --jsonld file.html    # extract + validate JSON-LD blocks
```

- `--meta`: title + length, description, canonical, og:title/description/image,
  twitter:card, robots, heading order, missing img alt.
- `--jsonld`: extracts `application/ld+json` blocks and validates `@context`
  (schema.org), `@type`, and type-specific required fields (Product→offers+name,
  Article/BlogPosting→headline+author, FAQPage→mainEntity, Organization→name+url).
- Pure Python stdlib; stdin supported.

## When to use

- User asks for "seo schema", "json-ld", "schema org", "structured data",
  "meta tags", "разметка", "структурированные данные".
- A page needs its schema.org markup and meta layer checked or written.

## Do NOT use

- For the full technical audit / CWV / reports / fixes — that is `seo-audit`.
- For content / keywords / headings / images — that is `seo-content`.
- For crawlability / linking structure — that is `seo-crawl`.
