# Canonical patterns: text-to-SQL analogues of sql-helper

Сводка канонических реализаций text-to-SQL (проверено по GitHub, август 2026) и
разбор того, что скрипт `sql_helper.py` уже делает, а что — нет. Ни в одной из
крупных коллекций скиллов (anthropics/skills, obra/superpowers, vercel-labs/skills,
trailofbits/skills) SQL-скилла нет — sql-helper закрывает реальный пробел; его
структура SKILL.md уже следует шаблону Anthropic.

## (a) Named analogues

### 1. Anthropic Cookbook — Text-to-SQL capability
- **Owner**: Anthropic · **URL**: https://github.com/anthropics/anthropic-cookbook/tree/main/capabilities/text_to_sql · **License**: MIT

Официальная capability: `guide.ipynb` (промптинг, self-improvement, RAG),
`data/data.db`, `evaluation/` — promptfoo-харнесс (`promptfooconfig.yaml`,
`prompts.py`, `tests/*.py`, `vectordb.py`). Каноническая интроспекция схемы —
`SELECT name FROM sqlite_master WHERE type='table'` + `PRAGMA table_info(tbl)`
(идентично нашему `load_schema()`), кандидаты оборачиваются в `<sql>…</sql>`
теги, валидация — исполнение SQL против sqlite-файла и сравнение результатов
(execution-based validation, «assert text match» стиль).

### 2. sqlsure / sql-semantic-check
- **Owner**: sqlsure (sqlsure.ai) · **URL**: https://github.com/sqlsure/sqlsure · скилл: https://github.com/sqlsure/sqlsure/blob/main/skills/sql-semantic-check/SKILL.md · **License**: —

Детерминированный семантический инспектор SQL (0.1 мс, офлайн, без доступа к
БД), поставляется как Agent Skill. Правила: FANOUT, CHASM, ADDITIVITY, JOIN_KEY,
CROSS_JOIN, WEIGHTED_AVG, UNDECLARED_JOIN, SENSITIVE_COLUMN. Интроспекция
`model_from_sqlite()` (PK → grain, FK → join edges). Аудит золотых ответов
BIRD/Spider: 2568 запросов, 45 флагов, ноль ложных срабатываний. Цикл
draft → check → fix → check → execute; «never suppress an error by editing the
rulebook».

### 3. Vanna.ai
- **Owner**: Vanna AI · **URL**: https://github.com/vanna-ai/vanna (23.8k★) · **License**: MIT

Открытая библиотека text-to-SQL: train() на DDL + документации + (вопрос, SQL)-
парах, Information Retrieval похожих пар как few-shot (`get_similar_question_sql`),
затем generate_sql → run_sql → verify. В 2.0 — агентная архитектура: SQL
исполняется только через `RunSqlTool` + `SqliteRunner` с row-level security
(паттерн «generate freely, execute gated»), жизненный цикл с хуками и лимитами.

### 4. Benchmarks: Spider, BIRD, Spider 2.0 + prompt-фреймворки
- **Spider**: https://github.com/Yale-LILY/spider (официальный репо жив; `taoyang/Spider` мёртв, 404)
- **BIRD**: https://github.com/bird-bench/mini_dev · **Spider 2.0**: https://github.com/xlang-ai/Spider2
- **DAIL-SQL**: https://github.com/BeachWang/DAIL-SQL · **MAC-SQL**: https://github.com/wbbeyourself/MAC-SQL · **DIN-SQL**: arXiv:2304.11015 (репо мёртв)
- **License**: —

Каноническая методология оценки: exact match (AST через `process_sql.py`),
execution accuracy (исполнить и сравнить результат), validity + efficiency
(BIRD). Schema linking как отдельный первый этап (DIN-SQL/DAIL-SQL, masked
schema linking); self-correction с фидбеком от исполнения (MAC-SQL refiner).
Таксономия типов вопросов из SQLCoder (https://github.com/defog-ai/sqlcoder):
`date, group_by, order_by, ratio, join, where`.

### 5. sqlite-utils + SQLGlot
- **sqlite-utils**: simonw · https://github.com/simonw/sqlite-utils · CLI-доки: https://sqlite-utils.datasette.io/en/stable/cli.html · **License**: Apache-2.0
- **SQLGlot**: tobymao · https://github.com/tobymao/sqlglot · **License**: MIT

sqlite-utils — канон CLI-интроспекции SQLite: `schema`, `analyze` (статистика
для планировщика), `memory` (in-memory БД — прямой аналог нашего подхода),
`tables --csv --no-headers`. SQLGlot — канонический ответ на квотинг
идентификаторов: `transpile(..., quote_identifiers=True)` — идентификаторы,
совпадающие с зарезервированными словами, обязаны быть в двойных кавычках.

### 6. grok-sqlite-explain
- **Owner**: asutherland · **URL**: https://github.com/asutherland/grok-sqlite-explain · **License**: —

Парсит вывод SQLite EXPLAIN и строит дерево запроса. Канонический факт: строки
EXPLAIN QUERY PLAN — это `(id, parent, notused, detail)`, и правильная глубина
дерева строится по ссылкам `parent`, а не по самому `id`. Прямой аналог нашего
`format_plan()`.

## (b) Techniques the script is MISSING

| # | Technique (source) | Where in code | Fix without dependencies |
|---|---|---|---|
| 1 | Identifier quoting (SQLGlot `quote_identifiers`; канон: идентификаторы из схемы всегда в `"…"`) | `generate()`, `_join_on()` — голые имена; колонка `order`/`group` ломает SQL | Обернуть все идентификаторы в `"…"` при генерации |
| 2 | PK/FK introspection for join candidates (sqlsure `model_from_sqlite`, WrenAI MDL relationships) | `_join_on()` — эвристика «общая колонка» вместо FK | Читать `PRAGMA foreign_key_list` / `PRAGMA index_list` при загрузке схемы |
| 3 | Execution-based validation (Anthropic tests, Vanna `run_sql`, Spider execution accuracy) | только EXPLAIN; `WHERE x = ?` без значения — SQL неисполним вне EXPLAIN | Флаг `--run`: исполнить, сравнить shape результата; извлекать значение для WHERE |
| 4 | Honest feedback instead of silent fallback (sqlsure: never suppress; «can't verify» ≠ «looks fine») | `main()`: при провале EXPLAIN — тихий `SELECT * FROM first_table` | Выводить текст ошибки в stderr, fallback только с предупреждением |
| 5 | Plan depth from `parent` references (grok-sqlite-explain: `(id, parent, notused, detail)`) | `format_plan()` использует `r[0]` (id) как глубину | Построить дерево `parent → children`, индентировать рекурсивно |
| 6 | Column types in schema dump (Anthropic: `- col (type)`) | `tables: dict[str, list[str]]` хранит только имена | Добавить типы + PK-флаг из `PRAGMA table_info` |
| 7 | LIMIT clamping (Vanna rate limiting; benchmark LIMIT conventions) | `LIMIT {_extract_number(q) or DEFAULT_LIMIT}` без потолка | Флаг `--max-limit` (по умолчанию, напр., 1000) |
| 8 | Semantic aggregation checks (sqlsure FANOUT/CHASM/ADDITIVITY) | нет — EXPLAIN не видит double-counting | Адвайзерная секция в SKILL.md: «COUNT после JOIN может удвоить строки» |
| 9 | date/ratio intents (SQLCoder taxonomy: date, group_by, order_by, ratio, join, where) | `_intents()` — нет date/ratio | Шаблоны «за последние N дней» (date-функции sqlite), «на сколько процентов» |
| 10 | Few-shot examples in SKILL.md (Anthropic `<query>/<sql>`, Vanna train-pairs) | нет секции примеров вопрос→SQL | 3-5 пар вопрос→SQL с фиксированным форматом в references |

## (c) Citable CLI/API examples

```bash
# sqlite-utils — интроспекция и in-memory (simonw/sqlite-utils)
sqlite-utils schema mydb.db                      # полный DDL схемы
sqlite-utils analyze mydb.db                     # ANALYZE — статистика для планировщика
sqlite-utils memory 'select sqlite_version()' --csv   # in-memory БД, аналог нашего подхода
sqlite-utils tables mydb.db --csv --no-headers   # машинный список таблиц

# sqlsure — семантическая проверка перед исполнением
python -m sqlsure.cli --model model.json query.sql   # exit 1 при violations
python -c "from sqlsure.introspect import model_from_sqlite; ..."  # PK→grain, FK→join edges

# Anthropic cookbook — promptfoo-харнесс (execution-based asserts)
npx promptfoo@latest eval -c promptfooconfig.yaml --output ../data/results.csv
# asserts: contains "<sql>", python file://tests/test_*.py (execute + compare)

# SQLGlot — квотинг и нормализация
from sqlglot import transpile
transpile("select order from t", read="sqlite", write="sqlite", pretty=True, quote_identifiers=True)

# Spider eval (Yale-LILY/spider): evaluation.py — exact match + execution accuracy
```

## (d) Adopted already

1. **In-memory схема из DDL + sqlite_master/PRAGMA table_info** — идентично канону Anthropic и sqlite-utils memory.
2. **EXPLAIN QUERY PLAN перед выдачей** — уровень «validity» из методологии BIRD.
3. **Плейсхолдер `= ?` вместо интерполяции значений** — параметризация против SQL-инъекций; пользовательский текст никогда не интерполируется, в SQL попадают только идентификаторы из схемы.
4. **DEFAULT_LIMIT = 10** — LIMIT-безопасность по умолчанию.
5. **Структура SKILL.md** (frontmatter name/description/license/metadata/compatibility + When to use / Do NOT use / Files / Usage / Verification) — совпадает с шаблоном Anthropic (https://github.com/anthropics/skills/tree/main/template).