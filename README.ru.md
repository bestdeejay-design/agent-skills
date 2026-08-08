# Agent Skills — Коллекция скиллов для AI-агентов

> Автономные инструкции (skills) для AI-агентов: Sisyphus, opencode, и совместимые. Каждый скилл — папка с `SKILL.md` (инструкция) и `skill.json` (манифест для установки/поиска).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills: 9](https://img.shields.io/badge/Skills-9-blue.svg)](index.json)
[![CI](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml)
[![Release](https://img.shields.io/github/v/release/bestdeejay-design/agent-skills?color=green)](https://github.com/bestdeejay-design/agent-skills/releases)
[![Updated](https://img.shields.io/badge/Updated-2026--08--08-green.svg)](index.json)
[![Community](https://img.shields.io/badge/Community%20Health-100%25-brightgreen.svg)](https://github.com/bestdeejay-design/agent-skills/community)

**🌐 Versions:** [English](README.md) · [Русский](README.ru.md) · [Website](https://bestdeejay-design.github.io/agent-skills/)

---

## 📦 Каталог скиллов

| Скилл | Категория | Описание | Триггеры |
|-------|-----------|----------|----------|
| [**github-repo-hygiene**](skills/github-repo-hygiene/SKILL.md) | `repository` | Проверка и обновление описательной части GitHub-репозитория: README (EN+RU), LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, issue/PR-шаблоны, социальное превью, релизы, description, topics, GitHub Pages, community health. | `github hygiene`, `оформить репозиторий`, `обновить readme`, `github page`, `описание репозитория`, `теги для поиска`, `topics`, `contributing`, `license`, `security policy` |
| [**test-graphics**](skills/test-graphics/SKILL.md) | `media` | Генерация тестовых изображений, фото, иконок, placeholders через Python + бесплатные API (loremflickr, placehold.co, picsum.dev, Lucide). | `test images`, `placeholder`, `тестовые картинки`, `иконки для теста`, `заглушки`, `mock data images`, `сгенерировать фото` |
| [**reddit-karma**](skills/reddit-karma/SKILL.md) | `social` | Систематическая работа на Reddit для набора кармы вашего аккаунта: поиск тем, подготовка ответов, распознавание тона, шаблоны благодарностей, регулярный забег. Настройте никнейм, сабы и целевой ресурс под себя. | `reddit`, `карма`, `karma`, `r/LocalLLaMA`, `поднять карму`, `ответить на комментарии`, `забег по reddit` |
| [**presentation-maker**](skills/presentation-maker/SKILL.md) | `media` | Генератор презентаций: Markdown-аутлайн, HTML 16:9 слайды, .pptx через python-pptx. Авто-лейауты, темы, дизайн-система (токены, mood), модуль «Продакт-дизайнер» (нарратив, дата-виз, a11y, премиум). | `сделай презентацию`, `presentation`, `слайды`, `pptx`, `сделай доклад`, `презентация для`, `generate slides`, `make a deck` |
| [**docs-system**](skills/docs-system/SKILL.md) | `repository` | Гайд для AI-агента: как правильно составлять продуктовую и проектную документацию и её состав. Продуктовая ветка (VISION/PRD/ROADMAP/FEATURES) и проектная ветка (ARCHITECTURE/ADR/контракты/TEST_CASES/карта REFERENCE), порядок заполнения (фазы), шаблоны, чек-лист полноты, уровни L1/L2/L3 для больших систем. | `документация`, `каталог документов`, `набор документации`, `полная документация`, `documentation`, `docs catalog`, `documentation structure`, `docs for new project` |
| [**commit-message-writer**](skills/commit-message-writer/SKILL.md) | `code` | Генерация Conventional Commits-сообщений на основе `git diff --staged`: тип по изменённым файлам, scope по путям, краткое описание, опциональный body. Скрипт `suggest.py` (Python 3) анализирует только застейдженные изменения, сам не коммитит. | `commit message`, `write commit`, `git commit`, `conventional commit`, `сообщение коммита`, `написать коммит`, `закоммитить` |
| [**code-review**](skills/code-review/SKILL.md) | `code` | Структурированный code review: читает git diff или путь к репозиторию/файлу, применяет чек-лист категорий (correctness, security, performance, style, tests, edge cases) и выдаёт замечания `[severity] файл:строка` с предлагаемым исправлением. Только анализ — правки не вносит. | `code review`, `ревью кода`, `review PR`, `проверь код`, `pull request review`, `code quality`, `найти баги`, `review commit` |
| [**diagram-maker**](skills/diagram-maker/SKILL.md) | `data` | Генерация диаграмм из текстового описания: flowchart, sequence, architecture, ER-схемы в синтаксисе Mermaid. Вход — описание на естественном языке, выход — код Mermaid + рекомендация по рендерингу (mermaid.live / mermaid-cli / MCP). | `диаграмма`, `diagram`, `mermaid`, `flowchart`, `блок-схема`, `sequence diagram`, `архитектура`, `ER-схема`, `draw a diagram` |
| [**skill-suggester**](skills/skill-suggester/SKILL.md) | `code` | Подбор скиллов из библиотеки под задачу пользователя: какой скилл использовать, что выбрать, рекомендовать скилл, подобрать инструмент. Читает index.json, скорит триггеры и описания, выдаёт топ-5 с релевантностью и комбо до 3 скиллов. | `какой скилл использовать`, `подбор скилла`, `suggest skill`, `reкомендовать скилл`, `какой навык`, `which skill` |

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
    │   └── skill.json
    ├── reddit-karma/
    │   ├── SKILL.md
    │   └── skill.json
    ├── presentation-maker/
    │   ├── SKILL.md
    │   ├── skill.json
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
    └── skill-suggester/
        ├── SKILL.md
        ├── skill.json
        └── scripts/skill_suggest.py
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