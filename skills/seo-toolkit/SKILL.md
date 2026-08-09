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

Загружай этот скилл, когда нужно выполнить **любую SEO-задачу**: технический аудит, анализ Core Web Vitals, проверку crawlability, валидацию schema.org, ключевые слова, meta-теги, контент, изображения, отчёты, сравнение с конкурентами или автономные исправления.

Скилл работает в **двух режимах**:
- **URL mode** — fetch внешнего сайта + `robots.txt` + `sitemap.xml` + ключевые страницы
- **File mode** — анализ локального проекта (`pages/`, `app/`, `public/`, конфиги фреймворка)

---

## Команды (13 slash-команд)

| Команда | Описание | Режим | Триггеры |
|---|---|---|---|
| [`seo-audit`](commands/seo-audit.md) | Полный технический аудит: meta, headings, alt, broken links, sitemap, robots.txt, canonical, URL structure | URL / File | `/seo-audit`, `seo audit`, `технический аудит` |
| [`seo-speed`](commands/seo-speed.md) | Core Web Vitals (LCP/CLS/INP), блокирующие ресурсы, неиспользуемый CSS/JS, кэширование | URL / File | `/seo-speed`, `core web vitals`, `скорость сайта` |
| [`seo-structure`](commands/seo-structure.md) | Внутренняя ссылка, глубина кликов, orphan pages, иерархия URL, breadcrumbs | URL / File | `/seo-structure`, `site structure`, `структура сайта` |
| [`seo-crawl`](commands/seo-crawl.md) | Crawlability: robots.txt, noindex, canonical, redirect chains, sitemap.xml | URL / File | `/seo-crawl`, `crawlability`, `роботы` |
| [`seo-schema`](commands/seo-schema.md) | JSON-LD schema.org: Product, Article, Organization, Breadcrumb, FAQ, валидация | URL / File | `/seo-schema`, `json-ld`, `schema org`, `микроразметка` |
| [`seo-keywords`](commands/seo-keywords.md) | Плотность ключей, канибализация, LSI, long-tail, intent mapping | URL / File | `/seo-keywords`, `keywords`, `ключевые слова` |
| [`seo-meta`](commands/seo-meta.md) | Генерация title/description: длины, уникальность, CTR, Open Graph, Twitter Cards | URL / File | `/seo-meta`, `meta tags`, `title description` |
| [`seo-headings`](commands/seo-headings.md) | Иерархия H1-H6, порядок, ключи в заголовках, доступность | URL / File | `/seo-headings`, `headings`, `h1 h2 h3` |
| [`seo-content`](commands/seo-content.md) | Thin content, дубликаты, читаемость (Flesch-Kincaid), E-E-A-T сигналы | URL / File | `/seo-content`, `content audit`, `контент аудит` |
| [`seo-images`](commands/seo-images.md) | Alt text, WebP/AVIF, lazy loading, размеры, srcset, lazy loading | URL / File | `/seo-images`, `image seo`, `изображения seo` |
| [`seo-report`](commands/seo-report.md) | Комплексный отчёт со скорингом (7 измерений, веса 100%), план действий по неделям | URL / File | `/seo-report`, `seo report`, `seo отчёт` |
| [`seo-compare`](commands/seo-compare.md) | Сравнение с конкурентом: gaps, overlapping keywords, content gaps | URL | `/seo-compare`, `competitor seo`, `сравнение seo` |
| [`seo-fix`](commands/seo-fix.md) | Автономный агент исправлений: P1-P5 приоритизация, diff-before-apply, safety rules | File | `/seo-fix`, `seo fix`, `автоисправление seo` |

---

## Режимы работы

### URL Mode (по умолчанию для внешних сайтов)
```
User: /seo-audit https://lovii.ru
Agent: fetch https://lovii.ru + robots.txt + sitemap.xml + ключевые внутренние страницы → аудит
```

### File Mode (для локальных проектов)
```
User: /seo-audit file:///path/to/project
Agent: анализ файлов pages/, app/, public/, конфиги next.config.js, astro.config.mjs, .htaccess
```

---

## Канонические паттерны (для разработки/обогащения)

Полный разбор — в `references/canonical-patterns.md`. Ключевые каноны:

- **Dual URL/FS mode** — каждая команда работает в обоих режимах: по URL (`https://...`) или по локальным файлам (`file:///path`), как test fixtures в Playwright
- **Weighted scoring** — 7 измерений с весами (seo-report): Meta 20%, Content 20%, Crawl 15%, Images 15%, Schema 10%, Perf 10%, Links 10% (модель Google Lighthouse)
- **P1–P5 prioritization** — автоисправления с приоритетами по влиянию (как security advisories)
- **Diff-before-apply** — обязательный показ diff перед применением правок (как GitHub PR review)
- **Safety rules** — никогда не менять URL, не удалять контент, не трогать логику без подтверждения

---

## Примеры использования

```bash
# Полный аудит lovii.ru
/seo-audit https://lovii.ru

# Core Web Vitals для локального Next.js проекта
/seo-speed file:///path/to/lovii_demo

# Schema.org валидация JSON-LD на странице
/seo-schema https://lovii.ru

# Ключевые слова + канибализация
/seo-keywords https://lovii.ru

# Комплексный отчёт с планом действий
/seo-report https://lovii.ru

# Сравнение с конкурентом
/seo-compare https://lovii.ru https://competitor.com

# Автономные исправления (только file mode)
/seo-fix file:///path/to/lovii_demo
```

---

## Canonical analogues

Полный разбор — в `references/canonical-patterns.md`. Ключевые каноны:

- **Google Lighthouse / PageSpeed Insights** — пороги Core Web Vitals (LCP ≤ 2.5s, CLS ≤ 0.1, INP ≤ 200ms), веса скоринга
- **Google Search Central / Search Console** — правила crawlability, sitemap.xml, robots.txt, canonical, rich snippets
- **schema.org** — словарь JSON-LD (Product, Article, Organization, Breadcrumb, FAQ) и обязательные поля
- **Playwright Test** — dual-mode fixtures: URL + файловая система
- **Screaming Frog / Ahrefs / Semrush** — паттерны crawl, детекция каннибализации ключей, content gaps
- **GitHub Security Advisories** — P1–P5 приоритизация и diff-before-apply safety

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