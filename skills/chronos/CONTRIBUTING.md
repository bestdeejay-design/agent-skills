# Contributing to Chronos

Спасибо за интерес к проекту! Вот как можно внести вклад.

## Development Setup

```bash
# Клонировать репозиторий
git clone https://github.com/bestdeejay-design/chronos.git
cd chronos

# Установить в development mode
pip install -e .

# Запустить тесты
python -m pytest tests/
```

## Project Structure

```
src/chronos/
├── agents/          # AI-агенты
│   ├── base.py      # Базовый класс
│   ├── canon.py     # Оркестратор
│   ├── censor.py    # Проверка фактов
│   ├── chronos.py   # Хранитель времени
│   ├── dewey.py     # Классификатор
│   └── veles.py     # Статистик
├── core/            # Ядро
│   ├── reader.py    # Чтение файлов
│   └── reporter.py  # Генерация отчётов
└── cli.py           # CLI интерфейс
```

## Code Style

- Python 3.8+
- Type hints для всех функций
- Docstrings для публичных методов
- Форматирование через black

## Pull Requests

1. Fork проект
2. Создайте ветку `feature/your-feature`
3. Внесите изменения
4. Запустите тесты: `python -m pytest tests/`
5. Отправьте PR с описанием изменений

## Issues

- Используйте GitHub Issues
- Опишите проблему максимально подробно
- Укажите версию Python и ОС

## License

Лицензия MIT. Contributions лицензируются по MIT.
