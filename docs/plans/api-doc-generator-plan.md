# Plan: Создать скилл api-doc-generator

> Дата: 2026-08-08
> Статус: `approved`

## Goal
Скилл `skills/api-doc-generator/` генерирует Markdown-документацию REST API из
OpenAPI-схемы. Рабочий скрипт `api_doc.py` извлекает OpenAPI 3.1 из FastAPI
приложения (app.openapi()) или читает /openapi.json и рендерит Markdown по
endpoint'ам (method, path, params, request/response schema, error codes).
Референс для Express (swagger-jsdoc / AST) — в SKILL.md. Только Python 3 stdlib.

**Acceptance criteria (проверяемо):**
- [x] CR1: `--schema openapi.json` выводит Markdown с секциями по endpoint'ам
- [x] CR2: секция включает method, path, summary, параметры (query/path/body), ответы и error codes
- [x] CR3: скилл проходит validate_skills.py (skill.json + SKILL.md + files)

## Constraints
- Только Python 3 stdlib (json, argparse); не вызывает сетевых запросов
- FastAPI-интеграция описана в SKILL.md, не в скрипте (скрипт читает готовую схему)
- Не трогать существующие скиллы

## Steps

### Step 1: парсер OpenAPI-схемы
- Files: `skills/api-doc-generator/scripts/api_doc.py`
- Produces: `load_schema(path) -> dict` + `iter_endpoints(schema) -> list[Endpoint]`
- Consumes: файл openapi.json (или JSON-строку через stdin)
- Action: извлечь paths, methods, operationId, summary, parameters, requestBody, responses
- Verification: `python3 api_doc.py --schema <json>` возвращает список endpoint'ов без ошибок
- [x] done

### Step 2: рендер Markdown
- Files: `skills/api-doc-generator/scripts/api_doc.py`
- Produces: `render_markdown(endpoints, title) -> str`
- Consumes: Endpoint из Step 1
- Action: секция на endpoint: `### METHOD /path`, параметры таблицей, пример ответа (код+description)
- Verification: вывод содержит method, path, таблицу параметров, коды ответов
- [x] done

### Step 3: манифесты скилла
- Files: `skills/api-doc-generator/SKILL.md`, `skills/api-doc-generator/skill.json`
- Action: SKILL.md по формату code-review (When to use, Workflow, Express-референс), skill.json с required fields
- Verification: `python3 .github/workflows/validate_skills.py` → скилл в списке ✅
- [x] done

## Interfaces
- Consumes → Produces:
  - `Step1.parser` → `Step2.renderer`
  - `Step2.markdown` → `Step3.description`
- Внешние рамки: FastAPI OpenAPI 3.1.0 (по умолчанию), Redocly CLI как альтернатива (в SKILL.md)

## Verification (полная)
- [x] `python3 skills/plan-skill/scripts/plan_validator.py <этот файл>` → ✅
- [x] `api_doc.py` отработал на реальной openapi.json (тестовая мини-схема)
- [x] Локальный валидатор скиллов 14/14 ✅
- [x] Ревью: замечаний нет