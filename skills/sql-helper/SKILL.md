---
name: sql-helper
description: "Генерация SQL по текстовому вопросу и DDL-схеме. Скрипт sql_helper.py читает DDL-файл, строит in-memory схему в sqlite3, распознаёт слова вопроса по таблицам/колонкам и собирает SQL по шаблонам интентов (select, join, where, group, order, count, limit). Каждый кандидат проверяется через EXPLAIN, при --explain выводится читаемый план запроса. Триггеры: 'sql helper', 'sql генерация', 'сгенерируй sql', 'explain запроса', 'sql запрос', 'напиши sql', 'formatted sql', 'sql formatting'."
license: MIT
metadata:
  author: best
  version: 1.0.0
compatibility: "Requires Python 3 stdlib (argparse, sqlite3)"
---

# SQL Helper

> Генерация SQL-запросов из текстового вопроса и DDL-схемы.

Загружай этот скилл когда нужно **превратить вопрос на естественном языке в SQL**:
для быстрых запросов к базе, разбора плана выполнения или форматирования SQL.

## 🎯 When to use

Use this skill when:
- Есть DDL-файл (CREATE TABLE) и вопрос, по которому нужен SQL-запрос
- Нужно быстро собрать SELECT/JOIN/GROUP BY/COUNT по шаблону
- Просят «сгенерируй sql», «напиши sql», «sql запрос», «sql helper»
- Нужно посмотреть план выполнения запроса (EXPLAIN) в читаемом виде

Do NOT use when:
- Нужна только проверка синтаксиса без схемы — достаточно обычного редактора
- Нужна миграция или генерация DDL — это отдельный инструмент
- Вопрос не про SQL (анализ данных, CSV, скрейпинг) — это другие скиллы

## 📦 Files

- `SKILL.md` — этот файл
- `scripts/sql_helper.py` — генератор SQL + EXPLAIN (Python 3 stdlib)

## 🧰 Usage

```bash
# Сгенерировать SQL по вопросу:
python3 skills/sql-helper/scripts/sql_helper.py --ddl schema.sql --question "select users by id"

# С планом выполнения:
python3 skills/sql-helper/scripts/sql_helper.py --ddl schema.sql --question "count orders by user" --explain

# JOIN двух таблиц:
python3 skills/sql-helper/scripts/sql_helper.py --ddl schema.sql --question "join users and orders"

# С лимитом и сортировкой:
python3 skills/sql-helper/scripts/sql_helper.py --ddl schema.sql --question "top 5 orders by date desc"
```

## 🔬 Проверка результата

- Скрипт выводит сгенерированный SQL в stdout и завершается с кодом 0.
- При `--explain` после SQL печатается секция `--- query plan ---` с планом.
- Пустой вопрос или невалидный DDL — сообщение в stderr и код выхода 1.