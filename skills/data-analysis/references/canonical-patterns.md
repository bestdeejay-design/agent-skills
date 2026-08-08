# Canonical EDA Patterns

> Эталонные паттерны разведочного анализа данных (EDA) из канонических инструментов:
> ydata-profiling, sweetviz, DuckDB SUMMARIZE, D-Tale, skimr, DataExplorer.
> Справочник для расширения `scripts/data_analyze.py` и интерпретации его вывода.

## (a) Named analogues

### 1. ydata-profiling (бывш. pandas-profiling)
- **Owner**: ydataai
- **URL**: https://github.com/ydataai/ydata-profiling · docs: https://docs.profiling.ydata.ai/latest/
- **Type**: генератор HTML/JSON-отчётов с алертами качества данных (MIT)

Эталонная структура отчёта: **Overview** (Number of variables, Number of observations,
Missing cells (+%), Duplicate rows (+%), Total size in memory, Average record size in
memory), **Alerts**, **Variables**, **Interactions**, **Correlations**
(auto/spearman/pearson/kendall/cramers/phi_k), **Missing**, **Sample**, **Reproduction**.
Enum алертов: CONSTANT, ZEROS, HIGH_CORRELATION, HIGH_CARDINALITY, UNSUPPORTED,
DUPLICATES, NEAR_DUPLICATES, SKEWED, IMBALANCE, MISSING, INFINITE, TYPE_DATE, UNIQUE,
CONSTANT_LENGTH, REJECTED, UNIFORM, NON_STATIONARY, SEASONAL, EMPTY. Пороги (config.py):
quantiles [0.05, 0.25, 0.5, 0.75, 0.95]; cardinality_threshold=50 (high cardinality —
>50 уникальных); percentage_cat_threshold=0.5 (текст, если >50% значений уникальны);
imbalance_threshold=0.5; skewness_threshold=20; chi_squared_threshold=0.999 (uniform);
корреляции warn_high_correlations=10, threshold=0.5, n_bins=10; DUPLICATES при >10
дублирующихся строках; флаг memory_deep для точного memory_usage(). Пермалинки
(SHA 628d40088663790f54fa3d01733e2ecca1bf9338): config.py L38-L90, alerts.py L34-L94,
overview.py L19-L85, correlations_pandas.py L19-L78.

### 2. sweetviz
- **Owner**: fbdesignpro
- **URL**: https://github.com/fbdesignpro/sweetviz
- **Type**: целевой анализ и сравнение датасетов, HTML-приложение (MIT)

Target analysis (`analyze(df, target_feat=...)`), `compare()`/`compare_intra()`
(train vs test, группы), mixed-type ассоциации: Pearson (число-число), uncertainty
coefficient (категория-категория, асимметричен), correlation ratio (категория-число).
Принуждение типов: force_cat/force_num/force_text. Сводка: unique/missing/duplicate
rows, min/max/range, quartiles, mean, mode, std, sum, MAD, CV, kurtosis, skewness.

### 3. DuckDB SUMMARIZE
- **Owner**: duckdb
- **URL**: https://duckdb.org/docs/current/guides/meta/summarize.html
- **Type**: SQL-профилирование одной командой (MIT)

Вывод: column_name, column_type, min, max, approx_unique, avg, std, q25, q50, q75,
count, null_percentage. Квантили приблизительные (approx).

### 4. D-Tale
- **Owner**: man-group
- **URL**: https://github.com/man-group/dtale
- **Type**: интерактивный GUI-визуализатор pandas (Flask+React, LGPL-2.1)

Describe, Outlier Detection, Summarize Data, Duplicates, Missing Analysis,
Correlations, Predictive Power Score, Heat Map, Low Variance Flag (постоянные
колонки), Code Exports.

### 5. skimr (R)
- **Owner**: ropensci
- **URL**: https://github.com/ropensci/skimr
- **Type**: консольное профилирование по типам (MIT)

Numeric: n_missing, complete_rate, mean, sd, p0/p25/p50/p75/p100, hist (sparkline);
character: min, max, empty, n_unique, whitespace; factor: top_counts; list:
min_length/max_length.

### 6. DataExplorer (R)
- **Owner**: boxuancui
- **URL**: https://github.com/boxuancui/DataExplorer
- **Type**: автоматический HTML-отчёт + feature engineering (MIT)

`introduce()`: rows, columns, discrete_columns, continuous_columns,
all_missing_columns, total_missing_values, complete_rows, total_observations,
memory_usage; `create_report(y="target")` — отчёт с целевой переменной, QQ-плоты, PCA.

**Дополнительно**: PhiK (KaveIO/PhiK) — Phi_K корреляция смешанных типов
(число-категория, категория-категория); Great Expectations
(fivetran/great_expectations) — канонический словарь expectation'ов
(values_to_be_unique, proportion_of_non_null_values_to_be_between,
values_to_match_regex, quantile_values_to_be_between); AutoViz (AutoViML/AutoViz) —
«Automatically Visualize any dataset, any size with a single line of code».

> Честно: «viz-pg» и «activate» как публичные AutoEDA-инструменты не найдены
> (GitHub-поиск пуст). Ближайшие реальные кандидаты: AutoViz, D-Tale, pandasgui
> (adamerose/PandasGUI, MIT-0). datapane (datapane/datapane, Apache-2.0) официально EOL (финал 0.17.0).

## (b) Missing features vs canonicals

Чего нет в `scripts/data_analyze.py` (каждая строка — канон из (a)):

1. **Overview на уровне датасета**: Total size in memory, Average record size in
   memory (ydata overview.py; pandas `DataFrame.memory_usage(deep=True)`; DataExplorer memory_usage).
2. **Missing % и null_percentage**: ydata Missing cells (+%), DuckDB null_percentage,
   skimr complete_rate (1 − доля пропусков), DataExplorer total_missing_values.
3. **Skewness/kurtosis**: ydata SkewedAlert (skewness_threshold=20), sweetviz
   kurtosis/skewness, skimr.
4. **Monotonic flags**: ydata monotonic (числовые и timeseries).
5. **p_unique / uniqueness ratio**: ydata p_unique; percentage_cat_threshold=0.5
   (текст при >50% уникальных); GE proportion_of_unique_values_to_be_between.
6. **MAD**: ydata mad, sweetviz median absolute deviation.
7. **Infinite counters**: ydata n_infinite/p_infinite, INFINITE alert.
8. **High-cardinality threshold**: ydata cardinality_threshold=50 (HIGH_CARDINALITY).
9. **Imbalance check**: ydata imbalance_threshold=0.5 (IMBALANCE alert).
10. **Categorical chi-squared/uniformity**: ydata chi_squared_threshold=0.999
    (UNIFORM alert); Cramér's V на chi2_contingency (correlations_pandas.py).
11. **Boolean dtype detection**: ydata typeset-иерархия (Boolean, Numeric, Date,
    Categorical, TimeSeries, URL, Path, File, Image).
12. **Sample first/last rows**: ydata Sample (первые/последние N строк).
13. **Near-duplicates**: ydata NEAR_DUPLICATES (fuzzy) — дорого (попарное сравнение),
    advisory.
14. **Spearman/Kendall кроме Pearson**: ydata auto (spearman по умолчанию для чисел),
    pandas `df.corr(method=...)`, scipy spearmanr (монотонность; ConstantInputWarning
    на константных колонках — выводите «constant» алерт, а не NaN). Scope: Spearman —
    нелинейно-монотонные связи, Kendall — ранговые, корректны при связях (ties);
    stdlib-эквивалент Spearman = Pearson на рангах.
15. **Predictive-power-style hints**: D-Tale Predictive Power Score; ydata
    HIGH_CORRELATION (warn_high_correlations=10, threshold=0.5) — advisory, без
    обучения моделей.

## (c) Citable CLI/API examples

```bash
# DuckDB CLI — профилирование таблицы одной командой
duckdb -c "SUMMARIZE SELECT * FROM read_csv_auto('data.csv');"

# ydata-profiling — отчёт в файл
python -c "from ydata_profiling import ProfileReport; ProfileReport(df).to_file('report.html')"

# sweetviz — целевой анализ
python -c "import sweetviz as sv; sv.analyze(df, target_feat='price').show_html('report.html')"

# D-Tale — интерактивный просмотр
python -c "import dtale; dtale.show(df)"

# Great Expectations — валидация
python -c "import great_expectations as gx; gx.validate(...)"
```

## (d) Cost guidance

Дешёвое и stdlib-реализуемое: duplicates, missing %, квантили
(`statistics.quantiles`), skewness/kurtosis (формулы), p_unique, MAD,
infinite-счётчики, boolean-детекция, порог кардинальности 50, sample-строки,
Spearman (Pearson на рангах). Вне скоупа: HTML/GUI-отчёты (ydata/sweetviz/D-Tale),
тяжёлые корреляции (Cramér's V, phi_k, полные матрицы), near-duplicates и
embeddings/PCA — требуют scipy/pandas и не нужны для текстового профиля.