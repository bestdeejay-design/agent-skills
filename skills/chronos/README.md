# Chronos

> The Documentation Timekeeper — AI agents for docs integrity

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Chronos — это AI-агент для поддержания целостности и консистентности документации в проектах. Следит за иерархией правды, ищет дубли, противоречия и устаревшие данные.

## Features

- **Duplicate Detection** — находит документы с высокой схожестью
- **Broken Links** — обнаруживает битые ссылки
- **Missing Documents** — проверяет обязательные документы для уровня
- **Orphan Detection** — находит документы без ссылок
- **Classification** — определяет тип документа (канон/производный/артефакт)
- **Staleness Check** — обнаруживает устаревшие данные

## Installation

```bash
pip install chronos
```

## Quick Start

```bash
# Базовый аудит
chronos --path .

# Полный Пантеон
chronos --path . --preset full

# Только JSON
chronos --path . --output json --output-file report.json
```

## Presets

| Preset | Agents | Description |
|--------|--------|-------------|
| `minimal` | Censor | Базовый аудит: дубли, битые ссылки |
| `standard` | Censor + Dewey + Canon | Полная проверка + классификация |
| `full` | All agents | Полный Пантеон |

## Agents

| Agent | Role | Description |
|-------|------|-------------|
| **Chronos** | Orchestrator | Запускает циклы проверки |
| **Censor** | Truth Guard | Ищет противоречия и дубли |
| **Dewey** | Classifier | Классифицирует документы |
| **Veles** | Statistician | Подсчитывает связи |
| **Canon** | Truth Keeper | Генерирует эталонный документ |

## Document Hierarchy

```
Level 1: Contracts (machine truth)
    ↓
Level 2: Product Canon (human truth)
    ↓
Level 3: Engineering Canon (implementation truth)
    ↓
Level 4: Derived (synthesized)
    ↓
Level 5: Artifacts (generated)
    ↓
Level 6: Auxiliary (supporting)
```

## Example Output

```markdown
# Docs Audit Report

**Project:** /path/to/project
**Level:** L2
**Total docs:** 24

## Summary

| Severity | Count |
|----------|-------|
| Critical | 1 |
| Warning | 3 |
| Nit | 5 |
| **Total** | **9** |

## Issues

### CRITICAL

**File:** docs/API.md:42

Endpoint GET /users описан как Deprecated, но в контракте — Active.

**Fix:** Обновить docs/API.md согласно контракту
```

## Development

```bash
# Клонировать
git clone https://github.com/bestdeejay-design/chronos.git

# Установить
pip install -e .

# Тесты
python -m pytest tests/
```

## License

MIT License — see [LICENSE](LICENSE) for details.
