# seo-schema (RU)

> Русское описание скилла. Сам скилл (`SKILL.md`, `skill.json`) — на английском.

**Назначение:** слой разметки в SEO — структурированные данные (JSON-LD/schema.org:
Product, Article, Organization, Breadcrumb, FAQ) и meta-теги (title, description,
Open Graph, Twitter Cards).

**Скрипт** `scripts/seo_schema.py`:
- `--meta file.html` — title+длина, description, canonical, og:* , twitter:card,
  robots, порядок заголовков, отсутствующие alt;
- `--jsonld file.html` — извлечение и валидация блоков JSON-LD (@context schema.org,
  @type, обязательные поля по типу). Чистый Python stdlib.

**Команды** (в `commands/`): seo-schema, seo-meta.

**Не применять:** для тех-аудита/CWV/отчётов/фиксов — `seo-audit`; для контента/
ключей/заголовков/картинок — `seo-content`; для краулинга — `seo-crawl`.
