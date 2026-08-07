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
5. **Обновите `index.json`** — добавьте запись в массив `skills[]` с полями: `name`, `version`, `category`, `description`, `path`, `triggers`, `updated`
6. **Проверьте**: `python3 -m json.tool index.json >/dev/null` (валидный JSON)
7. **Откройте PR** с описанием: что делает скилл, триггеры, требования

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

## Code of Conduct

Это проект следует [Contributor Covenant 2.1](CODE_OF_CONDUCT.md). Участвуя, вы соглашаетесь соблюдать его нормы.

## Лицензия

Вклады распространяются под [MIT License](LICENSE).