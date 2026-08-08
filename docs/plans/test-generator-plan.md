# Plan: Создать скилл test-generator

> Дата: 2026-08-08
> Статус: `approved`

## Goal
Скилл `skills/test-generator/` генерирует pytest-скелеты для Python-модулей из
AST по ghostwriter-эвристике (docstring → default → имя параметра), плюс
инструкции для TS (ts-morph) и Go (table-driven). Рабочий скрипт `test_gen.py`
на Python 3 stdlib.

**Acceptance criteria (проверяемо):**
- [x] CR1: `--file module.py` выдаёт pytest-код с parametrize для функций с типизированными параметрами
- [x] CR2: эвристика значений: bool→True/False, int→0/-1/1/граница, str→«sample», list/dict→пустые
- [x] CR3: приватные/dunder-функции (начинающиеся с `_`) пропускаются
- [x] CR4: скилл проходит validate_skills.py (skill.json + SKILL.md + files)

## Constraints
- Только Python 3 stdlib: `ast`, `argparse`, `typing`
- Не трогать существующие скиллы; не создавать файлы вне целевого пути рядом с модулем
- Вывод скрипта — только в stdout, без записи на диск (если не указан --out)

## Steps

### Step 1: парсер AST-функций
- Files: `skills/test-generator/scripts/test_gen.py`
- Produces: `collect_functions(source) -> list[FuncInfo]` (name, args, defaults, return_annotation, async)
- Consumes: `ast.parse(source)`, `ast.walk`
- Action: найти все FunctionDef/AsyncFunctionDef, исключить начинающиеся с `_`
- Verification: модуль импортируется, парсер возвращает сигнатуры,
- [x] done

### Step 2: эвристика значений аргументов
- Files: `skills/test-generator/scripts/test_gen.py`
- Produces: `sample_value(param: Parameter, defaults) -> str` (Python-литерал)
- Action) Маппинг аннотаций (bool, int, float, str, list, dict) + fallback на default
- Verification: для bool выдаётся True/False, для int — 0 и -1, для str — пустая строка
- [x] done

### Step 3: рендер pytest-кода
- Files: `skills/test-generator/scripts/test_gen.py`
- Produces: `render_pytest(funcs, module_name) -> str`
- Consumes: FuncInfo и sample_value из Step 1/2
- Action: сгенерировать `import` + `@pytest.mark.parametrize`, тело с assert-заглушкой для заполнения
- Verification: `python3 test_gen.py --file <module>` выдаёт валидный pytest-файл
- [x] done

### Step 4: манифесты скилла
- Files: `skills/test-generator/SKILL.md`, `skills/test-generator/skill.json`
- Action: SKILL.md по формату code-review, skill.json с required fields
- Verification: `python3 .github/workflows/validate_skills.py` → скилл в списке ✅
- [x] done

## Interfaces
- Consumes → Produces:
  - `Step1.parser` → `Step2.sampler`
  - `Step3.pytest_code` → `Step4.description`
- Внутренние рамки: скрипт использует только stdlib; TS/Go-реферensen описаны в SKILL.md, не в коде.

## Verification (полная)
- [x] `python3 skills/plan-skill/scripts/plan_validator.py <этот файл>` → ✅
- [x] `test_gen.py` отработал на реальном Python-модуле (numpy/skill-скрипт репозитория)
- [x] Локальный валидатор скиллов 14/14 ✅
- [x] Ревью: замечаний нет