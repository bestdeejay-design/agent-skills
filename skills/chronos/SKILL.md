# Chronos — Documentation Timekeeper

> AI-агент для поддержания целостности документации

## Что делает

Chronos проверяет документацию проекта на:

- **Дубликаты** — документы с высокой схожестью
- **Битые ссылки** — ссылки на несуществующие файлы
- **Отсутствующие документы** — обязательные файлы для уровня
- **Сироты** — документы без ссылок на них
- **Классификация** — тип документа (канон/производный/артефакт)
- **Устаревшие данные** — даты старше порога

## Использование

```bash
# Базовый аудит (только дубли + ссылки)
chronos --path .

# С классификацией
chronos --path . --preset standard

# Полный Пантеон
chronos --path . --preset full

# Только JSON
chronos --path . --output json --output-file report.json

# Фейл при ошибках
chronos --path . --fail-on critical
```

## Пресеты

| Пресет | Агенты | Описание |
|--------|--------|----------|
| `minimal` | Censor | Базовый: дубли + ссылки |
| `standard` | Censor + Dewey + Canon | Проверка + классификация |
| `full` | Все агенты | Полный Пантеон |

## Агенты

| Агент | Роль |
|-------|------|
| **Chronos** | Оркестратор |
| **Censor** | Проверка фактов |
| **Dewey** | Классификатор |
| **Veles** | Статистик |
| **Canon** | Хранитель правды |

## Установка

```bash
pip install chronos
```

## Иерархия документов

```
L1: Contracts (машинная правда)
L2: Product Canon (человеческая правда)
L3: Engineering Canon (правда реализации)
L4: Derived (синтезированные)
L5: Artifacts (сгенерированные)
L6: Auxiliary (вспомогательные)
```

## Пример вывода

```markdown
# Docs Audit Report

**Project:** /path/to/project
**Total docs:** 24

| Severity | Count |
|----------|-------|
| Critical | 1 |
| Warning | 3 |
| **Total** | **4** |

### CRITICAL

**File:** docs/API.md:42
Endpoint GET /users описан как Deprecated, но в контракте — Active.
**Fix:** Обновить docs/API.md согласно контракту
```

## Триггеры

- "проверь документацию"
- "docs audit"
- "audit docs"
- "docs integrity"
- "найди дубли в доках"
- "битые ссылки"
- "broken links"
- "docs check"
- "хронос"

## Файлы

```
skills/chronos/
├── SKILL.md
├── src/chronos/           # Python пакет
├── tests/                 # 67 pytest тестов
├── presets/               # JSON пресеты
└── pyproject.toml
```
