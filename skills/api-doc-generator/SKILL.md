---
name: api-doc-generator
description: "Генерация Markdown-документации REST API из OpenAPI-схемы (3.x, включая 3.1.0). Скрипт api_doc.py читает openapi.json (файл или stdin), извлекает endpoint'ы (method, path, summary, operationId, параметры query/path/header, requestBody, коды ответов) и рендерит Markdown-раздел на каждый эндпоинт. FastAPI: схема из app.openapi() или /openapi.json; Express: swagger-jsdoc (референс в SKILL.md). Триггеры: 'api doc', 'документация API', 'openapi', 'swagger в markdown', 'сгенерай api doc', 'документировать эндпоинты', 'api reference', 'описать API', 'rest api docs'.",
license: MIT
metadata:
  author: best
  version: 1.0.0
compatibility: "Requires Python 3 stdlib (json, argparse); input: OpenAPI 3.x JSON"
when_to_use: "Use when documenting a REST API as Markdown from an OpenAPI/Swagger spec. Triggers: 'api doc', 'документация API', 'openapi', 'swagger to markdown', 'описать эндпоинты', 'api reference'. Example: 'сгенерируй markdown-документацию из openapi.json'."
---

# API Doc Generator

> Генерация Markdown-документации REST API из OpenAPI-схемы: парсинг схемы,
> разбор endpoint'ов, рендер раздела на каждый метод с параметрами и кодами.

Загружай этот скилл когда нужно **документировать REST API** в Markdown:
по endpoint'ам, с параметрами, телами запросов и кодами ответов. Скилл читает
OpenAPI-схему (JSON) и выдаёт готовый документ.

## 🎯 When to use

Use this skill when:
- Есть `openapi.json`/`swagger.json` и нужен Markdown-документ для README/Wiki
- FastAPI-приложение: нужно отрендерить `app.openapi()` в документацию
- Просят «документация API», «api doc», «описать эндпоинты»
- Нужна автономная страница API Reference без хостинга Swagger UI

Do NOT use when:
- Есть Swagger UI / Redoc онлайн — это уже интерактивная документация
- Нужна сгенерированная из кода схема (Express + swagger-jsdoc) — сначала собери схему, потом этот скрипт
- Нужен глубокий разбор типов (oneOf/allOf) — скрипт выдаёт плоскую таблицу параметров

## 📦 Files

- `SKILL.md` — этот файл
- `scripts/api_doc.py` — рендерер OpenAPI → Markdown (Python 3 stdlib)

## 🧰 Usage

```bash
# Из файла:
python3 skills/api-doc-generator/scripts/api_doc.py --schema openapi.json

# Из stdin:
cat openapi.json | python3 api_doc.py --stdin

# В файл:
python3 api_doc.py --schema openapi.json --title "My API" --out API.md
```

## 🔌 Получение схемы по фреймворку

### FastAPI (OpenAPI 3.1 по умолчанию)
```python
import json, app  # your FastAPI app
with open("openapi.json", "w") as f:
    json.dump(app.openapi(), f, ensure_ascii=False, indent=2)
```
Затем: `python3 api_doc.py --schema openapi.json`.

### Express (Node.js)
Вариант A — swagger-jsdoc (аннотированный код):
```bash
npx swagger-jsdoc -d swagger-def.js -o openapi.json
```
Вариант B — AST-прогулка по маршрутам (если нет аннотаций): собрать
`app._router.stack` (Express 4) в список method+path вручную — базовый случай.

## ✅ Definition of Done
- Скрипт отработал: Markdown-документ в stdout или `--out`.
- Каждый endpoint: method, path, summary, параметры таблицей, коды ответов.
- Схема OpenAPI прошла `json.loads` без ошибок.