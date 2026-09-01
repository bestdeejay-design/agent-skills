# PRD — Docs Pantheon

> Что мы строим и зачем

## Goals

### Primary Goals
1. **Обнаружение дублей** — найти документы с >70% схожестью
2. **Поиск противоречий** — выявить факты, которые расходятся
3. **Проверка ссылок** — найти битые ссылки на документы
4. **Классификация** — определить тип документа (канон/производный/артефакт)
5. **Статистика** — подсчитать связи и зависимости

### Non-Goals
1. **Генерация документов** — мы проверяем, не создаём
2. **Стиль** — это ответственность линтеров (markdownlint)
3. **Перевод** — мы работаем с содержимым, не с языком
4. **Рефакторинг** — мы рекомендуем, не исправляем

## User Stories

### Story 1: Solo-dev проверяет документы
**Как** разработчик с 1 проектом,
**Хочу** проверить документацию на консистентность,
**Чтобы** быть уверенным, что документы актуальны.

**Приёмочные критерии:**
- Запуск: `python3 -m chronos --path .`
- Отчёт: JSON + Markdown
- Время: < 30 секунд на проект

### Story 2: Команда интегрирует в CI
**Как** DevOps-инженер,
**Хочу** автоматически проверять документы при пуше,
**Чтобы** ловить проблемы до мержа.

**Приёмочные критерии:**
- Exit code: 0 (чисто), 1 (проблемы), 2 (ошибка)
- JSON-отчёт для парсинга
- Флаг `--fail-on critical` для CI

### Story 3: Tech Writer аудиторует большой проект
**Как** технический писатель,
**Хочу** получить полную картину по документации,
**Чтобы** понять, что исправлять в первую очередь.

**Приёмочные критерии:**
- Карта документов с типами
- Список проблем по приоритету
- Рекомендации по исправлению

## Functional Requirements

### FR-1: Discovery (обнаружение)
- Рекурсивный обход `.md` файлов
- Исключение скрытых директорий (`.git`, `.github`)
- Чтение YAML-контрактов (`contracts/**/*.yaml`)

### FR-2: Classification (классификация)
Определение типа документа по паттернам:

| Паттерн | Тип | Уровень |
|---------|-----|---------|
| `contracts/openapi/*.yaml` | contracts | L1 |
| `docs/VISION.md`, `docs/PRD.md` | product_canon | L2 |
| `docs/ARCHITECTURE.md`, `docs/ADR/*.md` | engineering_canon | L3 |
| `README.md`, `ENTRY.md`, `docs/STATUS.md` | derived | L4 |
| `docs/api/*.md`, `docs/generated/*.md` | artifacts | L5 |
| `LICENSE`, `CONTRIBUTING.md` | auxiliary | L6 |

### FR-3: Duplicate Detection (поиск дублей)
- Алгоритм: SequenceMatcher (Python stdlib)
- Порог: >0.7 = подозрение на дубль
- Вывод: пара файлов + процент схожести

### FR-4: Contradiction Detection (противоречия)
- Извлечение фактов (предложения с глаголами)
- Сравнение фактов между документами
- Учёт иерархии правды

### FR-5: Broken Links (битые ссылки)
- Парсинг ссылок вида `[text](path)`
- Разрешение относительных путей
- Проверка существования файлов

### FR-6: Orphan Detection (сироты)
- Документы без ссылок на них
- Исключение обязательных документов
- Проверка наличия в REFERENCE.md/ENTRY.md

### FR-7: Missing Documents (пропущенные)
- Проверка обязательных документов для уровня
- L1: README, ARCHITECTURE, STATUS
- L2: + VISION, PRD, ROADMAP, REFERENCE, ENTRY

### FR-8: Stale Detection (устаревшие)
- Сравнение времён модификации
- Проверка производных после канонических
- Поиск упоминаний устаревших терминов

## Non-Functional Requirements

### NFR-1: Performance
- Время выполнения: < 30 секунд на проект до 1000 файлов
- Потребление памяти: < 100 МБ

### NFR-2: Compatibility
- Python 3.8+
- Зависимости: только stdlib (argparse, json, pathlib, re, hashlib, difflib)
- ОС: macOS, Linux, Windows

### NFR-3: Usability
- CLI с понятными флагами
- Отчёт на русском и английском
- Exit code совместим с CI

### NFR-4: Extensibility
- Каждый агент — отдельный модуль
- Пресеты для выбора набора агентов
- Кастомные проверки через плагины

## Architecture

### Модули

```
chronos/
├── __init__.py
├── __main__.py           # CLI entry point
├── core/
│   ├── __init__.py
│   ├── reader.py         # Чтение файлов
│   ├── classifier.py     # Классификация
│   └── reporter.py       # Генерация отчётов
├── agents/
│   ├── __init__.py
│   ├── base.py           # Базовый класс агента
│   ├── censor.py         # Проверка фактов
│   ├── dewey.py          # Классификация
│   ├── veles.py          # Статистика
│   ├── chronos.py        # Время
│   └── canon.py          # Оркестратор
├── presets/
│   ├── minimal.json      # Только Censor
│   ├── standard.json     # Censor + Dewey + Canon
│   └── full.json         # Полный Пантеон
└── cli.py                # CLI интерфейс
```

### Агенты

| Агент | Метод | Возвращает |
|-------|-------|------------|
| **Censor** | `check(docs, context)` | List[Issue] |
| **Dewey** | `classify(docs)` | Dict[str, DocType] |
| **Veles** | `analyze(docs, context)` | Stats |
| **Chronos** | `check_staleness(docs)` | List[Issue] |
| **Canon** | `orchestrate(docs, preset)` | Report |

### Data Flow

```
[Input: path to project]
        ↓
[Reader: collect .md + .yaml files]
        ↓
[Dewey: classify each document]
        ↓
[Veles: count links, find orphans]
        ↓
[Censor: check duplicates, contradictions]
        ↓
[Chronos: check staleness]
        ↓
[Canon: aggregate, prioritize]
        ↓
[Reporter: JSON + Markdown output]
```

## Success Metrics

| Metric | Target | How to measure |
|--------|--------|----------------|
| Detection rate | > 90% | Manual audit on 5 test projects |
| False positive rate | < 10% | Manual review of flagged issues |
| Execution time | < 30s | Benchmark on 1000-file project |
| User satisfaction | > 4/5 | Survey after 1 month |

## Milestones

### v1.0 — Censor (базовый аудит)
- [ ] Duplicate detection
- [ ] Broken links
- [ ] Missing documents
- [ ] JSON + Markdown output

### v1.1 — Dewey (классификация)
- [ ] Document classification
- [ ] Dependency tree
- [ ] Type validation

### v1.2 — Veles (статистика)
- [ ] Link analysis
- [ ] Orphan detection
- [ ] Coverage metrics

### v1.3 — Chronos (время)
- [ ] Staleness detection
- [ ] Archive recommendations
- [ ] Timeline tracking

### v2.0 — Canon (оркестратор)
- [ ] Chain of Responsibility
- [ ] Presets
- [ ] Plugin system

---

*PRD created: 2026-09-01*
*Author: best*
