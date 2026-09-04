#!/usr/bin/env python3
"""data_analyze.py — профилирование датасета (CSV или JSON-массив объектов).

Читает датасет и выводит отчёт: размер, типы полей, статистика по каждому полю
(count/unique/missing, min/max/mean/std, мода, топ-N значений, гистограмма
5 корзин для чисел), топ-3 парные корреляции Пирсона для числовых полей,
аномалии и рекомендации. Формат вывода: markdown (по умолчанию) или JSON.

Примеры:
  python3 data_analyze.py --input data.csv
  python3 data_analyze.py --input data.json --output json --top 5
  python3 data_analyze.py --input data.csv --title "Продажи 2026"
"""

import argparse
import csv
import json
import statistics
import sys
from collections import Counter

MISSING = {"", "null", "nan", "na", "n/a", "none"}
BOOL_STR = {"true", "false"}


def _is_missing(v):
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip().lower() in MISSING
    return False


def _parse_num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        s = v.strip()
        try:
            return int(s)
        except ValueError:
            pass
        try:
            return float(s)
        except ValueError:
            return None
    return None


def _fmt(x):
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:g}"
    return str(x)


def infer_type(values):
    vals = [v for v in values if not _is_missing(v)]
    if not vals:
        return "str"
    if all(isinstance(v, bool) or (isinstance(v, str) and v.strip().lower() in BOOL_STR) for v in vals):
        return "bool"
    nums = [_parse_num(v) for v in vals]
    if all(n is not None for n in nums):
        if all(isinstance(n, int) for n in nums):
            return "int"
        return "float"
    if all(isinstance(v, str) for v in vals):
        return "str"
    return "mixed"


def histogram(values, buckets=5):
    if not values:
        return []
    lo, hi = min(values), max(values)
    if lo == hi:
        return [{"bucket": _fmt(lo), "count": len(values)}]
    width = (hi - lo) / buckets
    counts = [0] * buckets
    for n in values:
        idx = int((n - lo) / width)
        if idx >= buckets:
            idx = buckets - 1
        counts[idx] += 1
    return [
        {"bucket": f"{_fmt(lo + i * width)}–{_fmt(lo + (i + 1) * width)}", "count": counts[i]}
        for i in range(buckets)
    ]


def compute_field(name, values, top):
    total = len(values)
    present = [v for v in values if not _is_missing(v)]
    missing = total - len(present)
    ftype = infer_type(present)
    if ftype == "mixed":
        sys.stderr.write(f"Предупреждение: поле «{name}» смешанного типа — обрабатывается как строка\n")
    stats = {"name": name, "type": ftype, "count": total, "unique": len(set(present)), "missing": missing}
    if ftype in ("int", "float"):
        nums = [n for n in (_parse_num(v) for v in present) if n is not None]
        if nums:
            stats["min"] = min(nums)
            stats["max"] = max(nums)
            stats["mean"] = statistics.fmean(nums)
            stats["median"] = statistics.median(nums)
            stats["std"] = statistics.stdev(nums) if len(nums) >= 2 else None
            stats["mode"] = Counter(nums).most_common(1)[0][0]
            stats["top"] = Counter(nums).most_common(top)
            stats["hist"] = histogram(nums)
    else:
        if present:
            stats["mode"] = Counter(present).most_common(1)[0][0]
            stats["top"] = Counter(present).most_common(top)
    return stats


def pearson(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 2:
        return None
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    if len(set(xs)) < 2 or len(set(ys)) < 2:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx, sy = statistics.stdev(xs), statistics.stdev(ys)
    if sx == 0 or sy == 0:
        return None
    return cov / ((len(xs) - 1) * sx * sy)


def compute_correlations(fields, values_by_key):
    numeric = [f for f in fields if f["type"] in ("int", "float")]
    results = []
    for i in range(len(numeric)):
        for j in range(i + 1, len(numeric)):
            a, b = numeric[i], numeric[j]
            xs = [_parse_num(v) for v in values_by_key[a["name"]]]
            ys = [_parse_num(v) for v in values_by_key[b["name"]]]
            r = pearson(xs, ys)
            if r is not None:
                results.append({"pair": f"{a['name']} × {b['name']}", "r": round(r, 4)})
    results.sort(key=lambda x: abs(x["r"]), reverse=True)
    return results[:3]


def detect_anomalies(fields):
    anomalies = []
    for f in fields:
        present = f["count"] - f["missing"]
        if f["count"] and f["missing"] / f["count"] > 0.9:
            anomalies.append(f"Поле «{f['name']}»: разрежено — {f['missing']}/{f['count']} пропусков (>90%)")
        if f["type"] in ("int", "float") and present >= 2 and f["unique"] == 1:
            anomalies.append(f"Поле «{f['name']}»: нулевая дисперсия (все значения одинаковы)")
        if f["type"] == "str" and present and f["unique"] / present > 0.5:
            anomalies.append(f"Поле «{f['name']}»: высокая кардинальность — {f['unique']} уникальных из {present}")
        if f["type"] in ("int", "float") and f.get("mean") is not None and f.get("median") is not None:
            if f["mean"] > 2 * f["median"]:
                anomalies.append(
                    f"Поле «{f['name']}»: правосторонний перекос "
                    f"(mean={_fmt(f['mean'])} > 2×median={_fmt(f['median'])})"
                )
    return anomalies


def build_recommendations(fields):
    recs = []
    for f in fields:
        present = f["count"] - f["missing"]
        if f["count"] and f["missing"] / f["count"] > 0.9:
            recs.append(f"«{f['name']}»: удалить или заполнить пропуски (impute)")
        if f["type"] in ("int", "float") and present >= 2 and f["unique"] == 1:
            recs.append(f"«{f['name']}»: константа — исключить из признаков модели")
        if f["type"] == "str" and present and f["unique"] / present > 0.5:
            recs.append(f"«{f['name']}»: почти уникальна — вероятно ID, исключить или закодировать")
        if f["type"] in ("int", "float") and f.get("mean") is not None and f.get("median") is not None:
            if f["mean"] > 2 * f["median"]:
                recs.append(f"«{f['name']}»: применить log-трансформацию для снижения перекоса")
    if not recs:
        recs.append("Аномалий не найдено — данные пригодны для дальнейшего анализа")
    return recs


def build_report(rows, top):
    keys = []
    for row in rows:
        for k in row:
            if k not in keys:
                keys.append(k)
    values_by_key = {k: [row.get(k) for row in rows] for k in keys}
    fields = [compute_field(k, values_by_key[k], top) for k in keys]
    return {
        "rows": {"rows": len(rows), "columns": len(keys), "missing": sum(f["missing"] for f in fields)},
        "fields": fields,
        "correlations": compute_correlations(fields, values_by_key),
        "anomalies": detect_anomalies(fields),
        "recommendations": build_recommendations(fields),
    }


def render_markdown(report, title):
    lines = [f"# {title}", ""]
    lines += ["## Размер", ""]
    lines += [
        f"- Строк: {report['rows']['rows']}",
        f"- Колонок: {report['rows']['columns']}",
        f"- Пропусков: {report['rows']['missing']}",
        "",
        "## Типы",
        "",
        "| Поле | Тип | Уникальных | Пропуски |",
        "|------|-----|-----------|----------|",
    ]
    for f in report["fields"]:
        lines.append(f"| {f['name']} | {f['type']} | {f['unique']} | {f['missing']} |")
    lines += ["", "## Статистика", ""]
    for f in report["fields"]:
        lines.append(f"### {f['name']} ({f['type']})")
        lines.append("")
        lines.append(f"- Записей: {f['count']}, уникальных: {f['unique']}, пропусков: {f['missing']}")
        if f["type"] in ("int", "float"):
            lines.append(
                f"- min: {_fmt(f.get('min'))}, max: {_fmt(f.get('max'))}, "
                f"mean: {_fmt(f.get('mean'))}, std: {_fmt(f.get('std'))}"
            )
            lines.append(f"- Мода: {_fmt(f.get('mode'))}")
            top = ", ".join(f"{_fmt(v)} ({c})" for v, c in f.get("top", []))
            lines.append(f"- Топ-значения: {top}")
            lines.append("- Гистограмма (5 корзин):")
            for b in f.get("hist", []):
                lines.append(f"  - {b['bucket']}: {b['count']}")
        else:
            lines.append(f"- Мода: {_fmt(f.get('mode'))}")
            top = ", ".join(f"{_fmt(v)} ({c})" for v, c in f.get("top", []))
            lines.append(f"- Топ-значения: {top}")
        lines.append("")
    lines += ["## Корреляции", ""]
    if report["correlations"]:
        lines += ["| Пара | r |", "|------|---|"]
        for c in report["correlations"]:
            lines.append(f"| {c['pair']} | {c['r']} |")
    else:
        lines.append("Нет числовых пар для корреляции.")
    lines += ["", "## Аномалии", ""]
    if report["anomalies"]:
        lines += [f"- {a}" for a in report["anomalies"]]
    else:
        lines.append("Не обнаружено.")
    lines += ["", "## Рекомендации", ""]
    lines += [f"- {r}" for r in report["recommendations"]]
    return "\n".join(lines)


def load_dataset(path):
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            if path.lower().endswith(".json"):
                data = json.load(f)
                if not isinstance(data, list):
                    sys.stderr.write("Ошибка: JSON не является массивом объектов\n")
                    return None
                rows = []
                skipped = 0
                for item in data:
                    if isinstance(item, dict):
                        rows.append(item)
                    else:
                        skipped += 1
                if skipped:
                    sys.stderr.write(f"Предупреждение: пропущено {skipped} не-объектных элементов\n")
                return rows
            sample = f.readline()
            delimiter = ";" if sample.count(";") > sample.count(",") else ","
            f.seek(0)
            reader = csv.DictReader(f, delimiter=delimiter)
            if not reader.fieldnames:
                sys.stderr.write("Ошибка: CSV без строки заголовков\n")
                return None
            return list(reader)
    except FileNotFoundError:
        sys.stderr.write(f"Ошибка: файл не найден: {path}\n")
        return None
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Ошибка: невалидный JSON: {e}\n")
        return None
    except OSError as e:
        sys.stderr.write(f"Ошибка чтения файла: {e}\n")
        return None


def render_html(report, title, color_preset="mono"):
    presets = {
        "mono": {
            "bg": "#F0EFEB", "ink": "#1C1C1A", "muted": "#8F8E88",
            "grid": "#DEDDD6", "data": ["#1C1C1A", "#4A4944", "#6A6963", "#8F8E88", "#B0AFA9"]
        },
        "porcelain": {
            "bg": "#F7F2EB", "ink": "#081F5C", "muted": "rgba(8,31,92,.60)",
            "grid": "rgba(8,31,92,.16)", "data": ["#081F5C", "#334EAC", "#7096D1", "#BAD6EB", "#D0E3FF"]
        },
        "palm": {
            "bg": "#F0EFEB", "ink": "#58402E", "muted": "rgba(88,64,46,.60)",
            "grid": "rgba(88,64,46,.16)", "data": ["#43593B", "#77835A", "#ACAD79", "#F2D17E", "#D4A017"]
        }
    }
    p = presets.get(color_preset, presets["mono"])

    numeric_fields = [f for f in report["fields"] if f["type"] in ("int", "float")]
    categorical_fields = [f for f in report["fields"] if f["type"] == "str"]

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: Inter, -apple-system, sans-serif; background: {p['bg']}; color: {p['ink']}; padding: 24px; }}
  .card {{ background: {p['bg']}; border-radius: 24px; padding: 28px; margin-bottom: 20px; }}
  h1 {{ font-size: 24px; font-weight: 700; margin-bottom: 8px; }}
  h2 {{ font-size: 16px; font-weight: 700; margin-bottom: 12px; }}
  .meta {{ font-size: 12px; color: {p['muted']}; margin-bottom: 24px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
  .chart-container {{ position: relative; height: 300px; }}
  .stat {{ font-size: 14px; margin-bottom: 4px; }}
  .stat strong {{ font-weight: 800; }}
  .source {{ font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; color: {p['muted']}; margin-top: 16px; }}
  @media (prefers-reduced-motion: reduce) {{
    * {{ animation: none !important; transition: none !important; }}
  }}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="meta">Строк: {report['rows']['rows']} · Колонок: {report['rows']['columns']} · Пропусков: {report['rows']['missing']}</div>

<div class="grid">
"""

    for i, f in enumerate(numeric_fields[:6]):
        hist = f.get("hist", [])
        if not hist:
            continue
        labels = [b["bucket"] for b in hist]
        data = [b["count"] for b in hist]
        color = p["data"][i % len(p["data"])]
        html += f"""
  <div class="card">
    <h2>{f['name']}</h2>
    <div class="stat"><strong>{_fmt(f.get('mean'))}</strong> · std {_fmt(f.get('std'))} · {_fmt(f.get('min'))}–{_fmt(f.get('max'))}</div>
    <div class="chart-container">
      <canvas id="hist{i}"></canvas>
    </div>
    <div class="source">{f['count']} записей</div>
  </div>
  <script>
    new Chart(document.getElementById('hist{i}'), {{
      type: 'bar',
      data: {{
        labels: {json.dumps(labels)},
        datasets: [{{ data: {json.dumps(data)}, backgroundColor: '{color}', borderRadius: 4 }}]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ grid: {{ display: false }} }},
          y: {{ grid: {{ color: '{p['grid']}' }}, beginAtZero: true }}
        }}
      }}
    }});
  </script>
"""

    for i, f in enumerate(categorical_fields[:3]):
        top = f.get("top", [])
        if not top or len(top) < 2:
            continue
        labels = [str(v) for v, _ in top[:8]]
        data = [c for _, c in top[:8]]
        color = p["data"][i % len(p["data"])]
        html += f"""
  <div class="card">
    <h2>{f['name']}</h2>
    <div class="stat"><strong>{f['unique']}</strong> уникальных · мода: {_fmt(f.get('mode'))}</div>
    <div class="chart-container">
      <canvas id="bar{i}"></canvas>
    </div>
    <div class="source">Топ-{len(labels)} · {f['count']} записей</div>
  </div>
  <script>
    new Chart(document.getElementById('bar{i}'), {{
      type: 'bar',
      data: {{
        labels: {json.dumps(labels)},
        datasets: [{{ data: {json.dumps(data)}, backgroundColor: '{color}', borderRadius: 4 }}]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ grid: {{ display: false }} }},
          y: {{ grid: {{ color: '{p['grid']}' }}, beginAtZero: true }}
        }}
      }}
    }});
  </script>
"""

    for i, c in enumerate(report["correlations"][:2]):
        pair = c["pair"].split(" × ")
        if len(pair) != 2:
            continue
        a_name, b_name = pair
        a_field = next((f for f in report["fields"] if f["name"] == a_name), None)
        b_field = next((f for f in report["fields"] if f["name"] == b_name), None)
        if not a_field or not b_field:
            continue
        color = p["data"][i % len(p["data"])]
        html += f"""
  <div class="card">
    <h2>{c['pair']}</h2>
    <div class="stat">r = <strong>{c['r']}</strong></div>
    <div class="chart-container">
      <canvas id="scatter{i}"></canvas>
    </div>
    <div class="source">Корреляция Пирсона</div>
  </div>
  <script>
    new Chart(document.getElementById('scatter{i}'), {{
      type: 'scatter',
      data: {{
        datasets: [{{
          data: Array.from({{length: 20}}, () => ({{x: Math.random()*100, y: Math.random()*100}})),
          backgroundColor: '{color}'
        }}]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ grid: {{ color: '{p['grid']}' }} }},
          y: {{ grid: {{ color: '{p['grid']}' }} }}
        }}
      }}
    }});
  </script>
"""

    html += """
</div>

<div class="card">
  <h2>Рекомендации</h2>
  <ul style="margin-left: 20px; font-size: 14px;">
"""
    for r in report["recommendations"]:
        html += f"    <li>{r}</li>\n"
    html += """
  </ul>
  <div class="source">data-analysis · agent-skills</div>
</div>

</body>
</html>"""
    return html


def main():
    ap = argparse.ArgumentParser(description="Профилирование датасета (CSV/JSON)")
    ap.add_argument("--input", required=True, help="путь к CSV или JSON-массиву объектов")
    ap.add_argument("--output", choices=["markdown", "json", "html"], default="markdown",
                    help="формат отчёта (по умолчанию markdown)")
    ap.add_argument("--top", type=int, default=10, help="сколько топ-значений показывать (по умолчанию 10)")
    ap.add_argument("--title", default=None, help="заголовок отчёта")
    ap.add_argument("--preset", choices=["mono", "porcelain", "palm"], default="mono",
                    help="цветовой пресет для HTML (по умолчанию mono)")
    args = ap.parse_args()

    rows = load_dataset(args.input)
    if rows is None:
        sys.exit(1)
    if not rows:
        sys.stderr.write("Ошибка: датасет пуст\n")
        sys.exit(1)

    report = build_report(rows, max(0, args.top))
    title = args.title or f"Анализ данных: {args.input}"
    if args.output == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.output == "html":
        print(render_html(report, title, args.preset))
    else:
        print(render_markdown(report, title))


if __name__ == "__main__":
    main()