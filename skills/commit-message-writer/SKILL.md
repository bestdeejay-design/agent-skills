---
name: commit-message-writer
description: "Используй, когда нужно оформить staged-изменения в Conventional Commit. Генерация Conventional Commits-сообщений на основе git diff --staged: тип по изменённым файлам, scope по путям, краткое описание, опциональный body с переносами. Триггеры: 'commit message', 'write commit', 'git commit', 'conventional commit', 'сообщение коммита', 'написать коммит', 'commit', 'закоммитить'."
license: MIT
metadata:
  author: best
  version: 1.1.0
compatibility: "Requires git and Python 3"
when_to_use: "Use when writing a Conventional Commit message from staged changes. Triggers: 'commit message', 'write commit', 'git commit', 'conventional commit', 'написать коммит', 'закоммитить'. Example: 'напиши сообщение коммита для застейдженных изменений'."
---

# Commit Message Writer

> Conventional Commits из вашего staged-diff за один шаг.

Загружай этот скилл когда нужно **написать сообщение коммита** по уже
застейдженным изменениям (`git add` уже сделан). Скилл анализирует diff,
определяет тип и scope, выдаёт готовое сообщение в формате
[Conventional Commits](https://www.conventionalcommits.org/).

## When to use

Use this skill when:
- Изменения уже застейджены (`git add`), нужно сообщение коммита
- Нужно привести формат к Conventional Commits (CI требует `commitlint`)
- Нужно автоматически определить scope по путям файлов
- Нужен короткий заголовок + тезисный body (если diff большой)

Do NOT use when:
- Изменения ещё не застейджены — сначала `git add` или `git add -p`
- Требуется разбить изменения на несколько логических коммитов —
  сначала разбей, потом вызывай скилл для каждой части
- Это squash/rebase/merge коммит — скажи об этом явно

## What this skill does

### Inputs
- `staged` (default): анализирует `git diff --cached` (только staged)
- `--unstaged` (опция): аналогично для unstaged (не рекомендуется)
- `--scope` (опция): принудительный scope вместо автодетекта
- `--emoji` (опция): добавить gitmoji-префикс перед типом (`✨ feat: ...`)

### Outputs
- **Готовое сообщение коммита** (1 строка заголовок + опциональный body),
  копируемое командой `git commit` или в файл `COMMIT_EDITMSG`.
- **Краткая справка**: тип, scope, почему выбран именно этот тип.

## How to use

### Шаг 1: убедись, что изменения застейджены

```bash
git add <file1> <file2>
git diff --cached --stat   # проверить, что видит скилл
```

### Шаг 2: сгенерировать сообщение

```bash
python3 scripts/suggest.py --cached
```

Пример вывода:

```
✨ feat(api): add GET /v1/health endpoint with liveness probe

- expose /v1/health via Fastify (src/routes/health.ts)
- add HealthService with process uptime + memory gauge
- wire route into router bootstrap (src/app.ts)

Type: feat — new endpoint, backwards-compatible addition
Scope: api — paths match src/api/** or src/routes/**
```

### Шаг 3: закоммитить

```bash
git commit -m "$(python3 scripts/suggest.py --c)"
```

(или скопируйте сообщение в `git commit` вручную).

## Examples

### Example 1: новая фича

**Input:** staged `src/routes/health.ts`, `src/index.ts`
**Output:**

```
feat(health): add /v1/health liveness endpoint

- add GET /v1/health (liveness probe)
- register route in server bootstrap
```

### Example 2: исправление

**Input:** staged fix в `src/util/parser.ts`
**Output:**

```
fix(parser): handle empty input instead of throwing

Return empty result set when input is blank; add regression test.
```

### Example 3: документация

**Input:** staged `README.md`, `docs/architecture.md`
**Output:**

```
docs: clarify onboarding flow in README and architecture
```

## Constraints & gotchas

- **Aнализ только staged**: скрипт не коммичит сам — только выдаёт сообщение.
- **Один логический коммит**: если изменения разнородные (feat + fix + docs в
  одном diff), скрипт выберет доминирующий тип и пометит в «краткой справке»,
  что стоит разбить на несколько коммитов.
- **Breaking changes**: если diff содержит `BREAKING CHANGE` или удаление
  публичного API (например `-` в функциях), скрипт добавит `!` к типу
  (`feat!`) и блок `BREAKING CHANGE:` в body.
- **Не использует эмодзи по умолчанию**: gitmoji включается только флагом
  `--emoji`.
- **Скроб-крайние случаи**: для merge/revert коммитов предложение не даётся —
  используйте дефолт `git merge`/`git revert`.

## Related

- Pairs well with `code-review` (ревью до коммита) и `changelog-generator`
  (после — из коммитов в CHANGELOG).
- Convention spec: https://www.conventionalcommits.org/ — правила типов.
- Линтер для CI: https://commitlint.js.org/ (если проекте используется).