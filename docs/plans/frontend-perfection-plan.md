# Plan: frontend-perfection — скилл аудита и доводки фронтенда (Lighthouse + SEO + адаптив + дизайн-токены)

> Дата: 2026-08-09
> Статус: `approved`
> Bootstrap: рекомендация из lovii-сессии (тест built-in `frontend` скилла выявил 8 проблем, которые скилл должен решать с учётом)

## Goal

Создать 29-й скилл каталога `frontend-perfection`: реальный аудит фронтенда
(статические HTML/CSS/JS и сборки) через реальный Chrome + Lighthouse ≥13,
SEO-мета-слой, адаптив/контрасты, дизайн-токены. Основной драйвер — устранить
имеющиеся проблемы built-in `frontend` (приватные поля Playwright, API Lighthouse,
неизолированные зависимости) и довести lovii_demo до зелёных метрик.

**Acceptance criteria (проверяемо):**
- [ ] CR1: `python3 .github/workflows/validate_skills.py` → 29/29 OK
- [ ] CR2: `skills/frontend-perfection/` содержит `SKILL.md` + `skill.json` + `scripts/audit.js` + `scripts/meta_audit.py` + `references/canonical-patterns.md`
- [ ] CR3: `node --check scripts/audit.js` и `py_compile scripts/meta_audit.py` без ошибок
- [ ] CR4: оба скрипта проходят smoke-запуск на `lovii_demo/index.html` (реальные цифры в showcase)
- [ ] CR5: ROADMAP v1.6 чекбоксы, CHANGELOG [1.6.0], README/README.ru (badge 29, таблица, showcase)
- [ ] CR6: скилл синхронизирован в `~/.config/opencode/skills` (всего 29)

## Constraints

- **Раннер Lighthouse — на стабильном API**: `chrome-launcher` + Lighthouse Node API, НЕ приватные поля Playwright (`_impl_obj._connection._transport._ws_url`) — они ломаются (PipeTransport)
- **Lighthouse ≥ 13**: `require('lighthouse')` больше не функция — обязательный фолбэк `require('lighthouse').default`
- **Изоляция зависимостей**: скрипт сам резолвит `lighthouse`/`chrome-launcher` (локальный `node_modules` → `NODE_PATH` → глобальный npm prefix), не падает с `Cannot find module`
- Реальный Chrome (channel `chrome`), не headless-shell по умолчанию; mobile + desktop прогоны
- Python-часть (SEO/контрасты/токены) — чистый Python 3 stdlib, офлайн
- Категория скилла — `code`, автор `best`, license `MIT`
- Никаких правок в другие скиллы; `index.json` — только точечная вставка 29-й записи (форматирование 2/3/4-space не менять)
- Showcase на `lovii_demo` (`/Users/best/Projects/lovii_demo/index.html`)

## Steps

### Step 1: план-документ
- Files: `docs/plans/frontend-perfection-plan.md`
- Produces: этот файл
- Action: зафиксировать цель, критерии, констрейнты (проблемы 1-8 из lovii-сессии)
- Verification: документ входит в коммит
- [ ] done

### Step 2: audit.js (Lighthouse-раннер)
- Files: `skills/frontend-perfection/scripts/audit.js`
- Produces: прогон реального Chrome (mobile+desktop) → JSON-отчёт по категориям (performance, accessibility, best-practices, seo), баллы 0-100, audit-ids проблемных мест, exit 0 если порог достигнут, 1 если нет
- Consumes: `chrome-launcher`, `lighthouse` (Node API, `.default`-фолбэк), `--url`, `--mobile`, `--desktop`, `--threshold`, `--out`, `--no-headless`
- Action: резолюция модулей (local `node_modules` → `NODE_PATH` → `npm root -g`), launch Chrome, LH-прогон, компактный отчёт (только failed/score<1 audits с id), запись JSON
- Verification: `node scripts/audit.js --url http://localhost:<порт>/ --no-headless` на lovii_demo → баллы по 4 категориям
- [ ] done

### Step 3: meta_audit.py (SEO + адаптив + токены)
- Files: `skills/frontend-perfection/scripts/meta_audit.py`
- Produces: проверка статического файла → JSON/Markdown-отчёт:
  - SEO-мета: title (≤60), description (≤160), canonical, OG (1200×630), Twitter, JSON-LD, robots/sitemap
  - Контрасты WCAG: вычисление относительной яркости (не на глаз) для пар цветов из CSS
  - Порядок заголовков h1→h6, один h1
  - Дизайн-токены: raw-hex вне `:root`/tokens → нарушение (0 raw-hex вне токенов)
  - Адаптив-подсказки: fixed-хедер → `scroll-padding-top`, overflow на планшетных широтах (по media queries)
- Consumes: stdlib (`re`, `html.parser`, `json`, `argparse`, `pathlib`), `--html`, `--css`, `--out`, `--tokens-file`
- Action: парсинг HTML+CSS, вычисления, отчёт, exit 0/1
- Verification: `python3 scripts/meta_audit.py --html index.html --css css/*.css` на lovii_demo → отчёт с реальными нарушениями
- [ ] done

### Step 4: SKILL.md
- Files: `skills/frontend-perfection/SKILL.md`
- Produces: полная инструкция для агента (EN-primary, YAML-frontmatter `name`/`description`)
- Action: разделы When to use / Workflow (audit → фикс с audit-id → re-audit до 100) / OG-методология (безопасная зона 600-640px, reflow `void offsetHeight` перед screenshot, смена URL вместо перезаписи для сброса кеша соцсетей) / Дизайн-система на минималках (все hex в токены) / Constraints / Примеры команд
- Verification: frontmatter валиден, триггеры совпадают с skill.json
- [ ] done

### Step 5: skill.json
- Files: `skills/frontend-perfection/skill.json`
- Produces: манифест (name, version 1.0.0, description, author best, license MIT, keywords, triggers EN/RU, category code, entrypoint SKILL.md, files, requirements: node+chrome+lighthouse, updated 2026-08-09)
- Action: по схеме CONTRIBUTING, описание 1-2 предложения семантичных
- Verification: `python3 -m json.tool`
- [ ] done

### Step 6: canonical-patterns.md
- Files: `skills/frontend-perfection/references/canonical-patterns.md`
- Produces: 3-6 аналогов (Anthropic frontend-design, obra/superpowers perfection, lighthouse-канон, design-powers/personas, beui.dev) + техники, которых не хватает текущей реализации
- Action: собрать по каноническим источникам обеих веток (вёрстка + og/SEO)
- Verification: секция обогащения в SKILL.md ссылается на неё
- [ ] done

### Step 7: smoke на lovii_demo + showcase
- Files: `docs/showcase/showcase-frontend-perfection-lovii.md`
- Produces: демонстрация на реальном `lovii_demo/index.html` (вход/запуск/вывод/интерпретация)
- Action: поднять `python3 -m http.server` на lovii_demo, прогнать audit.js (mobile+desktop) и meta_audit.py, собрать реальные цифры + список найденных нарушений
- Verification: в showcase реальные баллы, не заглушки
- [ ] done

### Step 8: интеграция каталога
- Files: `index.json`, `README.md`, `README.ru.md`, `ROADMAP.md`, `CHANGELOG.md`
- Produces: 29-я запись в index.json (точечная вставка), version 1.6.0, badge Skills: 29, таблица каталога, showcase-строка, ROADMAP v1.6 `[x]` + релизная строка, CHANGELOG [1.6.0] - 2026-08-09
- Action: следовать паттерну v1.5 (точечная вставка скриптом, НЕ json.dump всего файла)
- Verification: `python3 .github/workflows/validate_skills.py` → 29/29, json.tool OK
- [ ] done

### Step 9: локальная установка
- Files: `~/.config/opencode/skills/frontend-perfection/`
- Produces: скилл доступен локально (всего 29)
- Action: копирование папки скилла
- Verification: `ls ~/.config/opencode/skills | wc -l` → 29
- [ ] done

### Step 10: коммит + push + hygiene
- Action: коммит (conventional, feat(skills): frontend-perfection, catalog 28->29), push в main после подтверждения пользователя, github-repo-hygiene чек-лист (README описание, topics, Pages, CI)
- Verification: push `main`, CI зелёный
- [ ] done