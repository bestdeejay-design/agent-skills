# Canonical patterns: seo-toolkit

> Reference sources and gaps in the current skill relative to the canons.
> Processed from librarian research (August 2026) — the source skill imported
> from the open skills.sh catalog (13 SEO slash-commands).

---

## (a) Named analogues

| # | Name | Owner | URL | Type |
|---|------|-------|-----|------|
| 1 | Google Search Central — Search Essentials (technical SEO) | Google | https://developers.google.com/search/docs/essentials | Official documentation |
| 2 | Lighthouse / PageSpeed Insights | Google | https://developer.chrome.com/docs/lighthouse | Official tool + API |
| 3 | Google Rich Results Test | Google | https://search.google.com/test/rich-results | Official structured data validator |
| 4 | sitemaps.org protocol | sitemaps.org | https://www.sitemaps.org/protocol.html | XML-sitemaps standard |
| 5 | robots.txt protocol (RFC 9309) | Google / IETF | https://www.rfc-editor.org/rfc/rfc9309 | robots.txt standard |
| 6 | schema.org vocabulary | schema.org | https://schema.org/docs/documents.html | JSON-LD/microdata markup standard |
| 7 | Screaming Frog SEO Spider | Screaming Frog | https://www.screamingfrog.co.uk/seo-spider/ | Canonical crawl audit tool |
| 8 | Ahrefs / Semrush | Ahrefs / Semrush | https://ahrefs.com/ , https://www.semrush.com | Commercial SEO platforms |
| 9 | Google Search Console | Google | https://search.google.com/search-console | Official data source |
| 10 | Playwright Test | Microsoft | https://playwright.dev/docs/test-fixtures | Dual-mode / fixtures reference |

---

## (b) Techniques the skill is MISSING

| # | Technique / Source | What is missing in current skill |
|---|--------------------|----------------------------------|
| 1 | **LCP/INP/CLS measurement** (Lighthouse) | Commands provide checklists but no instruction to run Lighthouse/PSI and plug in real numbers (LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1). |
| 2 | **JSON-LD validation beyond syntax** (Rich Results Test) | `seo-schema` doesn't verify required fields per type, `@id` uniqueness, nesting, or types that actually produce rich results (Product, Article, FAQ, Breadcrumb). |
| 3 | **hreflang / international SEO** | No command for hreflang: `lang`/`hreflang` attributes, `x-default`, bidirectional links, canonical for language versions. |
| 4 | **robots.txt wildcard / size limits** | `seo-crawl` does not check: `*` and `$` patterns, 500 KB limit, `Allow`/`Disallow` ordering, `Sitemap:` directive. |
| 5 | **sitemap index / lastmod** (sitemaps.org) | No check of `<lastmod>`, `<sitemapindex>` for >50,000 URLs, UTF-8 encoding, hreflang inside the sitemap. |
| 6 | **Pagination & crawl budget** (Google Search Central) | No analysis of pagination (rel=prev/next is deprecated), noindex for filters, `?utm_`/`?gclid` parameters (URL normalization). |
| 7 | **E-E-A-T / YMYL** (Google Search) | `seo-content` does not assess authorship, about page, contacts, update dates, relevance for YMYL pages. |
| 8 | **Internal linking depth** (Screaming Frog) | `seo-structure` describes depth but no automated computation: orphan pages × internal link count, redirect chains. |
| 9 | **Open Graph / Twitter validation** | `seo-meta` generates title/description but no check of og:image (dimensions), twitter:card, OG uniqueness across pages. |
| 10 | **Fix-agent regression check** | `seo-fix` doesn't require a post-check: re-run `seo-audit` after applying diffs. |
| 11 | **Server logs analysis** (Screaming Frog core) | No server logs analysis (crawl budget, 4xx/5xx, bot behavior), no re-crawl after fixes. |
| 12 | **Competitor comparison depth** | `seo-compare` collects gaps manually — no methodology: keyword overlap, content-similarity scoring, SERP diff across geographies. |

---

## (c) Citable CLI examples

```bash
# 1) Robots.txt — RFC 9309 validation
curl -s https://lovii.ru/robots.txt | head -50

# 2) Sitemap — format check
curl -s https://lovii.ru/sitemap.xml | head -c 2000

# 3) Lighthouse / PSI — real Core Web Vitals (instead of a checklist)
npx lighthouse https://lovii.ru --only-categories=performance --output=json --output-path=out.json

# 4) JSON-LD — hard validation of required fields (e.g. Product)
python3 scripts/seo_toolkit.py --jsonld page.html

# 5) Keyword density (helper)
python3 scripts/seo_toolkit.py --density --file page.html --keyword "SEO audit"

# 6) Meta / headings / img audit (helper)
python3 scripts/seo_toolkit.py --meta page.html
```

---

## (d) Already adopted

1. **Meta audit** — title, description, canonical, OG, H1 hierarchy (single H1, ordering).
2. **Crawlability** — canonical, robots.txt, sitemap, redirect chains (`seo-crawl`).
3. **JSON-LD schema** — type reference (Product, Article, Organization, Breadcrumb, FAQ).
4. **Weighted scoring** — `seo-report` (7 dimensions, weighted, Lighthouse-like).
5. **P1–P5 prioritization** — fixes ranked by impact.
6. **Diff-before-apply** — safety for the fix agent.
7. **Dual URL/FS mode** — all commands work by URL or by files.
8. **Keywords** — density, cannibalization, LSI (basic).

---

## (e) Canonical analogue details (for deep enrichment)

### 1. Google Search Central — Search Essentials
- Technical SEO standard: crawlability (robots), indexability (noindex/canonical),
  healthy pages (no thin/duplicate, no intrusive interstitial), E-E-A-T signals.
- URL: https://developers.google.com/search/docs/essentials

### 2. Lighthouse / PageSpeed Insights
- Metrics: **LCP ≤ 2.5s**, **INP ≤ 200ms**, **CLS ≤ 0.1**.
- Canon for `seo-report`: scoring categories are not equal.
- URL: https://web.dev/vitals

### 3. Rich Results Test
- Types and requirements for rich results (Product/Review, Article+Author, FAQ,
  Breadcrumb, Video, Recipe, Event).
- Runs by URL or code snippet; the reference for markup validation.

### 4. sitemaps.org
- Format: `<urlset>`/`<sitemapindex>`, `<lastmod>`, `<changefreq>`, `<priority>`;
  limits — 50,000 URLs / 50 MB, UTF-8 encoding.

### 5. robots.txt RFC 9309
- Syntax: `User-agent:`, `Allow`/`Disallow` with `*` and `$`, `Sitemap:` in any
  section, rule ordering, file size limit, no `canonical` requirement in robots.

### 6. schema.org
- JSON-LD preferred; required properties per type
  (Product → name+offers; Article → headline, datePublished/dateModified, author;
  Organization → name+url/logo; FAQPage → mainEntity Question/Answer; BreadcrumbList → items).

### 7. Screaming Frog
- Patterns: full-site crawl, redirect chains, orphan discovery via link structure
  (requires link-graph input, not just checklists).

### 8. Ahrefs / Semrush
- Keyword cannibalization: multiple pages targeting one query (`site:` + exact match).
- Content gaps: against a competitor, accounting for SERP features and intent.

### 9. Google Search Console
- Index coverage checks, Page Experience, real Core Web Vitals data.
- The source of truth for on-site SEO decisions.

---

## Enrichment recommendations for the skill

1. `seo-speed` — collect real metrics (Lighthouse CLI/PSI API) instead of checklists.
2. `seo-crawl` — redo robots-rule validation per RFC 9309 (wildcards, `$`, `Sitemap:`, 64 KB limit).
3. `seo-schema` — a "required properties per type" table + a link to Rich Results Test.
4. `seo-content` — add an E-E-A-T checklist / YMYL.
5. `seo-compare` — formalize: keyword overlap + content overlap + SERP features.