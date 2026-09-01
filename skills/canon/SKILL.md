# Canon — Хранитель Ритуала

> Оркестрирует саб-агентов через пресеты

## Пресеты

| Пресет | Агенты | Описание |
|--------|--------|----------|
| minimal | Censor | Только дубли и ссылки |
| standard | Censor + Dewey | + классификация |
| full | Все 5 | Полный Пантеон |

## Использование

```bash
# Через Chronos агента
task(subagent_type="chronos", prompt="Запусти полный аудит /path/to/project", load_skills=["canon"])

# Или напрямую
PYTHONPATH=src python3 -c "from chronos.agents.canon import Canon; ..."
```

## Как работает

1. Canon получает пресет (minimal/standard/full)
2. Определяет какие агенты нужны
3. Запускает их последовательно
4. Агрегирует отчёты в единый результат
