# Plan: <Краткое имя задачи>

> Дата: YYYY-MM-DD
> Статус: `draft` → `approved` → `executing` | `done`

## Goal
<Одна строка: что получаем на выходе.>

**Acceptance criteria (проверяемо):**
- [ ] CR1: ...
- [ ] CR2: ...

## Constraints
- Не трогать: ...
- Только Python 3 stdlib / без новых зависимостей
- Совместимость с ...

## Steps

### Step 1: <название>
- Files: `path/to/file.py`
- Produces: `func_name(...) -> ...`
- Consumes: существующие `module.x`
- Action: конкретное изменение
- Verification: `python3 -m pytest tests/... -k ...` → Expected FAIL
- [ ] done

### Step 2: <название>
- Files: `path/to/tests/test_x.py`
- Produces: тест, который падает (FAIL)
- Action: пишем тест на CR1
- Verification: тест падает (это ожидаемо)
- [ ] done

### Step 3: <название>
- Files: `path/to/file.py`
- Action: реализация, закрывающая FAIL
- Verification: тест PASS
- [ ] done

## Interfaces
- Consumes → Produces:
  - `step1.output` → `step2.input`
  - `step3` вернёт `Result`-объект → используется дальше

## Verification (полная)
- [ ] `python3 scripts/plan_validator.py <этот файл>` → ✅
- [ ] Тесты зелёные
- [ ] Диагностика чистая
- [ ] Ревью (code-review скилл) — замечания закрыты