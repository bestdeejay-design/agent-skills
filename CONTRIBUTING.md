# Contributing to Agent Skills

Спасибо за интерес к улучшению коллекции скиллов! Этот документ описывает процесс добавления новых скиллов и обновления существующих.

## Как внести вклад

### 1. Добавление нового скилла

1. **Создайте ветку**: `git checkout -b feat/skill-<name>`
2. **Создайте папку** в `skills/<kebab-case-name>/`
3. **Добавьте два обязательных файла**:
   - `SKILL.md` — полная инструкция для агента (на английском — основной язык, русский по желанию; с YAML-фронтматтером `name`, `description`)
   - `skill.json` — манифест (см. схему ниже)
4. **При необходимости** добавьте скрипты/шаблоны в подпапки (`scripts/`, `templates/`, `icons/`)
5. **Обогатите скилл каноническими паттернами**: найдите 3-6 аналогов у канонических авторов (Anthropic skills, obra/superpowers, vercel-labs/skills, trailofbits/skills, NVIDIA SkillSpector и др.) и добавьте `references/canonical-patterns.md` — список аналогов с URL, техники, которых не хватает текущей реализации, и примеры использования. Создайте скилл с учётом найденных паттернов.
6. **Подготовьте showcase-пример на реальном проекте**: продемонстрируйте работу скилла на настоящем коде/данных (например, из вашего проекта — lovii.ru в `lovii_demo`). Добавьте `docs/showcase.md` в папку скилла — описание: входные данные (путь к файлам), запуск, вывод и что из этого следует. Цель — показать не абстрактный пример `foo.txt`, а реальное применение. Смотрите шаблон `docs/showcase-template.md` и существующие примеры в `docs/showcase/`.
7. **Обновите `index.json`** — добавьте запись в массив `skills[]` с полями: `name`, `version`, `category`, `description`, `path`, `triggers`, `updated`
8. **Проверьте**: `python3 -m json.tool index.json >/dev/null` (валидный JSON)
9. **Откройте PR** с описанием: что делает скилл, триггеры, требования

### 2. Обновление существующего скилла

1. Внесите изменения в `SKILL.md` и/или `skill.json`
2. Обновите `version` в `skill.json` (semver)
3. Обновите `updated` в `skill.json` и запись в `index.json`
4. Откройте PR

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

- Язык: **английский** (основной, инструкции для агента); русский — по желанию, не обязателен
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

## Требования к showcase-примерам

Каждый новый скилл обязан иметь `docs/showcase.md` — демонстрацию на **реальном**
проекте (не абстрактных `foo.txt`). Эталонный вариант — ваш проект:
- **lovii.ru** — `https://github.com/bestdeejay-design/lovii_demo` (frontend
  marketplace: `index.html`, `index.js`, `css/`, `design/`, `docs/`).

Что обязательно в `docs/showcase.md`:
1. **Вход**: конкретные пути к реальным файлам (репозиторий, относительный путь).
2. **Запуск**: точная команда (скрипт + аргументы).
3. **Вывод**: сокращённый реальный вывод или ссылка на артефакт.
4. **Интерпретация**: что результат означает и почему он полезен владельцу проекта.

Каркас: `docs/showcase-template.md` — скопируйте и заполните. Итоговые компилляции —
в `docs/showcase/` (по файлу на скилл), список показывается в `README`/`README.ru`.

---

## Code of Conduct

Это проект следует [Contributor Covenant 2.1](CODE_OF_CONDUCT.md). Участвуя, вы соглашаетесь соблюдать его нормы.

## Лицензия

Вклады распространяются под [MIT License](LICENSE).