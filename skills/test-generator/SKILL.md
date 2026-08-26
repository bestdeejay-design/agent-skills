---
name: test-generator
description: "Генерация pytest-скелетов из Python-модуля по AST с ghostwriter-эвристикой значений аргументов (bool→True/False, int→0/-1/1, str→sample/пустая, list/dict→пустые, Optional→None). Скрипт test_gen.py парсит функции/async-функции через ast, пропускает приватные (_), генерирует @pytest.mark.parametrize с assert-заглушками. Включает референс по генерации тестов на TypeScript (ts-morph, *.test.ts) и Go (table-driven). Триггеры: 'generate tests', 'сгенерируй тесты', 'test skeleton', 'pytest скелет', 'покрытие тестами', 'unit tests для функций', 'тесты на функции', 'создать тесты'.",
license: MIT
metadata:
  author: best
  version: 1.0.0
compatibility: "Requires Python 3 stdlib (ast, argparse); optional pytest to run generated tests"
when_to_use: "Use when you need starter pytest/unit tests from existing functions. Triggers: 'generate tests', 'сгенерируй тесты', 'test skeleton', 'pytest скелет', 'покрытие тестами', 'создать тесты'. Examples: 'Generate pytest skeletons for module.py' / 'Сгенерируй тесты для функций'."
---

# Test Generator

> Генерация pytest-скелетов из сигнатур функций: AST-парсинг + эвристика значений,
> готовый параметризованный тест-файл в stdout или файл.

Загружай этот скилл когда нужно **создать стартовый pytest-набор** для
существующих функций или модуля. Скилл читает исходник, извлекает сигнатуры
и генерирует `@pytest.mark.parametrize`-скелеты с разумными тестовыми значениями —
остаётся лишь дописать assert-ожидания.

## 🎯 When to use

Use this skill when:
- Нужны тесты для нового модуля, где покрытие начинается с пустого файла
- Просят «сгенерируй тесты», «test skeleton», «покрой функциям»
- Нужна быстрая заготовка parametrize-кейсов с типичными значениями
- Хочешь перейти к TDD: сгенерируй красные скелеты и реализуй

Do NOT use when:
- Нужны осмысленные ассерты под конкретную логику — скрипт даёт заглушки, логику пишешь сам
- Тесты уже покрывают функции — файл-генератор всё перезапишет
- Нужны моки/фикстуры вне модуля — это уровень pytest напрямую

## 📦 Files

- `SKILL.md` — этот файл
- `scripts/test_gen.py` — генератор из AST (Python 3 stdlib)
- `references/` — примеры и референс TS/Go (в будущих версиях)

## 🧰 Usage

```bash
# В stdout:
python3 skills/test-generator/scripts/test_gen.py --file path/to/module.py

# В файл (рядом с модулем):
python3 skills/test-generator/scripts/test_gen.py \
    --file path/to/module.py --out tests/test_module.py
```

## ⚙️ Эвристика значений аргументов

| Аннотация | Значения |
|-----------|----------|
| `bool` | `True`, `False` |
| `int` | `0`, `-1`, `1` |
| `float` | `0.0`, `-1.5` |
| `str` / `text` | `"sample"`, `""` |
| `list[...]` | `[]` |
| `tuple[...]` | `()` |
| `dict[...]` | `{}` |
| `Optional[...]` | `None` |
| иное | значение не подставляется → `None`-заглушка |

Правила:
- Функции, начинающиеся с `_`, пропускаются.
- `async def` оборачивается в `asyncio.run(...)`.
- В генерируемом коде assert-заглушка: `assert result is not None` — допиши реальные ожидания.

## ✅ Definition of Done
- Скрипт отработал: валидный pytest-файл в stdout или `--out`.
- Сгенерированный код проходит `python3 -c "import ast"` (синтаксис корректный).
- Значения аргументов соответствуют эвристикам (таблица выше).