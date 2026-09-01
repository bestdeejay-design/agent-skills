# Dewey — Классификатор

> Определяет тип и уровень документа в иерархии правды

## Иерархия

| Уровень | Тип | Примеры |
|---------|-----|---------|
| L1 | Contracts | `contracts/openapi/*.yaml` |
| L2 | Product Canon | `docs/VISION.md`, `docs/PRD.md` |
| L3 | Engineering Canon | `docs/ARCHITECTURE.md`, `docs/ADR/` |
| L4 | Derived | `README.md`, `docs/STATUS.md` |
| L5 | Artifacts | Сгенерированные файлы |
| L6 | Auxiliary | `LICENSE`, `CONTRIBUTING.md` |

## Что делает

- Классифицирует каждый документ по типу
- Определяет уровень проекта (L1-L3)
- Проверяет обязательные документы для уровня

## Использование

```bash
# Через Chronos агента
task(subagent_type="chronos", prompt="Классифицируй документы в /path/to/project", load_skills=["dewey"])
```

## Формат отчёта

```
[warning] missing: Отсутствует обязательный документ для L2 — docs/ROADMAP.md
```
