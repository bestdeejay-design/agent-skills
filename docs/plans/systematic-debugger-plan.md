# Plan: Создать скилл systematic-debugger

> Дата: 2026-08-08
> Статус: `approved`

## Goal
Скилл `skills/systematic-debugger/` — процессная методология отладки по «Iron Law»
(4 фазы: воспроизведение → гипотезы → изоляция причины → фикс+регресс-тест).
Рабочий скрипт `debug_log.py` собирает диагностическую информацию о среде и
оформляет отчёт по фазам. Только Python 3 stdlib.

**Acceptance criteria (проверяемо):**
- [x] CR1: SKILL.md описывает 4 фазы, Iron Law, Red Flags, Rationalization Table
- [x] CR2: скрипт `debug_log.py --label <имя>` формирует отчёт с секциями (среда, команда, ожидание, факт, гипотезы)
- [x] CR3: скилл проходит validate_skills.py (skill.json + SKILL.md + files)

## Constraints
- Только Python 3 stdlib; скрипт не исполняет опасные команды (только чтение env/версий)
- Не трогать существующие скиллы
- Рабочий процесс — «прогнать по фазам, зафиксировать в отчёт», а не автофикс

## Steps

### Step 1: процессная часть SKILL.md
- Files: `skills/systematic-debugger/SKILL.md`
- Produces: описание 4 фаз + Iron Law + Red Flags + Rationalization Table
- Consumes: исследование librarian (эталоны debugging)
- Action: структура по образцу code-review, секции When to use / Workflow / Red flags / DoD
- Verification: файл содержит ключевые термины (Iron Law, Red Flags, 4 фазы)
- [x] done

### Step 2: скрипт-отчёт
- Files: `skills/systematic-debugger/scripts/debug_log.py`
- Produces: `--label NAME` + опциональные `--command`, `--expected`, `--actual` → Markdown-отчёт
- Consumes: platform, sys, datetime (Python stdlib)
- Action: секции «Среда / Команда / Ожидаем / Факт / Гипотезы (1..3) / Регресс-план»
- Verification: `python3 debug_log.py --label test` выводит полный отчёт без ошибок
- [x] done

### Step 3: манифесты
- Files: `skills/systematic-debugger/skill.json`
- Action: required fields по образцу code-review; category=code
- Verification: `python3 .github/workflows/validate_skills.py` → скилл в списке ✅
- [x] done

## Interfaces
- Consumes → Produces:
  - `Step1.methodology` → `Step2.report_sections`
  - `Step2.report_md` → `Step3.description`
- Внешние рамки: методология без внешних зависимостей, только процесс

## Verification (полная)
- [x] `python3 skills/plan-skill/scripts/plan_validator.py <этот файл>` → ✅
- [x] `debug_log.py` отработал на реальной среде (macOS/Python)
- [x] Локальный валидатор скиллов 14/14 ✅
- [x] Ревью: замечаний нет