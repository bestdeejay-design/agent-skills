# Plan: Добавить `--lint` флаг в `scripts/lint.py`

> Дата: 2026-08-08
> Статус: `approved`

## Goal
Скрипт `scripts/lint.py` получает флаг `--lint`, который запускает внешний
линтер (ruff) вместо собственной проверки.

**Acceptance criteria (проверяемо):**
- [x] CR1: `python3 scripts/lint.py --lint --path src/app.py` вызывает ruff и выводит его сообщения
- [x] CR2: без `--lint` поведение скрипта не изменилось (регрессия отсутствует)

## Constraints
- Только Python 3 stdlib + вызов внешней команды (ruff) через `subprocess`
- Код функции `main()` в `scripts/lint.py` не выносится в отдельный модуль

## Steps

### Step 1: тест на флаг
- Files: `tests/test_lint.py`
- Produces: `test_lint_flag_invokes_ruff()` — падает (FAIL)
- Consumes: `main(argv)` из `scripts/lint.py`
- Action: добавить тест, проверяющий, что при `--lint` вызывается ruff через subprocess
- Verification: `python3 -m pytest tests/test_lint.py` → Expected FAIL
- [x] done

### Step 2: реализация флага
- Files: `scripts/lint.py`
- Action: распарсить `--lint` в `argparse`, вызвать `subprocess.run(["ruff", path])`
- Verification: тест из Step 1 → PASS
- [x] done

### Step 3: проверка регрессии
- Files: `scripts/lint.py`, `tests/test_lint.py`
- Action: прогнать полный набор тестов и убедиться, что старый режим работает
- Verification: `python3 -m pytest tests/` → PASS
- [x] done

## Interfaces
- Consumes → Produces:
  - `Step1.fail_test` → `Step2.implementation`
  - `Step2.lint_runner` → `Step3.regression_check`

## Verification (полная)
- [x] `python3 scripts/plan_validator.py examples/plan-example.md` → ✅
- [x] Тесты зелёные: `python3 -m pytest tests/`
- [x] Диагностика чистая
- [x] Ревью пройдено, замечаний нет