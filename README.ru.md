# Agent Skills — Коллекция скиллов для AI-агентов

> Автономные инструкции (skills) для AI-агентов: Sisyphus, opencode, и совместимые. Каждый скилл — папка с `SKILL.md` (инструкция) и `skill.json` (манифест для установки/поиска).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills: 5](https://img.shields.io/badge/Skills-5-blue.svg)](index.json)
[![CI](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/bestdeejay-design/agent-skills/actions/workflows/validate-skills.yml)
[![Updated](https://img.shields.io/badge/Updated-2026--08--07-green.svg)](index.json)

**🌐 Versions:** [English](README.md) · [Русский](README.ru.md) · [Website](https://bestdeejay-design.github.io/agent-skills/)

---

## 📦 Каталог скиллов

| Скилл | Категория | Описание | Триггеры |
|-------|-----------|----------|----------|
| [**github-repo-hygiene**](skills/github-repo-hygiene) | `repository` | Проверка и обновление описательной части GitHub-репозитория: README (EN+RU), LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, description, topics, GitHub Pages. | `github hygiene`, `оформить репозиторий`, `обновить readme`, `github page`, `описание репозитория`, `теги для поиска`, `topics`, `contributing`, `license`, `security policy` |
| [**test-graphics**](skills/test-graphics) | `media` | Генерация тестовых изображений, фото, иконок, placeholders через Python + бесплатные API (loremflickr, placehold.co, picsum.dev, Lucide). | `test images`, `placeholder`, `тестовые картинки`, `иконки для теста`, `заглушки`, `mock data images`, `сгенерировать фото` |
| [**reddit-karma**](skills/reddit-karma) | `social` | Систематическая работа на Reddit для набора кармы аккаунта InterviewDesigner777: поиск тем, подготовка ответов, распознавание тона, шаблоны благодарностей, регулярный забег. | `reddit`, `карма`, `karma`, `r/LocalLLaMA`, `поднять карму`, `ответить на комментарии`, `забег по reddit` |
| [**presentation-maker**](skills/presentation-maker) | `media` | Генератор презентаций: Markdown-аутлайн, HTML 16:9 слайды, .pptx через python-pptx. Авто-лейауты, темы, дизайн-система (токены, mood), модуль «Продакт-дизайнер» (нарратив, дата-виз, a11y, премиум). | `сделай презентацию`, `presentation`, `слайды`, `pptx`, `сделай доклад`, `презентация для`, `generate slides`, `make a deck` |
| [**docs-system**](skills/docs-system) | `repository` | Гайд для AI-агента: как правильно составлять продуктовую и проектную документацию и её состав. Продуктовая ветка (VISION/PRD/ROADMAP/FEATURES) и проектная ветка (ARCHITECTURE/ADR/контракты/TEST_CASES/карта REFERENCE), порядок заполнения (фазы), шаблоны, чек-лист полноты, уровни L1/L2/L3 для больших систем. | `документация`, `каталог документов`, `набор документации`, `полная документация`, `documentation`, `docs catalog`, `documentation structure`, `docs for new project` |

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
├── index.json                 # Манифест всего репозитория (поиск/каталог)
├── README.md                  # Английская версия
├── README.ru.md               # Эта файла (русская версия)
├── LICENSE                    # MIT License
├── CONTRIBUTING.md            # Как добавлять/обновлять скиллы
├── SECURITY.md                # Политика безопасности
├── CODE_OF_CONDUCT.md         # Contributor Covenant 2.1
├── .github/
│   └── workflows/
│       └── validate-skills.yml # CI: JSON схема, кросс-чек, синтаксис Python
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
        └── examples/pmos/README.md
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