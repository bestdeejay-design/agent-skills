---
name: csv-pro
description: "Профилирование CSV-файлов: типы колонок, статистика, аномалии. Скрипт csv_pro.py читает CSV (файл --input или stdin --stdin), определяет разделитель (по умолчанию ';', затем ','), для каждой колонки считает тип (int/float/str/date), min/max/mean, пропуски, уникальные значения и топ-3 частых. Ищет аномалии: нулевая дисперсия, >95% пустых, дубликаты строк, строки длиннее 1000 символов, выбросы (значение ≥ 5×IQR от медианы). Вывод: markdown-таблица (по умолчанию), JSON или HTML с графиками. Триггеры: 'csv profile', 'профиль csv', 'анализ csv', 'csv анализ', 'аномалии csv', 'csv anomalies', 'профилирование csv', 'что в csv'."
license: MIT
metadata:
  author: best
  version: 1.1.0
compatibility: "Requires Python 3 stdlib (csv, statistics, datetime)"
when_to_use: "Use when profiling a CSV file: column types, stats, anomalies. Triggers: 'csv profile', 'профиль csv', 'анализ csv', 'csv anomalies', 'что в csv', 'профилирование csv'. Example: 'профилируй data.csv и найди аномалии'."
---

# CSV Pro

> Профилирование CSV-файлов: типы колонок, статистика, аномалии.

Загружай этот скилл когда нужно **быстро понять, что лежит в CSV**:
типы колонок, диапазоны значений, пропуски, дубликаты и выбросы.

## 🎯 When to use

Use this skill when:
- Есть CSV-файл и нужно понять его структуру: типы колонок, min/max/mean, уникальные значения
- Нужно проверить качество данных перед загрузкой в БД или ML-пайплайн
- Просят «профиль csv», «анализ csv», «что в csv», «csv anomalies»
- Нужен отчёт об аномалиях: пустые колонки, дубликаты строк, выбросы, длинные строки

Do NOT use when:
- Нужна полная аналитика с корреляциями и рекомендациями — это `data-analysis`
- Нужны SQL-запросы к данным — это `sql-helper`
- Нужно просто посчитать строки или суммы — проще `wc -l` и `awk`

## 📦 Files

- `SKILL.md` — этот файл
- `scripts/csv_pro.py` — профилировщик CSV (Python 3 stdlib)

## 🧰 Usage

```bash
# Файл → markdown-профиль (по умолчанию):
python3 skills/csv-pro/scripts/csv_pro.py --input data.csv

# Файл → JSON:
python3 skills/csv-pro/scripts/csv_pro.py --input data.csv --output json

# Файл → HTML с графиками:
python3 skills/csv-pro/scripts/csv_pro.py --input data.csv --output html

# Из stdin (текст прямо в пайплайне):
cat data.csv | python3 csv_pro.py --stdin

# Явный разделитель:
python3 csv_pro.py --input data.csv --delimiter ';'
```

## Canonical analogues

Полный справочник канонических паттернов — `references/canonical-patterns.md`.
Топ-аналоги и их takeaways:

- **ydata-profiling** — эталонный набор метрик (skewness, kurtosis, quantiles, MAD, infinite counters) и 18 типов алертов.
- **csvkit csvstat** — CLI-эталон: `csvstat data.csv --json`, метрики `len` и `maxprecision`.
- **DuckDB SUMMARIZE** — SQL-профиль с approx-квантилями и `null_percentage`.
- **Great Expectations** — словарь проверяемых утверждений (63 core-ожидания).
- **dataprep.EDA** — типизированные инсайты: Zeros, Negatives, Constant Length, High Cardinality.

## 🔬 Проверка результата

- Markdown: таблица «Колонки» (тип, уникальные, пустые, min/max/mean, топ-3) + секция «Аномалии».
- JSON: валидный JSON с полями `columns` и `anomalies` — проверка `python3 -m json.tool`.
- HTML: интерактивный дашборд с гистограммами для числовых колонок и bar charts для категорий.
- Пустой файл: сообщение «Файл пуст», код 0.
- Отсутствующий файл: сообщение в stderr, код 1.