---
name: code-review
description: "Структурированный code review: читает git diff или путь к репозиторию/файлу, применяет чек-лист категорий (correctness, security, performance, style, tests, edge cases, a11y) и выдаёт замечания вида [severity] файл:строка с предлагаемым исправлением. Скилл только анализирует и комментирует, правки не вносит. Триггеры: 'code review', 'ревью кода', 'review PR', 'проверь код', 'pull request review', 'code quality', 'замечания по коду', 'найти баги', 'review commit', 'проверь изменения', 'review diff', 'ревью пул-реквеста'."
license: MIT
metadata:
  author: best
  version: 1.1.0
compatibility: "Requires Python 3 stdlib; git for --repo mode"
when_to_use: "Use when reviewing a PR/diff/commit for bugs, security, style before merge. Triggers: 'code review', 'ревью кода', 'review PR', 'проверь код', 'найди баги', 'замечания по коду'. Example: 'проверь код в этом PR'."
---

# Code Review

> Структурированный ревью PR/diff за один запуск: чек-лист, severity, файл:строка, исправление.

Загружай этот скилл когда нужно **проверить код** (diff, PR, commit) и получить
структурированные замечания с приоритетами. Скилл читает изменения, применяет
чек-лист из шести категорий и выдаёт готовый текст для комментария в PR.

## 🎯 When to use

Use this skill when:
- Нужно ревью PR/commit/diff перед мержем
- Просят «проверь код», «найди баги», «замечания по коду»
- Нужен чек-лист code quality перед релизом
- Нужно быстро прогнать diff по категориям: correctness, security, performance, style, tests, edge cases, a11y
- Нужен структурированный комментарий к PR с severity и ссылками на файл:строку

Do NOT use when:
- Нужно **внести правки** — скилл только анализирует и комментирует; исправления вносит агент отдельно по явному запросу
- Нужен полный аудит всего репозитория, а не изменений — скилл работает по diff
- Нужен security-аудит с PoC-доказательством уязвимости — используй специализированный security-скилл
- Это первичное ревью архитектуры без кода — скилл анализирует код, не схемы

## 📦 What this skill does

### Inputs
- `--repo PATH` — git-репозиторий: берётся `git diff HEAD` (staged + unstaged)
- `--file PATH` — обычный файл: ревьюится целиком, каждая строка считается добавленной
- `--diff PATH` — файл, содержащий git diff
- stdin — git diff (по умолчанию, `git diff | review.py`)

### Outputs
- **Список замечаний**: `[severity] файл:строка — правило: проблема` + предлагаемое исправление
- **Сводка** по категориям и severity (critical/warning/nit)
- **Markdown-отчёт** по шаблону `templates/review-template.md` — готов для комментария в PR

## 🔧 How to use

### Шаг 1: получить diff

```bash
git diff HEAD > /tmp/pr.diff
```

### Шаг 2: запустить ревью

```bash
python3 scripts/review.py --diff /tmp/pr.diff
```

Или напрямую из репозитория:

```bash
python3 scripts/review.py --repo /path/to/repo
```

Или через stdin:

```bash
git diff | python3 scripts/review.py
```

### Шаг 3: отфильтровать и оформить

```bash
# только critical/warning — то, что блокирует мерж
python3 scripts/review.py --diff /tmp/pr.diff --severity critical,warning

# только security-категория
python3 scripts/review.py --diff /tmp/pr.diff --category security

# markdown-отчёт по шаблону для комментария в PR
python3 scripts/review.py --diff /tmp/pr.diff \
  --format markdown --template templates/review-template.md

# JSON-отчёт для автоматизации
python3 scripts/review.py --diff /tmp/pr.diff --json
```

## 📚 Examples

### Example 1: ревью PR из репозитория

**Input:** `python3 review.py --repo ./myapp`
**Output:**

```
[critical] src/db.py:18 — SEC-001: SQL-запрос собирается из f-строки — риск SQL-инъекции.
    код: sql = f"INSERT INTO users (name) VALUES ({name})"
    fix: используйте параметризованные запросы: cursor.execute(sql, (name,))
[warning] src/db.py:9 — CORR-001: сравнение с None в Yoda-форме.
    fix: пишите `x is None`
```

### Example 2: ревью файла целиком

**Input:** `python3 review.py --file src/worker.go`
**Output:**

```
[critical] worker.go:16 — SEC-009: запуск через `sh -c` с конкатенацией — риск command injection.
    fix: передавайте аргументы отдельными элементами без shell.
```

### Example 3: markdown-отчёт для комментария в PR

**Input:** `python3 review.py --diff pr.diff --format markdown --template templates/review-template.md`
**Output:** готовый Markdown с секциями Summary / Findings / Checklist,
подстановкой `{{REVIEW_TARGET}}`, `{{TOTAL}}`, `{{CRITICAL}}`, `{{WARNING}}`,
`{{NIT}}`, `{{SUMMARY}}`, `{{FINDINGS}}`, `{{DATE}}`.

## ⚠️ Constraints & gotchas

- **Скилл не вносит правки**: он читает diff и выдаёт замечания. Исправления вносит агент только по явному запросу пользователя.
  - **Эвристики**: правила — регулярные выражения, возможны ложные срабатывания. Каждое замечание проверяй вручную перед публикацией.
  - **SEC-007 (innerHTML/XSS)** подавляется на строках, где применён escape-хелпер
    (`esc(`, `escapeHtml(`, `sanitize(` и т.п.) — такие находки ложные. Если экранирование
    происходит внутри вызываемой функции (например, `renderCard()`), проверь её вручную.
  - **EDGE-004 (деление на переменную)** не срабатывает внутри CSS `url(...)`, `data:`-URI и
    URL со схемой (`://`) — `/` там не арифметика (например, `http://.../svg`).
- **Только добавленные строки**: удалённые строки не ревьюятся, номера строк соответствуют новому файлу.
- **Без внешних зависимостей**: только Python 3 stdlib; `git` нужен только для режима `--repo`.
- **Секреты**: если найдены захардкоженные пароли/токены — не публикуй их в комментарии PR, сообщи приватно (DM/личный канал).
- **Severity не блокирует**: отчёт — материал для ревьюера, а не автоматический gate.

## 🔗 Related

- Pairs well with `commit-message-writer` (ревью до коммита) и `github-repo-hygiene` (гигиена репозитория после мержа).
- Чек-лист правил: `scripts/checklists.py` — расширяй под свой стек (добавляй dict-правила).
- Шаблон отчёта: `templates/review-template.md`.
- Пример разбора PR: `examples/example-pr.md`.
