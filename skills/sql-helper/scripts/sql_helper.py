#!/usr/bin/env python3
"""sql_helper.py — генерация SQL по текстовому вопросу и DDL-схеме.

Читает DDL-файл, строит in-memory схему в sqlite3, сопоставляет слова
вопроса с таблицами и колонками и собирает SQL по шаблонам интентов
(select, join, where, group, order, count, limit). Каждый кандидат
проверяется через EXPLAIN, чтобы отбросить невалидные запросы.

Вывод: сгенерированный SQL и, при --explain, читаемый план запроса.

Примеры:
  python3 sql_helper.py --ddl schema.sql --question "select users by id"
  python3 sql_helper.py --ddl schema.sql --question "count orders by user" --explain
"""

import argparse
import re
import sqlite3
import sys

DEFAULT_LIMIT = 10


def load_schema(ddl_text: str) -> tuple[sqlite3.Connection, dict[str, list[str]]]:
    """In-memory БД из DDL; возвращает (conn, {table: [columns]})."""
    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(ddl_text)
    except sqlite3.Error as e:
        sys.stderr.write(f"invalid DDL: {e}\n")
        sys.exit(1)
    tables = {}
    for (name,) in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ):
        cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{name}")')]
        tables[name] = cols
    return conn, tables


def _first_match(question: str, names: list[str]) -> str | None:
    """Первый элемент names, встречающийся в вопросе (без учёта регистра)."""
    q = question.lower()
    for n in names:
        if n.lower() in q:
            return n
    return None


def _extract_number(question: str) -> int | None:
    """Первое число из вопроса (для LIMIT), иначе None."""
    m = re.search(r"\d+", question)
    return int(m.group()) if m else None


def _intents(question: str) -> set[str]:
    """Интенты, найденные в вопросе: count, group, join, where, order, limit."""
    q = question.lower()
    found = set()
    if re.search(r"\bcount\b|сколько|количество", q):
        found.add("count")
    if re.search(r"\bgroup\b|групп", q):
        found.add("group")
    if re.search(r"\bjoin\b|объедин|вместе", q):
        found.add("join")
    if re.search(r"\bwhere\b|где|фильтр|только", q):
        found.add("where")
    if re.search(r"\border\b|сортир|по возрастанию|по убыванию", q):
        found.add("order")
    if re.search(r"\blimit\b|лимит|первые|топ\b|top\b", q):
        found.add("limit")
    return found


def _join_on(t1: str, t2: str, tables: dict[str, list[str]]) -> str:
    """Условие JOIN: общая колонка, иначе эвристика <t>_id = <t>.id."""
    shared = [c for c in tables[t1] if c in tables[t2]]
    if shared:
        return f"{t1}.{shared[0]} = {t2}.{shared[0]}"
    if f"{t1}_id" in tables[t2]:
        return f"{t2}.{t1}_id = {t1}.id"
    if f"{t2}_id" in tables[t1]:
        return f"{t1}.{t2}_id = {t2}.id"
    return f"{t1}.id = {t2}.id"


def generate(question: str, tables: dict[str, list[str]]) -> str:
    """Собирает SQL по интентам вопроса; возвращает строку SQL."""
    q = question.lower()
    mentioned = [t for t in tables if t.lower() in q]
    if not mentioned:
        mentioned = [next(iter(tables))]
    intents = _intents(q)

    if len(mentioned) >= 2:
        t1, t2 = mentioned[0], mentioned[1]
        on = _join_on(t1, t2, tables)
        sql = f"SELECT * FROM {t1} JOIN {t2} ON {on}"
        if "count" in intents:
            sql = f"SELECT COUNT(*) FROM {t1} JOIN {t2} ON {on}"
        cols = tables[t1] + tables[t2]
    else:
        table = mentioned[0]
        cols = tables[table]
        if "count" in intents and "group" not in intents:
            sql = f"SELECT COUNT(*) FROM {table}"
        elif "group" in intents:
            gcol = _first_match(q, cols)
            sql = (
                f"SELECT {gcol}, COUNT(*) FROM {table} GROUP BY {gcol}"
                if gcol
                else f"SELECT COUNT(*) FROM {table}"
            )
        else:
            sel = _first_match(q, cols)
            sql = f"SELECT {sel} FROM {table}" if sel else f"SELECT * FROM {table}"

    if "where" in intents:
        wcol = _first_match(q, cols)
        if wcol:
            sql += f" WHERE {wcol} = ?"
    if "order" in intents:
        ocol = _first_match(q, cols)
        direction = "DESC" if re.search(r"desc|убыван", q) else "ASC"
        if ocol:
            sql += f" ORDER BY {ocol} {direction}"
    if "limit" in intents:
        sql += f" LIMIT {_extract_number(q) or DEFAULT_LIMIT}"
    return sql


def explain(conn: sqlite3.Connection, sql: str) -> list[tuple]:
    """План запроса (EXPLAIN QUERY PLAN); при ошибке выход с кодом 1."""
    try:
        return list(conn.execute(f"EXPLAIN QUERY PLAN {sql}"))
    except sqlite3.Error as e:
        sys.stderr.write(f"invalid SQL: {e}\n")
        sys.exit(1)


def format_plan(rows: list[tuple]) -> str:
    """Читаемый текст плана: отступы по глубине узла."""
    return "\n".join("  " * r[0] + r[3] for r in rows)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate SQL from a natural-language question and a DDL schema"
    )
    ap.add_argument("--ddl", required=True, help="path to DDL file (CREATE TABLE statements)")
    ap.add_argument(
        "--question",
        required=True,
        help="natural-language question, e.g. 'count orders by user'",
    )
    ap.add_argument("--explain", action="store_true", help="also print the query plan")
    args = ap.parse_args()

    if not args.question.strip():
        sys.stderr.write("empty question\n")
        sys.exit(1)

    try:
        with open(args.ddl, "r", encoding="utf-8") as f:
            ddl_text = f.read()
    except OSError as e:
        sys.stderr.write(f"cannot read DDL file: {e}\n")
        sys.exit(1)

    conn, tables = load_schema(ddl_text)
    sql = generate(args.question, tables)
    try:
        conn.execute(f"EXPLAIN QUERY PLAN {sql}")
    except sqlite3.Error:
        # кандидат не прошёл EXPLAIN — откат к базовому SELECT
        sql = f"SELECT * FROM {next(iter(tables))}"
    print(sql)
    if args.explain:
        print("--- query plan ---")
        print(format_plan(explain(conn, sql)))


if __name__ == "__main__":
    main()