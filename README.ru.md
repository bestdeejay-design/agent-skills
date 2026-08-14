<p align="center">
  <a href="https://github.com/bestdeejay-design" target="_blank">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/header-dark.svg">
      <img src="assets/header.svg" alt="Agent Skills — header" />
    </picture>
  </a>
</p>

# Agent Skills — Коллекция скиллов для AI-агентов

> Автономные инструкции (skills) для AI-агентов: Sisyphus, opencode, и совместимые. Каждый скилл — папка с `SKILL.md` (инструкция) и `skill.json` (манифест для установки/поиска).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills: 41](https://img.shields.io/badge/Skills-41-blue.svg)](index.json)
[![CI](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml)
[![Release](https://img.shields.io/github/v/release/bestdeejay-design/agent-skills?color=green)](https://github.com/bestdeejay-design/agent-skills/releases)
[![Updated](https://img.shields.io/badge/Updated-2026--08--14-green.svg)](index.json)
[![Community](https://img.shields.io/badge/Community%20Health-100%25-brightgreen.svg)](https://github.com/bestdeejay-design/agent-skills/community)
[![code: 14](https://img.shields.io/badge/code-14-2F81F7.svg)](README.md#cat-code) [![data: 6](https://img.shields.io/badge/data-6-E3B341.svg)](README.md#cat-data) [![media: 13](https://img.shields.io/badge/media-13-A371F7.svg)](README.md#cat-media) [![repository: 10](https://img.shields.io/badge/repository-10-3FB950.svg)](README.md#cat-repository) [![social: 1](https://img.shields.io/badge/social-1-F85149.svg)](README.md#cat-social)

**🌐 Versions:** [English](README.md) · [Русский](README.ru.md) · [Website](https://bestdeejay-design.github.io/agent-skills/)

<details>
<summary><b>📑 Оглавление</b></summary>

- [📦 Каталог скиллов](#sec-catalog) — 41 скилл · 5 категорий
- [🎬 Showcase](#sec-showcase) — примеры на реальных проектах
- [🚀 Установка](#sec-installation)
- [📁 Структура репозитория](#sec-structure)
- [🔍 Поиск скиллов](#sec-discovery)
- [🛠 Добавление нового скилла](#sec-adding)
- [📄 Информация о проекте](#sec-project-info) — лицензия · контрибьютинг · безопасность · кодекс

</details>

---

<a id="sec-catalog"></a>

## 📦 Каталог скиллов

> 📚 Карта экосистемы: см. [**docs/SKILLS_CATALOG.md**](docs/SKILLS_CATALOG.md) — каталог экосистемы AI agent skills (официальные вендоры, форматы, стандарты, ~4.85M файлов SKILL.md, пробелы и рекомендации).

**41 скилл · 5 категорий.** Выбери категорию ниже; триггеры и полные метаданные — в [`index.json`](index.json).

| Категория | Скиллов | Что входит |
|-----------|:-------:|------------|
| 💻 [Разработка и код](#cat-code) | 14 | коммиты, ревью, отладка, тесты, покрытие, безопасность, планирование, фронтенд |
| 📊 [Данные и диаграммы](#cat-data) | 6 | профилирование, SQL, диаграммы, скраппинг |
| 🎬 [Контент и медиа](#cat-media) | 13 | слайды, видео, PDF-отчёты, SEO, тестовая графика |
| 🏗️ [Репозиторий и документация](#cat-repository) | 10 | README, community-файлы, метаданные, документация, API-доки |
| 💬 [Соцсети](#cat-social) | 1 | Reddit |

<a id="cat-code"></a>

### 💻 Разработка и код · `code` · 14

| Скилл | Назначение |
|-------|------------|
| [**commit-message-writer**](skills/commit-message-writer/SKILL.md) | Генерация Conventional Commits-сообщения из `git diff --staged`: тип по файлам, scope по путям, описание и body. |
| [**commit-lint**](skills/commit-lint/SKILL.md) | Валидация commit-сообщений по Conventional Commits v1.0.0 (тип, scope, длины, регистр); отчёт text/JSON, exit 0/1/2. |
| [**version-bumper**](skills/version-bumper/SKILL.md) | Детерминированный семвер-бамп + релизный тег по git-истории (feat/fix/breaking); режим `-s`, read-only. |
| [**code-review**](skills/code-review/SKILL.md) | Структурированное ревью diff/репозитория: чек-листы по категориям (correctness, security, performance, style, tests, edge cases), замечания `[severity] файл:строка` с фиксами. Только анализ — правок не вносит. |
| [**systematic-debugger**](skills/systematic-debugger/SKILL.md) | Отладка по Iron Law: воспроизведение → гипотезы → корень → минимальный фикс + регресс-тест; Red Flags, отчёт по фазам. |
| [**test-generator**](skills/test-generator/SKILL.md) | pytest-скелеты из AST Python-модуля с ghostwriter-эвристикой аргументов; каркас parametrize, референсы TS/Go. |
| [**coverage-analyzer**](skills/coverage-analyzer/SKILL.md) | Анализ покрытия из coverage.py XML: общий % строк/веток, файлы без покрытия, худшие-10, дельта от базовой, гейт PASS/FAIL. |
| [**secret-scanner**](skills/secret-scanner/SKILL.md) | Поиск утечек секретов (AWS, GitHub, OpenAI, Anthropic, Stripe, Google, Slack, ключи, JWT): паттерны gitleaks + энтропия + allowlist; офлайн, редактирование, exit-коды для CI. |
| [**security-review**](skills/security-review/SKILL.md) | Оркестратор security-ревью: инвентаризация lockfile'ов + классификатор exit-кодов 13 сканеров (semgrep, bandit, gitleaks, osv-scanner, trivy, grype…) в единую схему находок; по OWASP. |
| [**plan-skill**](skills/plan-skill/SKILL.md) | Планирование реализации (superpowers v2): брейншторм → план → исполнение → проверка; HARD-GATE, мелкие шаги, без заглушек; скрипт-валидатор. |
| [**skill-suggester**](skills/skill-suggester/SKILL.md) | Подбор нужного скилла из библиотеки под задачу: скоринг триггеров/описаний в `index.json`, топ-5 + комбо до 3 скиллов. |
| [**api-contract-testing**](skills/api-contract-testing/SKILL.md) | Сверка контракта API с OpenAPI 3.x (офлайн по манифесту + живые HTTP-пробы); JSON-отчёт, exit 0/1/2. |
| [**frontend-perfection**](skills/frontend-perfection/SKILL.md) | Аудит и доводка фронтенда до проверяемого идеала: Lighthouse ≥13 в реальном Chrome (mobile+desktop), офлайн-аудит мета/SEO/WCAG/токенов, генерация OG-изображений. |

<a id="cat-data"></a>
| [**long-running-agent-workflow**](skills/long-running-agent-workflow/SKILL.md) | Протокол для AI-агентов в длинных сессиях: каталог `.lra/` со списком фич (id/приоритет/критерии приёмки/статус) и контрольные точки прогресса. |

### 📊 Данные и диаграммы · `data` · 6

| Скилл | Назначение |
|-------|------------|
| [**csv-pro**](skills/csv-pro/SKILL.md) | Профилирование CSV: типы колонок, статистика, аномалии (пустые/дубли/выбросы), автоопределение разделителя; markdown/JSON. |
| [**data-analysis**](skills/data-analysis/SKILL.md) | Профилирование датасета (CSV/JSON): статистика полей, моды, гистограммы, топ-3 корреляции Пирсона, аномалии и рекомендации. |
| [**sql-helper**](skills/sql-helper/SKILL.md) | Генерация SQL по текстовому вопросу и DDL: схема в памяти sqlite, шаблоны интентов, каждый запрос проверяется через EXPLAIN. |
| [**diagram-maker**](skills/diagram-maker/SKILL.md) | Диаграммы из текстового описания в синтаксисе Mermaid: flowchart, sequence, architecture, ER + рекомендация по рендеру. |
| [**mermaid-to-image**](skills/mermaid-to-image/SKILL.md) | Рендер `.mmd` в PNG/SVG: локальный mermaid-cli, fallback на mermaid.ink; форматы, масштаб, фон. |
| [**web-scraper**](skills/web-scraper/SKILL.md) | Вежливый скраппинг HTML в Markdown/JSON: CSS-селекторы, текст/ссылки/таблицы; легальные ограничители — robots.txt, честный UA, задержки. |

<a id="cat-media"></a>

### 🎬 Контент и медиа · `media` · 12

| Скилл | Назначение |
|-------|------------|
| [**video-script-writer**](skills/video-script-writer/SKILL.md) | Сценарий видео: Hook → Body (5 сцен с таймслотами) → CTA; таймкоды, ru/en, полный сценарий или план. |
| [**pdf-report-builder**](skills/pdf-report-builder/SKILL.md) | Markdown → PDF-отчёт: HTML через pandoc/встроенный конвертер, PDF через Chrome headless / weasyprint / pandoc; таблицы, код, цитаты. |
| [**test-graphics**](skills/test-graphics/SKILL.md) | Тестовые картинки, заглушки, иконки, аватары для моков/staging/e2e: Python + бесплатные API (loremflickr, placehold.co, picsum, Lucide). |
| [**frontend-design-taste**](skills/frontend-design-taste/SKILL.md) | Выразительное дизайн-направление без «AI-шаблонности»: погружение в тему, система токенов, гейт уникальности, копирайт под пользователя. |
| [**seo-audit**](skills/seo-audit/SKILL.md) | Технический SEO-аудит: мета/заголовки/alt/ссылки/sitemap/robots, Core Web Vitals, скоринг-отчёт (7 измерений), автофиксы P1–P5. |
| [**seo-schema**](skills/seo-schema/SKILL.md) | Разметка и мета: JSON-LD schema.org (Product/Article/Organization/Breadcrumb/FAQ) + title/description/OG/Twitter. |
| [**seo-content**](skills/seo-content/SKILL.md) | Контент страниц: тонкие/дубли, читаемость, E-E-A-T, ключевые слова (плотность, каннибализация, LSI, long-tail), иерархия заголовков, SEO картинок. |
| [**seo-crawl**](skills/seo-crawl/SKILL.md) | Индексация: robots.txt, noindex, canonical, редиректы, sitemap, перелинковка, глубина кликов, сироты, сравнение с конкурентами. |
| [**seo-toolkit**](skills/seo-toolkit/SKILL.md) | ⚠️ **Устарел (роутер)** → используй [seo-audit](skills/seo-audit/SKILL.md) / [seo-schema](skills/seo-schema/SKILL.md) / [seo-content](skills/seo-content/SKILL.md) / [seo-crawl](skills/seo-crawl/SKILL.md). |
| [**presentation-maker**](skills/presentation-maker/SKILL.md) | Презентации «под ключ» из темы: план → JSON-спека → HTML-слайды 16:9 (с обязательной проверкой Playwright) и настоящий `.pptx`; пресеты-стратегии, экспорт в PDF, аудит качества. Одна команда на этап. |
| [**presentation-craft**](skills/presentation-craft/SKILL.md) | Роутер качественных дек: оркестрирует docs-product → frontend-design-taste → presentation-maker → frontend-perfection по этапам (смысл, визуальное направление, сборка, аудит). |

<a id="cat-repository"></a>

### 🏗️ Репозиторий и документация · `repository` · 10

| Скилл | Назначение |
|-------|------------|
| [**repo-readme-assets**](skills/repo-readme-assets/SKILL.md) | README.md (EN) + локализованное зеркало + локальные анимированные SVG header/footer (4 пресета), без внешних сервисов. |
| [**repo-community-files**](skills/repo-community-files/SKILL.md) | Community/легальные файлы: LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, шаблоны issue/PR, FUNDING; поднимает Community Health. |
| [**repo-metadata-health**](skills/repo-metadata-health/SKILL.md) | Метаданные и здоровье репозитория: описание, topics (≤20), ссылка Pages, % Community Health через gh API + чек-лист из 16 пунктов. |
| [**repo-social-preview**](skills/repo-social-preview/SKILL.md) | Социальная превью GitHub (og:image) PNG 1280×640: шапка + волны, <1 МБ, рекомендуется сплошной фон. |
| [**api-doc-generator**](skills/api-doc-generator/SKILL.md) | Markdown-документация REST API из OpenAPI 3.x: секции по эндпоинтам (метод, параметры, запрос/ответ); референсы FastAPI/Express. |
| [**changelog-generator**](skills/changelog-generator/SKILL.md) | Раздел CHANGELOG (Keep a Changelog) из git-истории (Conventional Commits): tag..HEAD, маппинг типов, даты, ссылки на коммиты. |
| [**docs-system**](skills/docs-system/SKILL.md) | Мета-гайд + роутер документации: продуктовая ветка (зачем/что) vs проектная (как), фазы, уровни L1–L3, чек-лист полноты. |
| [**docs-product**](skills/docs-product/SKILL.md) | Продуктовая ветка — «зачем» и «что»: VISION → PRD → ROADMAP → FEATURES, от идеи вперёд; шаблоны + чек-лист. |
| [**docs-project**](skills/docs-project/SKILL.md) | Проектная ветка — «как»: README, ENTRY, ARCHITECTURE, ADR, контракты (OpenAPI/AsyncAPI), тесты, карта REFERENCE; шаблоны + чек-лист. |
| [**github-repo-hygiene**](skills/github-repo-hygiene/SKILL.md) | ⚠️ **Устарел (роутер)** → используй [repo-readme-assets](skills/repo-readme-assets/SKILL.md) / [repo-community-files](skills/repo-community-files/SKILL.md) / [repo-metadata-health](skills/repo-metadata-health/SKILL.md) / [repo-social-preview](skills/repo-social-preview/SKILL.md). |

<a id="cat-social"></a>

### 💬 Соцсети · `social` · 1

| Скилл | Назначение |
|-------|------------|
| [**reddit-karma**](skills/reddit-karma/SKILL.md) | Системный набор кармы на Reddit: поиск тем, ответы с учётом тона, шаблоны благодарностей, регулярные забеги; настраивается под аккаунт. |

<a id="sec-showcase"></a>

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

<a id="sec-installation"></a>

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

<a id="sec-structure"></a>

## 📁 Структура репозитория

```
agent-skills/
├── index.json                 # Мастер-каталог: name, version, category, description, triggers
├── README.md · README.ru.md   # Этот документ (EN / RU-зеркало)
├── CHANGELOG.md · LICENSE · CONTRIBUTING.md · SECURITY.md · SUPPORT.md · CODE_OF_CONDUCT.md · FUNDING.yml
├── og-image.png               # Социальная превью 1280×640
├── assets/                    # SVG header/footer для README
├── docs/
│   ├── SKILLS_CATALOG.md      # Каталог экосистемы AI agent skills
│   ├── showcase/              # Примеры на реальных проектах (+ шаблон)
│   └── plans/                 # Планировочные документы
├── .github/
│   ├── ISSUE_TEMPLATE/ · pull_request_template.md · release.yml
│   └── workflows/validate-skills.yml   # CI: валидация манифестов
└── skills/                    # 41 скилл, по папке на каждый
    └── <skill-name>/
        ├── SKILL.md           # Инструкция для агента (обязательно)
        ├── skill.json         # Манифест: name, version, triggers, files (обязательно)
        ├── scripts/           # Исполняемые скрипты (Python/JS)
        ├── templates/         # Шаблоны
        └── references/        # Дополнительные материалы
```

**Анатомия папки скилла** (пример — `code-review`):

```
skills/code-review/
├── SKILL.md              # Инструкция: введение → шаги → примеры → ограничения
├── skill.json            # Манифест: name, version, category, triggers, files
├── scripts/              # review.py, checklists.py
├── templates/            # review-template.md
└── examples/             # example-pr.md
```

> Обязательны только `SKILL.md` и `skill.json` — всё остальное опционально и зависит от скилла.

---

<a id="sec-discovery"></a>

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

<a id="sec-adding"></a>

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

<a id="sec-project-info"></a>

## 📄 Информация о проекте

| | |
|---|---|
| **Лицензия** | [MIT](LICENSE) |
| **Контрибьютинг** | [CONTRIBUTING.md](CONTRIBUTING.md) |
| **Безопасность** | [SECURITY.md](SECURITY.md) |
| **Кодекс поведения** | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Contributor Covenant 2.1 |

---

<p align="center">
  <a href="https://github.com/bestdeejay-design" target="_blank">
    <img src="assets/footer.svg" alt="footer" />
  </a>
</p>