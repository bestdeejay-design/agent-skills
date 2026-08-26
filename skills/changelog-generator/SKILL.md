---
name: changelog-generator
description: "Генерация раздела CHANGELOG (Keep a Changelog) из git-истории по Conventional Commits. Скрипт changelog_gen.py читает git log в диапазоне tag..HEAD, парсит commit-сообщения, маппит типы (feat→Added, fix→Fixed, perf/refactor→Changed, breaking→отдельная секция) и рендерит Markdown с датами и ссылками на коммиты. Режимы: --top (Unreleased), --from-tag, включая скрытые типы (docs/ci/chore) через флаг. Триггеры: 'changelog', 'сгенерай чанжлог', 'обнови changelog', 'release notes', 'история изменений', 'keep a changelog', 'generate changelog', 'сборка changelog'.",
license: MIT
metadata:
  author: best
  version: 1.0.0
compatibility: "Requires Python 3 stdlib and git repo with Conventional Commits"
when_to_use: "Use when generating/updating a CHANGELOG from git history (Conventional Commits). Triggers: 'changelog', 'сгенерируй чанжлог', 'release notes', 'история изменений', 'keep a changelog'. Example: 'обнови CHANGELOG.md перед релизом'."
---

# Changelog Generator

> Генерация раздела CHANGELOG из git-истории: анализ commit-логов, группировка
> по Keep a Changelog секциям, готовый Markdown в stdout или файл.

Загружай этот скилл когда нужно **сгенерировать/обновить changelog** из истории
коммитов для релиза или представительской проверки. Скилл читает `git log`,
классифицирует изменения по типам и выдаёт готовый Markdown.

## 🎯 When to use

Use this skill when:
- Нужно сгенерировать `CHANGELOG.md` перед релизом (секции Added/Fixed/Changed)
- Нужен «что нового» для PR или release notes
- Просят «созерай чанлог», «обнови changelog», «история изменений»
- Нужно быстро посмотреть, какие фичи/фиксы попали в диапазон тегов

Do NOT use when:
- Лог коммитов нужен «как есть» (без группировки) — это обычный git log
- Нужна переносим MVP-типов вручную — скрипт уже делает маппинг
- Репозиторий не использует Conventional Commits — маппинг будет пустым

## 📦 Files

- `SKILL.md` — этот файл
- `scripts/changelog_gen.py` — основной скрипт (Python 3 stdlib only)

## 🔧 Usage

```bash
# Unreleased (от последнего тега до HEAD)
python3 skills/changelog-generator/scripts/changelog_gen.py --repo <path> --top

# Для версии между тегами:
python3 skills/changelog-generator/scripts/changelog_gen.py \
    --repo <path> --from-tag v1.0.0 --version 1.1.0

# Включить скрытые типы (docs/ci/chore/test):
python3 changelog_gen.py --repo <path> --top --all

# Записать в файл:
python3 changelog_gen.py --repo <path> --top --out CHANGELOG.md
```

## 🔄 Маппинг типов

| Conventional Commits | Секция | Замечание |
|----------------------|--------|-----------|
| `feat: ...`           | Added  | Новая функциональность |
| `fix: ...`            | Fixed  | Багификсы |
| `perf:` / `refactor:` | Changed | Изменения поведения |
| `revert:`             | Reverts| Откаты |
| breaking (`!` или `BREAKING CHANGE:`) | Breaking | Выносится в свою секцию |
| docs/style/test/build/ci/chore | скрыты | Видны только с `--all` |

## ✅ Definition of Done
- Скрипт отработал без ошибок: stdout или файл с секциями Added/Fixed/Changed.
- Breaking-коммиты вынесены в отдельную секцию.
- Дата и версия в заголовке корректны.
- Если нужен CHANGELOG.md в репо — содержимое вставлено (по отдельным запросам).