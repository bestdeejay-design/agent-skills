---
name: data-analysis
description: "Профилирование датасета (CSV или JSON-массив объектов): типы полей, статистика (count/unique/missing, min/max/mean/std), мода и топ-N значений, гистограмма 5 корзин для чисел, топ-3 парные корреляции Пирсона, аномалии и рекомендации. Скрипт data_analyze.py читает --input и выводит отчёт в markdown (по умолчанию) или JSON. Триггеры: 'data analysis', 'анализ данных', 'профиль датасета', 'статистика данных', 'dataset анализ', 'почитать данные', 'data profiling', 'разведочный анализ', 'eda'."
license: MIT
metadata:
  author: best
  version: 1.0.0
compatibility: "Requires Python 3 stdlib (json, csv, statistics, collections)"
---

# Data Analysis

> Профилирование датасета: статистика полей, корреляции, аномалии и рекомендации.

Загружай этот скилл когда нужно **разобраться в данных**: понять типы полей,
распределения, пропуски, корреляции между числовыми полями и что стоит почистить
перед анализом или моделированием.

## 🎯 When to use

Use this skill when:
- Есть CSV или JSON-массив объектов и нужен профиль датасета (EDA)
- Нужно понять типы полей, пропуски, распределения и выбросы
- Просят «проанализировать данные», «почитать данные», «сделать EDA»
- Нужны корреляции между числовыми полями и рекомендации по очистке данных

Do NOT use when:
- Нужен SQL-запрос к базе данных — это `sql-helper`
- Нужна обработка CSV как таблицы (фильтры, join, преобразования) — это `csv-pro`
- Нужны графики/визуализации — скрипт выдаёт текстовый отчёт (markdown/JSON), не картинки

## 📦 Files

- `SKILL.md` — этот файл
- `scripts/data_analyze.py` — профилировщик датасета (Python 3 stdlib)
- `references/canonical-patterns.md` — эталонные EDA-паттерны канонических инструментов

## Canonical analogues

Эталонные EDA-паттерны и gap-анализ скрипта против канонических инструментов —
в `references/canonical-patterns.md`. Топ-аналоги:

- **ydata-profiling** — эталонная структура отчёта (Overview/Alerts/Variables/Correlations/Missing/Sample) и алерты качества с порогами.
- **sweetviz** — целевой анализ (target_feat) и mixed-type ассоциации (uncertainty coefficient, correlation ratio).
- **DuckDB SUMMARIZE** — профилирование одной SQL-командой: min/max/approx_unique/avg/std/q25/q50/q75/null_percentage.
- **D-Tale** — интерактивный GUI: Describe, Outlier Detection, Duplicates, Missing Analysis, Predictive Power Score.
- **skimr / DataExplorer (R)** — консольное профилирование по типам и метрики introduce() (memory_usage, complete_rows).

## 🧰 Usage

```bash
# CSV → markdown-отчёт (по умолчанию):
python3 skills/data-analysis/scripts/data_analyze.py --input data.csv

# JSON-массив объектов → markdown-отчёт:
python3 skills/data-analysis/scripts/data_analyze.py --input data.json

# JSON-отчёт (для программного использования):
python3 skills/data-analysis/scripts/data_analyze.py --input data.csv --output json

# Топ-5 значений вместо 10 и свой заголовок:
python3 skills/data-analysis/scripts/data_analyze.py --input data.csv --top 5 --title "Продажи 2026"
```

## 🔬 Проверка результата

- Markdown-отчёт содержит секции: **Размер**, **Типы**, **Статистика**, **Корреляции**, **Аномалии**, **Рекомендации**.
- JSON-отчёт — зеркало тех же секций: ключи `rows`, `fields`, `correlations`, `anomalies`, `recommendations`.
- Числовые поля: min/max/mean/std, медиана, мода, топ-N значений, гистограмма из 5 корзин.
- Корреляции: таблица 3 сильнейших парных коэффициентов Пирсона (по полным парам, без numpy).
- Аномалии: разреженные (>90% пропусков), нулевая дисперсия, высокая кардинальность строк, правосторонний перекос.
- При неисправимой ошибке (файл не найден, невалидный JSON, пустой датасет) скрипт пишет причину в stderr
  и завершается с кодом 1; предупреждения (смешанный тип поля, пропущенные элементы) работу не прерывают.
