<p align="center">
  <a href="https://github.com/bestdeejay-design" target="_blank">
    <img src="assets/header.svg" alt="header" />
  </a>
</p>

# Agent Skills — Коллекция скиллов для AI-агентов

> Автономные инструкции (skills) для AI-агентов: Sisyphus, opencode, и совместимые. Каждый скилл — папка с `SKILL.md` (инструкция) и `skill.json` (манифест для установки/поиска).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills: 39](https://img.shields.io/badge/Skills-39-blue.svg)](index.json)
[![CI](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml)
[![Release](https://img.shields.io/github/v/release/bestdeejay-design/agent-skills?color=green)](https://github.com/bestdeejay-design/agent-skills/releases)
[![Updated](https://img.shields.io/badge/Updated-2026--08--12-green.svg)](index.json)
[![Community](https://img.shields.io/badge/Community%20Health-100%25-brightgreen.svg)](https://github.com/bestdeejay-design/agent-skills/community)

**🌐 Versions:** [English](README.md) · [Русский](README.ru.md) · [Website](https://bestdeejay-design.github.io/agent-skills/)

---

## 📦 Каталог скиллов

> 📚 Карта экосистемы: см. [**docs/SKILLS_CATALOG.md**](docs/SKILLS_CATALOG.md) — каталог экосистемы AI agent skills (официальные вендоры, форматы, стандарты, ~4.85M файлов SKILL.md, пробелы и рекомендации).

| Скилл | Категория | Описание | Триггеры |
|-------|-----------|----------|----------|
| [**github-repo-hygiene**](skills/github-repo-hygiene/SKILL.md) | `repository` | **УСТАРЕЛ** — роутер-скилл. Разбит на четыре фокусных скилла: repo-readme-assets, repo-community-files, repo-metadata-health, repo-social-preview. Загружай один из них напрямую. | `github hygiene`, `repo polish`, `github repo docs` |
| [**repo-readme-assets**](skills/repo-readme-assets/SKILL.md) | `repository` | создание и обновление `README.md` (английская версия) + локализованного | `readme header`, `animated svg`, `waving svg`, `svg banner`, `readme assets`, `readme visual`, `smil animation`, `repo header`, `readme footer`, `readme generator`, `update readme`, `readme badges` |
| [**repo-community-files**](skills/repo-community-files/SKILL.md) | `repository` | создание и сопровождение легальных/community-файлов репозитория: | `license file`, `code of conduct`, `contributing guide`, `security policy`, `support file`, `issue template`, `pr template`, `funding yml`, `community files`, `repo legal files`, `contributor covenant` |
| [**repo-metadata-health**](skills/repo-metadata-health/SKILL.md) | `repository` | аудит и обновление метаданных и community-здоровья репозитория на | `repo description`, `repo topics`, `github topics`, `github pages`, `community health`, `repo audit`, `repo metadata`, `repo checklist`, `health percentage`, `repo about` |
| [**repo-social-preview**](skills/repo-social-preview/SKILL.md) | `repository` | генерация кастомного social preview (og:image) репозитория — PNG | `social preview`, `og image`, `og:image`, `social share image`, `repo preview png`, `open graph image`, `github social preview` |
| [**test-graphics**](skills/test-graphics/SKILL.md) | `media` | Генерация тестовых изображений, фото, иконок, placeholders через Python + бесплатные API (loremflickr, placehold.co, picsum.dev, Lucide). | `test images`, `placeholder`, `тестовые картинки`, `иконки для теста`, `заглушки`, `mock data images`, `сгенерировать фото` |
| [**reddit-karma**](skills/reddit-karma/SKILL.md) | `social` | Систематическая работа на Reddit для набора кармы вашего аккаунта: поиск тем, подготовка ответов, распознавание тона, шаблоны благодарностей, регулярный забег. Настройте никнейм, сабы и целевой ресурс под себя. | `reddit`, `карма`, `karma`, `r/LocalLLaMA`, `поднять карму`, `ответить на комментарии`, `забег по reddit` |
| [**presentation-maker**](skills/presentation-maker/SKILL.md) | `media` | **УСТАРЕЛ** — роутер-скилл. Разбит на три фокусных: deck-outline, deck-html, deck-pptx. Загружай один из них напрямую. | `сделай презентацию`, `presentation`, `слайды`, `pptx`, `сделай доклад` |
| [**deck-outline**](skills/deck-outline/SKILL.md) | `media` | Построение структуры презентации из темы: параметры, контент-рулы (без эмодзи/URL, только SVG-иконки), маппинг контента в лейауты, автовыбор. Выход: outline.md + JSON-спека для deck-html и deck-pptx. | `структура слайдов`, `аутлайн презентации`, `раскадровка`, `outline slides`, `deck outline`, `план презентации` |
| [**deck-html**](skills/deck-html/SKILL.md) | `media` | Сборка автономных HTML-слайдов 16:9 из JSON-спеки: тема + палитра, build_html.py (копирует шаблон, инжектит палитру в :root), обязательный гейт verify_slides.py (Playwright) + визуальный контроль + продакт-дизайн-ревью. | `сделай слайды`, `слайды html`, `html slides`, `16:9 слайды`, `build slides`, `сверстать презентацию` |
| [**deck-pptx**](skills/deck-pptx/SKILL.md) | `media` | Сборка настоящего PowerPoint (.pptx) из JSON-спеки через python-pptx: textbox, TrueTable, CategoryChartData-графики, фоны по палитре. | `сделай pptx`, `pptx`, `powerpoint`, `собрать pptx`, `build pptx`, `отдать в pptx` |
| [**docs-system**](skills/docs-system/SKILL.md) | `repository` | **Мета-гайд + роутер** документации: две ветки (docs-product «зачем/что», docs-project «как»), порядок фаз, уровни L1/L2/L3, чек-лист полноты. Для фокусной работы загружай ветку напрямую. | `документация`, `набор документации`, `docs catalog`, `documentation structure`, `какую документацию писать` |
| [**docs-product**](skills/docs-product/SKILL.md) | `repository` | Продуктовая ветка документации — «зачем» и «что»: VISION → PRD → ROADMAP → FEATURES. Пишется от идеи вперёд, до инженерной ветки. Шаблоны и чек-лист в комплекте. | `продуктовая документация`, `vision`, `prd`, `роадмап`, `roadmap`, `product docs`, `требования к продукту` |
| [**docs-project**](skills/docs-project/SKILL.md) | `repository` | Проектная (инженерная) ветка документации — «как»: README, ENTRY, ARCHITECTURE, ADR, контракты (OpenAPI/AsyncAPI до кода), тесты, карта REFERENCE. Шаблоны и чек-лист в комплекте. | `проектная документация`, `архитектура документация`, `adr`, `engineering docs`, `контракты openapi`, `project docs` |
| [**commit-message-writer**](skills/commit-message-writer/SKILL.md) | `code` | Генерация Conventional Commits-сообщений на основе `git diff --staged`: тип по изменённым файлам, scope по путям, краткое описание, опциональный body. Скрипт `suggest.py` (Python 3) анализирует только застейдженные изменения, сам не коммитит. | `commit message`, `write commit`, `git commit`, `conventional commit`, `сообщение коммита`, `написать коммит`, `закоммитить` |
| [**code-review**](skills/code-review/SKILL.md) | `code` | Структурированный code review: читает git diff или путь к репозиторию/файлу, применяет чек-лист категорий (correctness, security, performance, style, tests, edge cases) и выдаёт замечания `[severity] файл:строка` с предлагаемым исправлением. Только анализ — правки не вносит. | `code review`, `ревью кода`, `review PR`, `проверь код`, `pull request review`, `code quality`, `найти баги`, `review commit` |
| [**diagram-maker**](skills/diagram-maker/SKILL.md) | `data` | Генерация диаграмм из текстового описания: flowchart, sequence, architecture, ER-схемы в синтаксисе Mermaid. Вход — описание на естественном языке, выход — код Mermaid + рекомендация по рендерингу (mermaid.live / mermaid-cli / MCP). | `диаграмма`, `diagram`, `mermaid`, `flowchart`, `блок-схема`, `sequence diagram`, `архитектура`, `ER-схема`, `draw a diagram` |
| [**mermaid-to-image**](skills/mermaid-to-image/SKILL.md) | `data` | Рендер Mermaid-диаграмм (.mmd) в PNG/SVG: приоритет локальному mmdc (mermaid-cli), fallback на API mermaid.ink; форматы svg/png, фон, масштаб, движок auto/mmdc/ink, файл или stdin. | `mermaid в картинку`, `отрендерить диаграмму`, `render diagram`, `диаграмма в svg`, `mermaid to image` |
| [**pdf-report-builder**](skills/pdf-report-builder/SKILL.md) | `media` | Сборка PDF-отчётов из Markdown: HTML через pandoc (или встроенный конвертер), PDF первым доступным движком — Chrome/Chromium headless, weasyprint или pandoc + PDF-движок. Таблицы/код/цитаты. | `отчёт в pdf`, `markdown в pdf`, `собери отчёт`, `pdf report`, `document to pdf` |
| [**skill-suggester**](skills/skill-suggester/SKILL.md) | `code` | Подбор скиллов из библиотеки под задачу пользователя: какой скилл использовать, что выбрать, рекомендовать скилл, подобрать инструмент. Читает index.json, скорит триггеры и описания, выдаёт топ-5 с релевантностью и комбо до 3 скиллов. | `какой скилл использовать`, `подбор скилла`, `suggest skill`, `reкомендовать скилл`, `какой навык`, `which skill` |
| [**api-doc-generator**](skills/api-doc-generator/SKILL.md) | `repository` | Генерация Markdown-документации REST API из OpenAPI-схемы (3.x, включая 3.1.0): секции на каждый endpoint с методом, path, параметрами, телом запроса и кодами ответов. FastAPI: `app.openapi()`; Express: swagger-jsdoc. | `api doc`, `документация API`, `openapi`, `swagger в markdown`, `api reference`, `описать API` |
| [**changelog-generator**](skills/changelog-generator/SKILL.md) | `repository` | Генерация раздела CHANGELOG (Keep a Changelog) из git-истории по Conventional Commits: git log tag..HEAD, маппинг типов feat→Added/fix→Fixed/perf→Changed, breaking — в отдельную секцию. Python 3 stdlib. | `changelog`, `сгенерай чанжлог`, `release notes`, `история изменений`, `keep a changelog` |
| [**plan-skill**](skills/plan-skill/SKILL.md) | `code` | Планирование реализации по superpowers v2: brainstorm → writing-plans → executing → verification; HARD-GATE, bite-sized шаги, no placeholders, интерфейсы Produces/Consumes. Скрипт `plan_validator.py` проверяет план на готовность к исполнению. | `спланируй`, `составь план`, `plan`, `как реализовать`, `разбей на шаги`, `план реализации` |
| [**systematic-debugger**](skills/systematic-debugger/SKILL.md) | `code` | Отладка по Iron Law: 4 фазы (воспроизведение → гипотезы → изоляция причины → фикс + регресс-тест), Red Flags, Rationalization Table. Скилл фиксирует причину, не автофиксит. Скрипт `debug_log.py` оформляет отчёт по фазам. | `debug`, `отладить`, `почему не работает`, `баг`, `debugging`, `fix the bug` |
| [**test-generator**](skills/test-generator/SKILL.md) | `code` | Генерация pytest-скелетов из Python-модуля по AST с ghostwriter-эвристикой значений аргументов (bool→True/False, int→0/-1/1, str→sample/пустая, list/dict→пустые, Optional→None): `@pytest.mark.parametrize`. Референс TS/Go. | `generate tests`, `сгенерируй тесты`, `test skeleton`, `pytest скелет`, `покрытие тестами` |
| [**video-script-writer**](skills/video-script-writer/SKILL.md) | `media` | Генерация структурированных видео-сценариев из темы: Hook → Body (5 сцен: Problem/Basics/Walkthrough/Pitfalls/Pro tip) → CTA, таблица таймкодов, ru/en, свой CTA, полный сценарий или аутлайн. | `сценарий видео`, `video script`, `напиши сценарий`, `план видео`, `video outline` |
| [**sql-helper**](skills/sql-helper/SKILL.md) | `data` | Генерация SQL по текстовому вопросу и DDL-схеме: in-memory схема в sqlite3 из DDL, слова вопроса маппятся на таблицы/колонки, шаблоны интентов (select/join/where/group/order/count/limit), каждый кандидат проверяется через EXPLAIN, читаемый план с `--explain`. | `sql helper`, `sql генерация`, `сгенерируй sql`, `explain запроса`, `sql formatting` |
| [**csv-pro**](skills/csv-pro/SKILL.md) | `data` | Профилирование CSV-файлов: типы колонок, min/max/mean, пропуски, уникальные, топ-3 частых; аномалии (нулевая дисперсия, >95% пустых, дубликаты строк, строки >1000 символов, выбросы ≥5×IQR); markdown или JSON, определение разделителя, файл или stdin. | `csv profile`, `профиль csv`, `анализ csv`, `аномалии csv`, `csv anomalies` |
| [**web-scraper**](skills/web-scraper/SKILL.md) | `data` | Вежливый скраппинг HTML в Markdown/JSON: простой CSS-селектор (tag/tag#id/tag.class), извлечение текста/ссылок/таблиц; легальные guardrails — проверка robots.txt, честный User-Agent, задержка запросов, лимит 10 МБ. | `web scraping`, `скраппинг`, `скачать данные с сайта`, `парсинг сайта`, `scrape` |
| [**data-analysis**](skills/data-analysis/SKILL.md) | `data` | Профилирование датасетов (CSV или JSON-массив): типы полей, count/unique/missing, min/max/mean/std, мода + топ-N, гистограмма 5 корзин, топ-3 корреляции Пирсона, аномалии, рекомендации; markdown или JSON отчёт. | `data analysis`, `анализ данных`, `профиль датасета`, `статистика данных`, `eda` |
| [**seo-toolkit**](skills/seo-toolkit/SKILL.md) | `media` | 13 SEO-команд для AI-агентов: технический аудит, Core Web Vitals, crawlability, schema.org, ключевые слова, meta-теги, контент-анализ, изображения, отчёты, сравнение с конкурентами, автономные исправления. URL-режим + файловый режим. Скиптер `seo_toolkit.py`: аудит meta/заголовков/alt, плотность ключей, валидация JSON-LD. | `seo audit`, `core web vitals`, `schema org`, `json-ld`, `keywords analysis`, `seo report`, `meta tags`, `crawlability` |
| [**secret-scanner**](skills/secret-scanner/SKILL.md) | `code` | Сканирование кода и git-репозиториев на утечки секретов и токенов (AWS, GitHub, OpenAI, Anthropic, Stripe, Google, Slack, приватные ключи, JWT) по паттернам gitleaks v8.30.1 + энтропийный фильтр Шеннона + allowlist шума. Чистый Python 3 stdlib, офлайн, отчёты JSON/Markdown/text, редактирование секретов, CI-шлюз. | `secret scan`, `проверь секреты`, `leaked token`, `scan for keys`, `hardcoded credentials` |
| [**security-review**](skills/security-review/SKILL.md) | `code` | Оркестрация security-ревью зависимостей и кода: инвентаризация lockfiles (npm/pip/cargo/go/gem/maven/gradle/composer), классификатор exit-кодов 13 инструментов (semgrep, bandit, gitleaks, osv-scanner, pip-audit, trufflehog, checkov, trivy, grype, npm audit, cargo audit), нормализация JSON-отчётов в единую схему. Офлайн, stdlib. | `security review`, `audit dependencies`, `lockfile audit`, `проверь зависимости`, `уязвимости`, `osv-scanner` |
| [**version-bumper**](skills/version-bumper/SKILL.md) | `code` | Детерминированный bump семвер-версии по git-истории: читает теги (fallback `0.0.0`), считает feat/fix/breaking-коммиты в Conventional Commits, предлагает bump (major/minor/patch) + release-тег, режим `-s`. Офлайн, stdlib, read-only. Замыкает `commit-message-writer`/`changelog-generator`. | `version bump`, `next version`, `semver`, `release tag`, `какая следующая версия`, `определи версию` |
| [**commit-lint**](skills/commit-lint/SKILL.md) | `code` | Валидация git-коммитов по Conventional Commits v1.0.0: читает `git log` (или stdin), парсит type/scope/subject, сообщает нарушения (missing/invalid type, регистр, длина subject/header/body, точка в конце), отчёт text/JSON, exit 0/1/2. Офлайн, stdlib, read-only. Локальный аналог commitlint. | `commit lint`, `lint commits`, `conventional commits`, `check commit messages`, `проверка коммитов`, `валидация коммитов`, `commit style check` |
| [**coverage-analyzer**](skills/coverage-analyzer/SKILL.md) | `code` | Анализ покрытия кода тестами из coverage.py отчётов (XML/JSON): statement/line/branch coverage, разбивка по файлам с проблемными (ниже порогов), итоговый процент, рекомендации. Офлайн, stdlib. Пара к `test-generator`. | `coverage`, `coverage analysis`, `coverage report`, `test coverage`, `покрытие кода`, `анализ покрытия`, `branch coverage` |
| [**api-contract-testing**](skills/api-contract-testing/SKILL.md) | `code` | Проверка контракта API против OpenAPI 3.x (JSON/YAML, встроенный YAML-парсер, без PyYAML): перечисляет операции (paths + webhooks), проверяет внутреннюю консистентность ($ref, дубликаты, отсутствующие responses), сверяет manifest эндпоинтов офлайн, в live-режиме шлёт HTTP-запросы и сравнивает статусы. JSON-отчёт, exit 0/1/2. Офлайн, stdlib. | `api contract testing`, `contract test`, `validate openapi spec`, `spec vs manifest`, `endpoint coverage`, `проверь контракт API`, `тест контракта` |
| [**frontend-perfection**](skills/frontend-perfection/SKILL.md) | `code` | Аудит и доводка фронтенда до проверяемого идеала: реальный Chrome через chrome-launcher + Lighthouse ≥13 Node API (mobile+desktop, без Playwright-интерналов, с `.default`-фолбэком и авто-резолюцией зависимостей, exit 0/1/2, компактный JSON с failed audit-id); офлайн Python-stdlib аудит статики (SEO-мета-слой, контрасты WCAG по вычисленной яркости, порядок заголовков, дизайн-токены — ноль raw-hex вне токенов, scroll-padding под fixed-хедер, брейкпоинты); генерация crop-safe OG-изображений (1200×630 с центральной безопасной зоной ~640px, смена имени вместо перезаписи для сброса кеша соцсетей, принудительный reflow перед скриншотом). Каждый фикс привязывается к audit-id. | `frontend audit`, `lighthouse check`, `make it 100/100/100/100`, `perfect the layout`, `og image`, `contrast check`, `design tokens`, `проверь вёрстку`, `довести фронтенд до идеала` |
| [**frontend-design-taste**](skills/frontend-design-taste/SKILL.md) | `media` | Задать сайту осмысленное дизайн-направление, которое не читается как шаблонный AI: погружение в тему, токен-система (палитра/типографика/лейаут/сигнатура), гейт уникальности против трёх AI-дефолтов, копирайт со стороны пользователя. Метод на основе официального скилла Anthropic, пример ishotgirls. | `design direction`, `design taste`, `make it look good`, `redesign with taste`, `visual identity` |

## 🎬 Showcase — примеры на реальных проектах

> Живые демонстрации скиллов на **реальных** проектах (не абстрактные примеры).
> Эталон: **lovii.ru** (`lovii_demo`). Требование к new скиллов — обязательный
> showcase. Шаблон: [`docs/showcase-template.md`](docs/showcase-template.md).

| Скилл | Проект | Что показано |
|---|---|---|
| [`web-scraper`](docs/showcase/showcase-web-scraper-lovii.md) | lovii.ru (лендинг White Paper) | Скраппинг публичной страницы → Markdown-сводка (разделы, метрики, контакты, таблица) |
| [`diagram-maker`](docs/showcase/showcase-diagram-maker-lovii.md) | lovii_demo `docs/ARCHITECTURE.md` | Текстовая архитектура SPA → Mermaid flowchart структуры экранов по ролям |
| [`github-repo-hygiene`](docs/showcase/showcase-github-repo-hygiene-lovii.md) | lovii_demo репозиторий | Аудит Community Health (0% → 100%): отсутствующие файлы, метаданные, API-чеклисты |
| [`test-graphics`](docs/showcase/showcase-test-graphics-lovii.md) | lovii_demo мок-данные + бренд | Аватары партнёров, placeholder-ы товаров, иконки Lucide, batch для e2e |
| [`seo-toolkit`](docs/showcase/showcase-seo-toolkit-lovii.md) | lovii.ru (лендинг White Paper) | SEO-аудит публичной страницы: meta/OG/заголовки/alt через helper + Core Web Vitals + пробелы JSON-LD |
| [`secret-scanner`](docs/showcase/showcase-secret-scanner-lovii.md) | lovii_demo репо | Скан репозитория: 1 Medium (generic-api-key, UUID false positive, `index.js:7`) — энтропия + allowlist |
| [`security-review`](docs/showcase/showcase-security-review-lovii.md) | lovii_demo репо | Инвентаризация lockfiles (npm `package-lock.json` в `.opencode/`), классификация exit-кодов (osv-scanner 129 = API-ошибка, semgrep 1 = находки) |
| [`version-bumper`](docs/showcase/showcase-version-bumper-lovii.md) | agent-skills + lovii_demo | Следующая semver-версия по git-истории: agent-skills `v1.0.0` → `v1.1.0` (minor), lovii_demo fallback `0.0.0` → `v0.1.0` |
| [`commit-lint`](docs/showcase/showcase-commit-lint-lovii.md) | agent-skills + lovii_demo | Валидация Conventional Commits: 12/12 agent-skills (длинные subject + тип `i18n`), lovii_demo — классы type-case и missing-type |
| [`coverage-analyzer`](docs/showcase/showcase-coverage-analyzer-lovii.md) | agent-skills | Отчёт покрытия из coverage.py XML: statements/line/branch, файлы ниже порога, итоговый процент |
| [`frontend-perfection`](docs/showcase/showcase-frontend-perfection-lovii.md) | lovii_demo | Реальный Chrome-Lighthouse по форм-факторам (mobile 94/96/100/91, desktop 72/96/100/91) + офлайн meta-аудит (17 проверок, 12 нарушений: мета-слой, токены, контраст, scroll-padding) |

---

## 🚀 Установка

### Для opencode

Скопируйте нужную папку скилла в `~/.config/opencode/skills/`:

```bash
# Пример: установка presentation-maker
cp -r skills/presentation-maker ~/.config/opencode/skills/
```

Или загрузите напрямую через skill tool, указав путь к `SKILL.md`:

```bash
# В сессии opencode
skill load path/to/skills/presentation-maker/SKILL.md
```

### Для Sisyphus / других агентов

Каждый скилл содержит:
- `SKILL.md` — полная инструкция (Markdown)
- `skill.json` — манифест с метаданными (name, version, triggers, requirements, files)

Агент может парсить `index.json` для поиска скиллов по триггерам/категориям и загружать нужный.

---

## 📁 Структура репозитория

```
agent-skills/
├── index.json                 # Манифест репозитория (поиск/каталог)
├── README.md                  # Этот файл (английский)
├── README.ru.md               # Русское зеркало
├── CHANGELOG.md               # Keep a Changelog
├── LICENSE                    # MIT License
├── CONTRIBUTING.md            # Как добавить/обновить скиллы
├── SECURITY.md                # Политика безопасности
├── SUPPORT.md                 # Где получить помощь
├── CODE_OF_CONDUCT.md         # Contributor Covenant 2.1
├── FUNDING.yml                # Кнопка Sponsor
├── og-image.png               # Социальное превью (1280x640)
├── docs/
│   └── SKILLS_CATALOG.md      # Каталог экосистемы (вендоры, форматы, пробелы)
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml     # Форма issue (баг)
│   │   └── feature_request.yml # Форма issue (фича)
│   ├── pull_request_template.md
│   ├── release.yml            # Конфиг авто-релиз-нот
│   └── workflows/
│       └── validate-skills.yml # CI: JSON schema, cross-check, Python syntax
└── skills/
    ├── github-repo-hygiene/
    │   ├── SKILL.md
    │   └── skill.json
    ├── test-graphics/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/test-graphics.py
    ├── reddit-karma/
    │   ├── SKILL.md
    │   └── skill.json
    ├── presentation-maker/
    │   ├── SKILL.md
    │   ├── skill.json
    │   ├── references/
    │   │   ├── design-system.md
    │   │   └── product-designer.md
    │   ├── scripts/
    │   │   ├── build_html.py
    │   │   ├── build_pptx.py
    │   │   └── verify_slides.py
    │   ├── templates/
    │   │   ├── slides.html
    │   │   ├── themes/*.json
    │   │   └── icons/*.svg
    └── docs-system/
        ├── SKILL.md
        ├── skill.json
        ├── ROADMAP.md
        ├── references/
        │   ├── product-docs.md
        │   ├── project-docs.md
        │   ├── order.md
        │   ├── completeness.md
        │   └── levels.md
        ├── templates/
        │   ├── product/   (VISION.tmpl, PRD.tmpl, ROADMAP.tmpl)
        │   └── project/   (14 *.tmpl)
        └── examples/example-monorepo/README.md
    ├── commit-message-writer/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/suggest.py
    ├── code-review/
    │   ├── SKILL.md
    │   ├── skill.json
    │   ├── scripts/
    │   │   ├── review.py
    │   │   └── checklists.py
    │   ├── templates/review-template.md
    │   └── examples/example-pr.md
    ├── diagram-maker/
    │   ├── SKILL.md
    │   ├── skill.json
    │   ├── scripts/mermaid_to_markdown.py
    │   ├── templates/ (flowchart.mmd, sequence.mmd, architecture.mmd, er.mmd)
    │   └── examples/ (example-cart-flow.mmd, example-billing-seq.mmd)
    ├── mermaid-to-image/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/mermaid_to_image.py
    ├── pdf-report-builder/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/pdf_report_builder.py
    └── skill-suggester/
        ├── SKILL.md
        ├── skill.json
        └── scripts/skill_suggest.py
    ├── api-doc-generator/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/api_doc.py
    ├── changelog-generator/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/changelog_gen.py
    ├── plan-skill/
    │   ├── SKILL.md
    │   ├── skill.json
    │   ├── scripts/plan_validator.py
    │   ├── templates/implementation-plan.md
    │   └── examples/implementation-plan-example.md
    ├── systematic-debugger/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/debug_log.py
    ├── test-generator/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/test_gen.py
    └── video-script-writer/
        ├── SKILL.md
        ├── skill.json
        └── scripts/video_script_writer.py
    ├── sql-helper/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/sql_helper.py
    ├── csv-pro/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/csv_pro.py
    ├── data-analysis/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/data_analyze.py
    ├── web-scraper/
    │   ├── SKILL.md
    │   ├── skill.json
    │   └── scripts/scrape.py
    ├── seo-toolkit/
    │   ├── SKILL.md
    │   ├── skill.json
    │   ├── references/canonical-patterns.md
    │   ├── scripts/seo_toolkit.py
    │   └── commands/ (13 × seo-*.md)
    └── frontend-perfection/
        ├── SKILL.md
        ├── skill.json
        ├── references/canonical-patterns.md
        ├── scripts/audit.js
        └── scripts/meta_audit.py
```

---

## 🔍 Поиск скиллов

Используйте `index.json` — он содержит массив `skills` с полями:
- `name`, `version`, `category`, `description`, `path`, `triggers`, `updated`

Пример фильтрации по триггеру (Python):
```python
import json
with open('index.json') as f:
    data = json.load(f)
# Найти скиллы по триггеру "presentation"
matches = [s for s in data['skills'] if 'presentation' in ' '.join(s['triggers'])]
```

---

## 🛠 Добавление нового скилла

1. Создайте папку в `skills/<name>/`
2. Добавьте два обязательных файла:
   - `SKILL.md` — полная инструкция для агента (на английском — основной язык, русский по желанию; с YAML-фронтматтером `name`, `description`)
   - `skill.json` — манифест (см. схему ниже)
3. При необходимости добавьте скрипты/шаблоны в подпапки (`scripts/`, `templates/`, `icons/`)
4. Обновите `index.json` (добавьте запись в массив `skills[]`)
5. Создайте PR

### Схема `skill.json` (обязательные поля)

```json
{
  "name": "kebab-case-name",
  "version": "1.0.0",
  "description": "Краткое описание (1-2 предложения)",
  "author": "github-username",
  "license": "MIT",
  "keywords": ["tag1", "tag2"],
  "triggers": ["trigger phrase 1", "триггер на русском"],
  "category": "repository|media|social|code|data",
  "entrypoint": "SKILL.md",
  "files": ["SKILL.md", "scripts/*.py"],
  "requirements": {
    "tools": ["python3", "gh"],
    "permissions": ["repo:read"]
  },
  "updated": "YYYY-MM-DD"
}
```

**Категории**: `repository`, `media`, `social`, `code`, `data`

**Триггеры**: фразы, по которым агент должен загрузить скилл. Укажите на английском (основной), русский — по желанию.

### Требования к `SKILL.md`

- Язык: **английский** (основной, инструкции для агента); русский — по желанию
- Обязательный YAML-фронтматтер:
  ```yaml
  ---
  name: skill-name
  description: "Описание для каталога/поиска"
  ---
  ```
- Структура: введение → параметры/шаги → примеры → ограничения/ноу-хау
- Без эмодзи в качестве иконок (только SVG)
- Конкретные команды, пути, примеры вызовов

### Проверка перед PR

```bash
# Валидация JSON
python3 -m json.tool index.json >/dev/null
python3 -m json.tool skills/<name>/skill.json >/dev/null

# Проверка наличия файлов
ls skills/<name>/SKILL.md skills/<name>/skill.json
```

---

## 📄 Лицензия

MIT License — см. [LICENSE](LICENSE).

---

## 🤝 Контрибьютинг

См. [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 🔒 Безопасность

См. [SECURITY.md](SECURITY.md).

---

## 📜 Кодекс поведения

См. [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) (Contributor Covenant 2.1).

---

<p align="center">
  <a href="https://github.com/bestdeejay-design" target="_blank">
    <img src="assets/footer.svg" alt="footer" />
  </a>
</p>