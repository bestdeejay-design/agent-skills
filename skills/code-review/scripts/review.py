#!/usr/bin/env python3
"""code-review — структурированный PR-review на основе git diff.

Применяет чек-лист из checklists.py к добавленным строкам diff и выдаёт
структурированный отчёт: [severity] файл:строка — проблема + исправление.

Источник входа (по приоритету):
    --repo PATH   git-репозиторий: берётся `git diff HEAD`
    --file PATH   обычный файл: ревьюится целиком (каждая строка = добавленная)
    --diff PATH   файл, содержащий git diff
    stdin         git diff из stdin (по умолчанию)

Опции:
    --severity S   фильтр по severity: critical, warning, nit (через запятую)
    --category C   фильтр по категории: correctness, security, performance,
                   style, tests, edge_cases (через запятую)
    --format FMT   text (default) | markdown
    --template T   шаблон итогового ревью (templates/review-template.md)
    --output FILE  сохранить отчёт в файл
    --json         вывести JSON-отчёт
    --no-color     без ANSI-цветов

Примеры:
    git diff | python3 review.py
    python3 review.py --repo /path/to/repo
    python3 review.py --file src/main.py
    python3 review.py --diff changes.diff --format markdown --template templates/review-template.md

Зависимости: только Python 3 stdlib.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime

from checklists import RULES

SEVERITY_ORDER = {"critical": 0, "warning": 1, "nit": 2}
CATEGORY_LABELS = {
    "correctness": "Correctness",
    "security": "Security",
    "performance": "Performance",
    "style": "Style",
    "tests": "Tests",
    "edge_cases": "Edge cases",
}
COLORS = {
    "critical": "\033[31m",
    "warning": "\033[33m",
    "nit": "\033[36m",
    "reset": "\033[0m",
}


def colorize(text, color, enabled=True):
    if not enabled:
        return text
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def get_diff_from_repo(repo):
    """Возвращает `git diff HEAD` для репозитория."""
    try:
        proc = subprocess.run(
            ["git", "-C", repo, "diff", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        sys.exit("error: git не найден в PATH")
    if proc.returncode != 0:
        sys.exit(f"error: не удалось получить diff из {repo}: {proc.stderr.strip()}")
    return proc.stdout


def parse_diff(diff_text):
    """Разбирает git diff в список добавленных строк.

    Возвращает список dict: {"file": str, "line": int, "text": str}.
    Удалённые строки и контекст не ревьюятся.
    """
    added = []
    current_file = None
    new_line = None
    for raw in diff_text.splitlines():
        line = raw.rstrip("\n")
        if line.startswith("+++ "):
            current_file = line[4:].split("\t")[0]
            if current_file.startswith("b/"):
                current_file = current_file[2:]
            new_line = None
            continue
        if line.startswith("--- "):
            continue
        if line.startswith("@@"):
            m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            if m:
                new_line = int(m.group(1))
            continue
        if new_line is None:
            continue
        if line.startswith("+"):
            added.append({"file": current_file, "line": new_line, "text": line[1:]})
            new_line += 1
        elif line.startswith("-"):
            continue
        elif line.startswith("\\"):
            continue
        else:
            new_line += 1
    return added


def review(lines, severity_filter, category_filter):
    """Применяет чек-лист к строкам. Возвращает список находок."""
    findings = []
    for entry in lines:
        text = entry["text"]
        for rule in RULES:
            if severity_filter and rule["severity"] not in severity_filter:
                continue
            if category_filter and rule["category"] not in category_filter:
                continue
            # Suppress arithmetic false positives inside URL contexts (e.g. SVG
            # data: URIs in CSS like http://www.w3.org/2000/svg).
            if rule["id"] == "EDGE-004" and re.search(r"://|url\(|data:", text):
                continue
            try:
                if re.search(rule["pattern"], text):
                    findings.append(
                        {
                            "severity": rule["severity"],
                            "category": rule["category"],
                            "rule_id": rule["id"],
                            "file": entry["file"] or "<stdin>",
                            "line": entry["line"],
                            "message": rule["message"],
                            "suggestion": rule["suggestion"],
                            "code": text.strip(),
                        }
                    )
            except re.error as exc:
                print(
                    f"warning: неверный regex в правиле {rule['id']}: {exc}",
                    file=sys.stderr,
                )
    findings.sort(
        key=lambda f: (
            SEVERITY_ORDER.get(f["severity"], 9),
            f["file"] or "",
            f["line"],
        )
    )
    return findings


def summarize(findings):
    """Краткая сводка по категориям."""
    by_cat = {}
    for f in findings:
        by_cat[f["category"]] = by_cat.get(f["category"], 0) + 1
    parts = []
    for cat in CATEGORY_LABELS:
        if cat in by_cat:
            parts.append(f"{CATEGORY_LABELS[cat]}: {by_cat[cat]}")
    return "; ".join(parts) if parts else "замечаний не найдено"


def render_text(findings, color=True):
    lines = []
    for f in findings:
        loc = f"{f['file']}:{f['line']}"
        head = f"[{f['severity']}] {loc} — {f['rule_id']}: {f['message']}"
        lines.append(colorize(head, f["severity"], color))
        if f["code"]:
            lines.append(f"    код: {f['code']}")
        lines.append(f"    fix: {f['suggestion']}")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_markdown_finding(f):
    cat = CATEGORY_LABELS.get(f["category"], f["category"])
    loc = f"{f['file']}:{f['line']}"
    block = (
        f"### [{f['severity']}] `{loc}` — {f['rule_id']} ({cat})\n\n"
        f"**Проблема:** {f['message']}\n\n"
        f"**Исправление:** {f['suggestion']}\n"
    )
    if f["code"]:
        block += f"\n**Код:**\n```\n{f['code']}\n```\n"
    return block


def render_markdown(findings, target, template_path=None):
    total = len(findings)
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITY_ORDER}
    findings_block = "\n\n".join(render_markdown_finding(f) for f in findings)
    if not findings_block:
        findings_block = "_Замечаний не найдено._"

    if template_path and os.path.isfile(template_path):
        with open(template_path, encoding="utf-8") as fh:
            template = fh.read()
        return (
            template.replace("{{REVIEW_TARGET}}", target)
            .replace("{{DATE}}", date.today().isoformat())
            .replace("{{TOTAL}}", str(total))
            .replace("{{CRITICAL}}", str(counts["critical"]))
            .replace("{{WARNING}}", str(counts["warning"]))
            .replace("{{NIT}}", str(counts["nit"]))
            .replace("{{SUMMARY}}", summarize(findings))
            .replace("{{FINDINGS}}", findings_block)
        )

    return (
        f"# Code Review\n\n"
        f"**Ревью:** `{target}`  \n"
        f"**Дата:** {date.today().isoformat()}  \n"
        f"**Найдено:** {total} (critical: {counts['critical']}, "
        f"warning: {counts['warning']}, nit: {counts['nit']})\n\n"
        f"## Summary\n\n{summarize(findings)}\n\n"
        f"## Findings\n\n{findings_block}\n"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Структурированный code-review по git diff (Python 3 stdlib)."
    )
    parser.add_argument("path", nargs="?", help="путь к git-репозиторию (аналог --repo)")
    parser.add_argument("--repo", help="путь к git-репозиторию")
    parser.add_argument("--file", help="путь к файлу для ревью целиком")
    parser.add_argument("--diff", help="путь к файлу с git diff")
    parser.add_argument("--severity", help="фильтр: critical,warning,nit")
    parser.add_argument(
        "--category",
        help="фильтр: correctness,security,performance,style,tests,edge_cases",
    )
    parser.add_argument("--format", choices=["text", "markdown"], default="text")
    parser.add_argument("--template", help="путь к шаблону итогового ревью")
    parser.add_argument("--output", help="сохранить отчёт в файл")
    parser.add_argument("--json", action="store_true", help="вывести JSON-отчёт")
    parser.add_argument("--no-color", action="store_true", help="без ANSI-цветов")
    args = parser.parse_args()

    severity_filter = {
        s.strip() for s in (args.severity or "").split(",") if s.strip()
    }
    category_filter = {
        c.strip() for c in (args.category or "").split(",") if c.strip()
    }

    if args.repo or args.path:
        repo = args.repo or args.path
        lines = parse_diff(get_diff_from_repo(repo))
        target = repo
    elif args.file:
        with open(args.file, encoding="utf-8") as fh:
            lines = [
                {
                    "file": os.path.basename(args.file),
                    "line": i + 1,
                    "text": line.rstrip("\n"),
                }
                for i, line in enumerate(fh)
            ]
        target = args.file
    elif args.diff:
        with open(args.diff, encoding="utf-8") as fh:
            lines = parse_diff(fh.read())
        target = args.diff
    else:
        lines = parse_diff(sys.stdin.read())
        target = "stdin"

    findings = review(lines, severity_filter, category_filter)

    if args.json:
        report = {
            "target": target,
            "generated": datetime.now().isoformat(timespec="seconds"),
            "total": len(findings),
            "counts": {
                s: sum(1 for f in findings if f["severity"] == s)
                for s in SEVERITY_ORDER
            },
            "findings": findings,
        }
        out = json.dumps(report, ensure_ascii=False, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(out + "\n")
            print(f"Отчёт сохранён в {args.output}")
        else:
            print(out)
        return

    if args.format == "markdown":
        body = render_markdown(findings, target, template_path=args.template)
    else:
        body = render_text(findings, color=not args.no_color)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(body + "\n")
        print(f"Отчёт сохранён в {args.output}")
    else:
        print(body)


if __name__ == "__main__":
    main()