# Canonical patterns: seo-toolkit

> Эталонные источники и пробелы текущего скилла относительно канонов.
> Обработка результатов librarian-исследования (август 2026) — исходный
> скилл из открытого каталога skills.sh (13 slash-команд по SEO).

---

## (a) Named analogues

| # | Name | Owner | URL | Type |
|---|------|-------|-----|------|
| 1 | Google Search Central — Search Essentials (technical SEO) | Google | https://developers.google.com/search/docs/essentials | Официальная документация |
| 2 | Lighthouse / PageSpeed Insights | Google | https://developer.chrome.com/docs/lighthouse | Официальный инструмент + API |
| 3 | Google Rich Results Test | Google | https://search.google.com/test/rich-results | Официальный валидатор structured data |
| 4 | sitemaps.org protocol | sitemaps.org | https://www.sitemaps.org/protocol.html | Стандарт XML-sitemaps |
| 5 | robots.txt protocol (RFC 9309) | Google / IETF | https://www.rfc-editor.org/rfc/rfc9309 | Стандарт robots.txt |
| 6 | schema.org vocabulary | schema.org | https://schema.org/docs/documents.html | Стандарт разметки JSON-LD/microdata |
| 7 | Screaming Frog SEO Spider | Screaming Frog | https://www.screamingfrog.co.uk/seo-spider/ | Эталонный crawl-аудит |
| 8 | Ahrefs / Semrush | Ahrefs / Semrush | https://ahrefs.com/ , https://www.semrush.com | Коммерческие SEO-платформы |
| 9 | Google Search Console | Google | https://search.google.com/search-console | Официальный источник данных |
| 10 | Playwright Test | Microsoft | https://playwright.dev/docs/test-fixtures | Эталон dual-mode / fixtures |

---

## (b) Techniques the skill is MISSING

| # | Technique / Source | What is missing in current skill |
|---|--------------------|----------------------------------|
| 1 | **LCP/INP/CLS measurement** (Lighthouse) | Команды дают чек-листы, но нет инструкции прогнать Lighthouse/PSI и подставить реальные цифры (LCP ≤ 2.5 с, INP ≤ 200 ms, CLS ≤ 0.1). |
| 2 | **JSON-LD validation beyond syntax** (Rich Results Test) | `seo-schema` не проверяет обязательные поля типа, уникальность `@id`, вложенность, типы, дающие rich results (Product, Article, FAQ, Breadcrumb). |
| 3 | **hreflang / international SEO** | Нет команды для hreflang: `lang`/`hreflang` атрибуты, `x-default`, двунаправленные ссылки, canonical для языковых версий. |
| 4 | **robots.txt wildcard / size limits** | `seo-crawl` не проверяет: `*` и `$` в паттернах, лимит 500 КБ, порядок `Allow`/`Disallow`, директиву `Sitemap:`. |
| 5 | **sitemap index / lastmod** (sitemaps.org) | Нет проверки `<lastmod>`, `<sitemapindex>` при >50 000 URL, кодировки UTF-8, hreflang в sitemap. |
| 6 | **Pagination & crawl budget** (Google Search Central) | Нет анализа пагинации (rel=prev/next устарел), noindex для фильтров, параметров `?utm_`/`?gclid` (URL-условности). |
| 7 | **E-E-A-T / YMYL** (Google Search) | `seo-content` не оценивает авторство, about→контакты, даты обновления, принадлежность для YMYL-страниц. |
| 8 | **Internal linking depth** (Screaming Frog) | `seo-structure` описывает depth, но нет автоматического расчёта: орфан-страницы × число внутренних ссылок, redirect chains. |
| 9 | **Open Graph / Twitter validation** | `seo-meta` генерит title/description, но нет проверки og:image (размер), twitter:card, уникальности OG на страницах. |
| 10 | **Fix-agent regression check** | `seo-fix` не требует post-проверки: re-run `seo-audit` после применения diff. |
| 11 | **Server logs анализ** (Screaming Frog core) | Нет анализа server logs (crawl budget, 4xx/5xx, поведение ботов), нет повторного crawl после правок. |
| 12 | **Competitor comparison depth** | `seo-compare` собирает gaps вручную — нет методологии: keyword overlap, content-similarity scoring, SERP diff по регионам. |

---

## (c) Citable CLI examples

```bash
# 1) Robots.txt — валидация по RFC 9309
curl -s https://lovii.ru/robots.txt | head -50

# 2) Sitemap — проверка формата
curl -s https://lovii.ru/sitemap.xml | head -c 2000

# 3) Lighthouse / PSI — реальные Core Web Vitals (вместо чек-листа)
npx lighthouse https://lovii.ru --only-categories=performance --output=json --output-path=out.json

# 4) JSON-LD — твёрдая валидация обязательных полей (пример для Product)
python3 scripts/seo_toolkit.py --jsonld page.html

# 5) Keyword density (helper)
python3 scripts/seo_toolkit.py --density --file page.html --keyword "SEO audit"

# 6) Meta / headings / img audit (helper)
python3 scripts/seo_toolkit.py --meta page.html
```

---

## (d) Adopted already

1. **Meta-аудит** — title, description, canonical, OG, H1-иерархия (одна H1, порядок).
2. **Crawlability** — canonical, robots.txt, sitemap, redirect chains (`seo-crawl`).
3. **JSON-LD schema** — справочник типов (Product, Article, Organization, Breadcrumb, FAQ).
4. **Weighted scoring** — `seo-report` (7 измерений, весовые, как Lighthouse).
5. **P1–P5 приоритизация** — правки по импорту.
6. **Diff-before-apply** — safety для fix-агента.
7. **Dual URL/FS mode** — все команды работают по URL или по файлам.
8. **Keywords** — плотность, каннибализация, LSI (базово).

---

## (e) Canonical analogue details (for deep enrichment)

### 1. Google Search Central — Search Essentials
- Технический SEO-стандарт: crawlability (robots), indexability (noindex/canonical), здоровые страницы
  (без thin/duplicate, без intrusive interstitial), E-E-A-T-сигналы.
- URL: https://developers.google.com/search/docs/essentials

### 2. Lighthouse / PageSpeed Insights
- Метрики: **LCP ≤ 2.5 s**, **INP ≤ 200 ms**, **CLS ≤ 0.1**.
- Канон для `seo-report`: категории скоринга не равнозначны.
- URL: https://web.dev/vitals

### 3. Rich Results Test
- Типы и требования rich results (Product/Review, Article+Author, FAQ, Breadcrumb, Video, Recipe, Event).
- Запуск по URL или фрагменту кода; референс для валидации разметки.

### 4. sitemaps.org
- Формат: `<urlset>`/`<sitemapindex>`, `<lastmod>`, `<changefreq>`, `<priority>`; лимиты — 50 000 URL / 50 МБ, кодировка UTF-8.

### 5. robots.txt RFC 9309
- Синтаксис: `User-agent:`, `Allow`/`Disallow` с `*` и `$`, `Sitemap:` в любой секции, порядок правил,
  лимит размера файла, отсутствие требования `canonical` в robots.

### 6. schema.org
- JSON-LD предпочтителен; обязательные поля на тип
  (Product → name+offers; Article → headline, datePublished/dateModified, author;
  Organization → name+url/logo; FAQPage → mainEntity Question/Answer; BreadcrumbList → элементы).

### 7. Screaming Frog
- Паттерны: полный crawl сайта, redirect chains, обнаружение орфан-страниц по глубина ссылок
  (нужен вход в структуру линков, а не только чек-листы).

### 8. Ahrefs / Semrush
- Каннибализация ключей: несколько страниц на один запрос (`site:` + exact match).
- Content gaps: по конкуренту, с учётом SERP-фичи и насыщенности интента.

### 9. Google Search Console
- Проверка индексации (coverage), Page experience, Core Web Vitals в реальном данных выдает.
  VS источник реальных данных о сайтах площадок.

---

## Рекомендации для обогащения скилла

1. `seo-speed` — авто собирать реальные метрики (Lighthouse CLI/PSI API), а не только чек-лист.
2. `seo-crawl` — пересборка проверки robots-правил по RFC 9309 (wildcard, `$`, `Sitemap:`, лимит 64 КБ).
3. `seo-schema` — таблица «required fields per type» + ссылка на Rich Results Test.
4. `seo-content` — добавить E-E-A-T checklist / YMYL.
5. `seo-compare` — формализовать: keyword overlap + content overlap + SERP feature.