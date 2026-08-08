#!/usr/bin/env python3
"""csv_pro.py — профиль CSV: типы колонок, статистика, аномалии.

Читает CSV (файл --input или stdin --stdin), определяет разделитель
(по умолчанию ';', затем ','), для каждой колонки считает тип
(int/float/str/date), min/max/mean, пропуски, уникальные значения и топ-3
частых. Ищет аномалии: нулевая дисперсия, >95% пустых, дубликаты строк,
строки длиннее 1000 символов, выбросы (значение >= 5×IQR от медианы).
Вывод: markdown-таблица (по умолчанию) или JSON (--output json).

Примеры:
  python3 csv_pro.py --input data.csv
  python3 csv_pro.py --input data.csv --output json
  cat data.csv | python3 csv_pro.py --stdin
"""

import argparse
import csv
import json
import statistics
import sys
from collections import Counter
from datetime import datetime

DATE_FORMATS = ("%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d")
LONG_STRING = 1000
MISSING_RATIO = 0.95
SPIKE_IQR = 5.0


def load_lines(path):
    if path:
        with open(path, "rb") as f:
            raw = f.readlines()
    else:
        raw = sys.stdin.buffer.readlines()
    lines, skipped = [], 0
    for b in raw:
        try:
            lines.append(b.decode("utf-8-sig"))
        except UnicodeDecodeError:
            skipped += 1
    return lines, skipped


def detect_delimiter(lines):
    for ln in lines:
        if ln.strip():
            return ";" if ln.count(";") > ln.count(",") else ","
    return ","


def parse_value(raw):
    s = raw.strip()
    if not s:
        return None
    try:
        int(s)
        return "int"
    except ValueError:
        pass
    try:
        float(s)
        return "float"
    except ValueError:
        pass
    for fmt in DATE_FORMATS:
        try:
            datetime.strptime(s, fmt)
            return "date"
        except ValueError:
            pass
    try:
        datetime.fromisoformat(s)
        return "date"
    except ValueError:
        return "str"


def is_header(row):
    return bool(row) and all(parse_value(c) in ("str", "date") for c in row)


def analyze_column(name, values, missing, total):
    types = {t for t in (parse_value(v) for v in values) if t}
    if types == {"int"}:
        ctype = "int"
    elif types and types <= {"int", "float"}:
        ctype = "float"
    elif types == {"date"}:
        ctype = "date"
    else:
        ctype = "str"
    nums = []
    if ctype in ("int", "float"):
        for v in values:
            try:
                nums.append(float(v))
            except ValueError:
                pass
    prof = {
        "name": name,
        "type": ctype,
        "missing": missing,
        "unique": len(set(values)),
        "top3": [list(t) for t in Counter(values).most_common(3)],
    }
    if nums:
        prof["min"] = min(nums)
        prof["max"] = max(nums)
        prof["mean"] = statistics.mean(nums)
    anomalies = []
    if len(nums) >= 2 and min(nums) == max(nums):
        anomalies.append({"type": "zero_variance", "column": name,
                          "detail": f"все значения = {min(nums):g}"})
    if total and missing / total > MISSING_RATIO:
        anomalies.append({"type": "mostly_missing", "column": name,
                          "detail": f"{missing}/{total} пустых"})
    long = sum(1 for v in values if len(v) > LONG_STRING)
    if long:
        anomalies.append({"type": "long_strings", "column": name,
                          "detail": f"{long} значений длиннее {LONG_STRING} символов"})
    if len(nums) >= 4:
        med = statistics.median(nums)
        q1, _, q3 = statistics.quantiles(nums, n=4)
        iqr = q3 - q1
        if iqr > 0:
            spikes = sum(1 for v in nums if abs(v - med) >= SPIKE_IQR * iqr)
            if spikes:
                anomalies.append({"type": "spikes", "column": name,
                                  "detail": f"{spikes} значений >= 5xIQR от медианы"})
    return prof, anomalies


def fmt_num(v):
    return f"{v:g}" if isinstance(v, float) else str(v)


def short(s, n=40):
    s = str(s)
    return s if len(s) <= n else s[: n - 1] + "…"


def esc(s):
    return str(s).replace("|", "\\|")


def render_md(meta, profiles, anomalies):
    out = [f"# Профиль CSV: `{meta['file']}`", ""]
    out.append(f"- Строк: {meta['rows']}")
    out.append(f"- Колонок: {meta['columns']}")
    out.append(f"- Разделитель: `{meta['delimiter']}`")
    if meta["skipped_lines"]:
        out.append(f"- Не декодировано строк: {meta['skipped_lines']}")
    out += ["", "## Колонки", "",
            "| Колонка | Тип | Уникальных | Пустых | Min | Max | Mean | Топ-3 частых |",
            "|---------|-----|-----------|--------|-----|-----|------|--------------|"]
    for p in profiles:
        top3 = ", ".join(f"{short(v)} ({n})" for v, n in p["top3"])
        out.append(f"| {esc(p['name'])} | {p['type']} | {p['unique']} | {p['missing']} "
                   f"| {fmt_num(p.get('min', ''))} | {fmt_num(p.get('max', ''))} "
                   f"| {fmt_num(p.get('mean', ''))} | {top3} |")
    out += ["", "## Аномалии", ""]
    if not anomalies:
        out.append("Аномалий не найдено.")
    else:
        for a in anomalies:
            col = f"`{a['column']}`: " if a["column"] else ""
            out.append(f"- {col}{a['type']} — {a['detail']}")
    return "\n".join(out)


def render_json(meta, profiles, anomalies):
    return json.dumps({
        "file": meta["file"],
        "rows": meta["rows"],
        "columns": meta["columns"],
        "delimiter": meta["delimiter"],
        "skipped_lines": meta["skipped_lines"],
        "columns": profiles,
        "anomalies": anomalies,
    }, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser(description="CSV profile: types, stats, anomalies")
    ap.add_argument("--input", help="input CSV file")
    ap.add_argument("--stdin", action="store_true", help="read CSV from stdin")
    ap.add_argument("--output", choices=["md", "json"], default="md",
                    help="output format (default: md)")
    ap.add_argument("--delimiter", default=None,
                    help="CSV delimiter (default: auto-detect ';' then ',')")
    args = ap.parse_args()

    if not args.input and not args.stdin:
        ap.error("need --input or --stdin")
    if args.delimiter and len(args.delimiter) != 1:
        ap.error("--delimiter must be a single character")

    csv.field_size_limit(10_000_000)
    path = args.input
    try:
        lines, skipped = load_lines(path)
    except OSError as e:
        sys.stderr.write(f"csv_pro: не удалось прочитать {path}: {e}\n")
        sys.exit(1)
    if skipped:
        sys.stderr.write(f"csv_pro: пропущено {skipped} строк (не UTF-8)\n")

    delim = args.delimiter or detect_delimiter(lines)
    try:
        rows = [r for r in csv.reader(lines, delimiter=delim) if any(c.strip() for c in r)]
    except csv.Error as e:
        sys.stderr.write(f"csv_pro: ошибка разбора CSV: {e}\n")
        sys.exit(1)

    meta = {"file": path or "<stdin>", "rows": 0, "columns": 0,
            "delimiter": delim, "skipped_lines": skipped}

    if not rows:
        if args.output == "json":
            print(render_json(meta, [], []))
        else:
            print(f"# Профиль CSV: `{meta['file']}`\n\nФайл пуст: нет данных для анализа.")
        return

    has_header = is_header(rows[0])
    names = rows[0] if has_header else [f"Column{i+1}" for i in range(len(rows[0]))]
    data = rows[1:] if has_header else rows
    meta["rows"] = len(data)
    meta["columns"] = len(names)

    if not data:
        if args.output == "json":
            print(render_json(meta, [], []))
        else:
            print(f"# Профиль CSV: `{meta['file']}`\n\nТолько заголовок, данных нет.")
        return

    profiles, anomalies = [], []
    for i, name in enumerate(names):
        values, missing = [], 0
        for row in data:
            cell = row[i] if i < len(row) else ""
            if cell.strip():
                values.append(cell)
            else:
                missing += 1
        prof, anoms = analyze_column(name, values, missing, len(data))
        profiles.append(prof)
        anomalies.extend(anoms)

    dup = len(data) - len({tuple(r) for r in data})
    if dup:
        anomalies.append({"type": "duplicate_rows", "column": None,
                          "detail": f"{dup} дубликатов строк"})

    if args.output == "json":
        print(render_json(meta, profiles, anomalies))
    else:
        print(render_md(meta, profiles, anomalies))


if __name__ == "__main__":
    main()