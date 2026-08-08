# Canonical patterns

Справочник по каноническим паттернам профилирования CSV: аналоги `csv_pro.py`,
метрики, которых скрипту не хватает, эталонные CLI/API-примеры и маппинг на
измерения качества данных (DAMA DMBOK / ISO 8000).

## (a) Named analogues

| Name | Owner | URL | Type |
|---|---|---|---|
| ydata-profiling | ydataai | https://github.com/ydataai/ydata-profiling | Python library |
| Great Expectations | great-expectations | https://github.com/great-expectations/great_expectations | Python library / validation framework |
| csvkit (csvstat) | wireservice | https://github.com/wireservice/csvkit | CLI tool |
| dataprep.EDA | sfu-db | https://github.com/sfu-db/dataprep | Python library |
| DuckDB SUMMARIZE | DuckDB | https://duckdb.org/docs/stable/guides/meta/summarize.html | SQL function |
| OpenRefine | OpenRefine | https://github.com/OpenRefine/OpenRefine | GUI tool |

- **ydata-profiling** — де-факто стандарт профилирования таблиц: генерирует HTML-отчёт
  с унивариантными метриками (mean, std, variance, min, max, kurtosis, skewness, sum,
  quantiles 25/50/75%, iqr, range, mad, n_infinite/p_infinite, monotonic_increase/
  decrease, histogram), категориальными (length_histogram, chi_squared, first_rows)
  и алертами enum из 18 типов: CONSTANT, CONSTANT_LENGTH, DUPLICATES, NEAR_DUPLICATES,
  EMPTY, HIGH_CARDINALITY, DIRTY_CATEGORY, HIGH_CORRELATION, IMBALANCE, INFINITE,
  MISSING, NON_STATIONARY, SEASONAL, SKEWED, TYPE_DATE, UNIFORM, UNIQUE, UNSUPPORTED.
- **Great Expectations** — фреймворк валидации данных: 63 core-ожидания вида
  `column_mean_to_be_between`, `column_median_to_be_between`, `column_min/max/sum/
  stdev_to_be_between`, `column_quantile_values_to_be_between`,
  `proportion_of_unique_values_to_be_between`, `values_to_be_unique`,
  `proportion_of_non_null_values_to_be_between`, `values_to_match_regex`,
  `values_to_be_in_set`, `values_to_be_dateutil_parseable`, `values_to_be_json_parseable`,
  `value_lengths_to_be_between`, `values_to_be_increasing/decreasing`.
- **csvkit csvstat** — CLI-профилировщик одной командой: OPERATIONS = type, nulls,
  nonnulls, unique, min, max, sum, mean, median, stdev, len (длина самого длинного
  значения), maxprecision (максимум знаков после запятой), freq (частотная таблица).
  Флаги `--json` / `--csv` / `--indent` — эталон для машинного вывода.
- **dataprep.EDA** — EDA-библиотека с типизированными инсайтами: Duplicates, Similar
  Distribution, Uniform, Missing, Skewed, Infinity, Zeros, Negatives, Normal,
  High Cardinality, Constant, Constant Length, Unique; skew/kurtosis считает через
  scipy.stats.
- **DuckDB SUMMARIZE** — SQL-профиль таблицы: column_name, column_type, min, max,
  approx_unique, avg, std, q25, q50, q75, count, null_percentage (approx-квантили).
  Самый дешёвый способ профилировать большие файлы.
- **OpenRefine** — GUI-only (facets, clustering); упоминается как альтернатива для
  интерактивной очистки, не как замена CLI-профилировщику.

## (b) Metrics the script is MISSING

Скрипт сейчас считает: тип колонки, min/max/mean, пропуски, уникальные значения,
топ-3 частых, аномалии (нулевая дисперсия, >95% пустых, дубликаты строк, строки
длиннее 1000 символов, выбросы ≥ 5×IQR). Чего не хватает относительно канонов:

| Metric | Canonical source | Notes |
|---|---|---|
| skewness, kurtosis | ydata-profiling, dataprep.EDA (scipy.stats) | stdlib `statistics` не даёт — нужен scipy или ручная формула |
| std / variance | ydata-profiling, csvkit, DuckDB SUMMARIZE | std есть в stdlib `statistics` |
| q25 / q50 / q75 + IQR | ydata-profiling, DuckDB SUMMARIZE | скрипт использует IQR только для выбросов, квантили не выводит |
| uniqueness ratio (unique/count) | ydata-profiling `p_unique`, GE `proportion_of_unique_values_to_be_between` | сейчас только абсолютное число уникальных |
| null_percentage | DuckDB SUMMARIZE, GE `proportion_of_non_null_values_to_be_between` | сейчас только счёт пропусков |
| mad (median absolute deviation) | ydata-profiling | робастная альтернатива std |
| n_infinite / p_infinite | ydata-profiling, dataprep.EDA (Infinity) | счётчик inf в float-колонках |
| zeros / negatives ratios | dataprep.EDA (Zeros, Negatives) | доли нулей и отрицательных значений |
| monotonic_increase / monotonic_decrease | ydata-profiling | флаги монотонности |
| max value length / length histogram / constant length | csvkit `len`, ydata-profiling `length_histogram`, dataprep.EDA (Constant Length) | сейчас только порог 1000 символов |
| maxprecision (most decimal places) | csvkit | точность float-колонок |
| boolean dtype hint | ydata-profiling, dataprep.EDA | колонка из 0/1 или true/false |
| first_rows sample | ydata-profiling | пример значений для категориальных колонок |
| sum | csvkit, GE `column_sum_to_be_between` | тривиально, но полезно |
| high-cardinality alert | ydata-profiling HIGH_CARDINALITY | unique/count выше порога |
| imbalance alert | ydata-profiling IMBALANCE | одна категория доминирует |

## (c) Citable CLI/API examples

```bash
# csvkit: полный профиль одной командой, JSON-вывод
csvstat data.csv
csvstat data.csv --json

# DuckDB: SQL-профиль с approx-квантилями
duckdb -c "SUMMARIZE SELECT * FROM read_csv_auto('data.csv');"

# Great Expectations: валидация ожиданий
gx.validate(...)

# ydata-profiling: HTML-отчёт
from ydata_profiling import ProfileReport
ProfileReport(df).to_file("report.html")
```

## (d) DAMA dimension mapping

Метрики скрипта ложатся на стандартные измерения качества данных (DAMA DMBOK,
ISO 8000): **completeness** — пропуски и null_percentage; **uniqueness** — число
уникальных и их доля; **validity** — типы колонок, диапазоны, формат дат;
**accuracy** — выбросы (≥5×IQR), min/max против ожидаемого диапазона;
**consistency** — дубликаты строк, константные колонки, монотонность.
Ограничение: **timeliness** (свежесть данных) требует семантики временных меток
(что считать «сейчас» и период актуальности), поэтому скрипт её не покрывает —
это осознанный out-of-scope.

**Cost guidance**: дёшево добавить на stdlib — std/variance, q25/q50/q75, sum,
uniqueness ratio, null_percentage, zeros/negatives ratios, max value length,
first_rows, high-cardinality/imbalance алерты. Дорого или out-of-scope —
корреляции, near-duplicates, chi-squared, гистограммы: требуют scipy/numpy или
специализированных библиотек (ydata-profiling, dataprep) — оставлять как
advisory-ссылку, а не реализацию.