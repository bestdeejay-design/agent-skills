# Agent Skills — Коллекция скиллов для AI-агентов

> Автономные инструкции (skills) для AI-агентов: Sisyphus, opencode, и совместимые. Каждый скилл — папка с `SKILL.md` (инструкция) и `skill.json` (манифест для установки/поиска).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills: 4](https://img.shields.io/badge/Skills-4-blue.svg)](index.json)
[![Updated](https://img.shields.io/badge/Updated-2025--08--07-green.svg)](index.json)

---

## 📦 Каталог скиллов

| Скилл | Категория | Описание | Триггеры |
|-------|-----------|----------|----------|
| [**github-repo-hygiene**](skills/github-repo-hygiene) | `repository` | Проверка и обновление описательной части GitHub-репозитория: README (EN+RU), LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, description, topics, GitHub Pages. | `github hygiene`, `оформить репозиторий`, `обновить readme`, `github page`, `описание репозитория`, `теги для поиска`, `topics`, `contributing`, `license`, `security policy` |
| [**test-graphics**](skills/test-graphics) | `media` | Генерация тестовых изображений, фото, иконок, placeholders через Python + бесплатные API (loremflickr, placehold.co, picsum.dev, Lucide). | `test images`, `placeholder`, `тестовые картинки`, `иконки для теста`, `заглушки`, `mock data images`, `сгенерировать фото` |
| [**reddit-karma**](skills/reddit-karma) | `social` | Систематическая работа на Reddit для набора кармы аккаунта InterviewDesigner777: поиск тем, подготовка ответов, распознавание тона, шаблоны благодарностей, регулярный забег. | `reddit`, `карма`, `karma`, `r/LocalLLaMA`, `поднять карму`, `ответить на комментарии`, `забег по reddit` |
| [**presentation-maker**](skills/presentation-maker) | `media` | Генератор презентаций: Markdown-аутлайн, HTML+CSS 16:9, .pptx через python-pptx. Авто-лейауты, темы, дизайн-система (токены, mood), модуль «Продакт-дизайнер» (нарратив, дата-виз, a11y, премиум). | `сделай презентацию`, `presentation`, `слайды`, `pptx`, `сделай доклад`, `презентация для`, `generate slides`, `make a deck` |

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
├── README.md                  # Этот файл
├── LICENSE                    # MIT License
├── CONTRIBUTING.md            # Как добавлять/обновлять скиллы
├── SECURITY.md                # Политика безопасности
├── CODE_OF_CONDUCT.md         # Contributor Covenant 2.1
├── .github/
│   └── workflows/
│       └── validate-skills.yml # CI: проверка манифестов
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
    └── presentation-maker/
        ├── SKILL.md
        ├── skill.json
        ├── scripts/
        │   ├── build_html.py
        │   ├── build_pptx.py
        │   └── verify_slides.py
        ├── templates/
        │   ├── slides.html
        │   ├── themes/*.json
        │   └── icons/*.svg
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
2. Добавьте `SKILL.md` — полная инструкция для агента (см. существующие как образец)
3. Добавьте `skill.json` — манифест (см. схему ниже)
4. При необходимости — скрипты/шаблоны в подпапках
5. Обновите `index.json` (добавьте запись в `skills[]`)
6. Создайте PR

### Схема `skill.json`

```json
{
  "name": "kebab-case-name",
  "version": "1.0.0",
  "description": "Краткое описание (1-2 предложения)",
  "author": "your-github-username",
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