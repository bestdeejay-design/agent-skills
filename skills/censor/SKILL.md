# Censor — Страж Истины

> Проверяет документы на дубликаты и битые ссылки

## Что делает

- **Дубликаты** — находит документы с высокой схожестью (>70%)
- **Битые ссылки** — проверяет ссылки в markdown файлах
- Пропускает ссылки в code blocks и inline code
- Пропускает внешние ссылки (http, https, mailto)

## Использование

```bash
# Через Chronos агента
task(subagent_type="chronos", prompt="Проверь дубли и ссылки в /path/to/project", load_skills=["censor"])

# Или напрямую
PYTHONPATH=src python3 -c "from chronos.agents.censor import Censor; ..."
```

## Формат отчёта

```
[warning] duplicate: Высокая схожесть (85%) с docs/ROADMAP.md
[warning] broken_link: Битая ссылка: missing.md
```

## Пороги

- `duplicate_threshold = 0.7` — порог схожести для дубликатов
