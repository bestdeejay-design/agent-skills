#!/usr/bin/env python3
"""mermaid_to_markdown.py — обёртка Mermaid-кода в markdown-файл.

Читает описание диаграммы (mermaid-код) из stdin или файла, валидирует
базовый синтаксис и формирует markdown-файл с mermaid-блоком.

Примеры:
    # Из файла
    python3 mermaid_to_markdown.py --type flowchart input.mmd --output out.md

    # Из stdin
    echo "A --> B" | python3 mermaid_to_markdown.py --type flowchart

    # С заголовком секции
    python3 mermaid_to_markdown.py --type er --title "Схема БД" schema.txt

Валидация:
    - одинарные/двойные кавычки для node labels со спецсимволами
    - отсутствие спецсимволов, ломающих синтаксис Mermaid
    - предупреждение, если в диаграмме больше 20 узлов
"""
import argparse
import re
import sys

# Спецсимволы, которые ломают синтаксис Mermaid, если label не в кавычках.
# Внутри label без кавычек нельзя использовать: [ ] { } ( ) : # и т.п.
UNQUOTED_LABEL_BREAKERS = re.compile(r"[\[\]{}():#]")

# Символы, которые вообще не должны попадать в mermaid-код.
FORBIDDEN_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

# Паттерны соединений по типам диаграмм (для подсчёта узлов).
EDGE_PATTERNS = {
    "flowchart": re.compile(r"-->|---|==>|-.->"),
    "sequence": re.compile(r"->>|-->>|->|-->"),
    "architecture": re.compile(r"-->|==>"),
    "er": re.compile(r"\|o|o\||\|\||--"),
}

SUPPORTED_TYPES = ("flowchart", "sequence", "architecture", "er")


def read_input(args: argparse.Namespace) -> str:
    """Читает mermaid-код из файла или stdin."""
    if args.input:
        with open(args.input, encoding="utf-8") as f:
            return f.read()
    return sys.stdin.read()


def validate(text: str) -> list:
    """Возвращает список предупреждений/ошибок по тексту диаграммы."""
    issues = []
    lines = [ln for ln in text.splitlines() if ln.strip()]

    if not lines:
        issues.append("ERROR: пустой ввод — нет ни одной строки диаграммы")
        return issues

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        # Пропускаем комментарии и пустые строки.
        if not stripped or stripped.startswith("%%"):
            continue

        # Контрольные символы — всегда ошибка.
        if FORBIDDEN_CHARS.search(stripped):
            issues.append(
                f"ERROR: строка {lineno}: найдены управляющие символы"
            )
            continue

        # Проверка кавычек в label.
        # Если в строке есть спецсимволы [ ] { } ( ) : # и при этом
        # label не обёрнут в одинарные или двойные кавычки — предупреждение.
        if UNQUOTED_LABEL_BREAKERS.search(stripped):
            # Строка с узлом вида: A[Текст: с двоеточием] --> B
            # label внутри [ ] должен быть в кавычках, если содержит : или #
            for match in re.finditer(r"\[([^\]]*)\]", stripped):
                label = match.group(1)
                if UNQUOTED_LABEL_BREAKERS.search(label) and not (
                    (label.startswith('"') and label.endswith('"'))
                    or (label.startswith("'") and label.endswith("'"))
                ):
                    issues.append(
                        f"WARN: строка {lineno}: label '{label}' содержит "
                        f"спецсимволы — оберни его в кавычки: "
                        f'["{label}"] или [\'{label}\']'
                    )

        # Проверка несбалансированных кавычек.
        for quote in ('"', "'"):
            if stripped.count(quote) % 2 != 0:
                issues.append(
                    f"WARN: строка {lineno}: нечётное количество кавычек "
                    f"{quote} — возможно, незакрытый label"
                )

    # Подсчёт узлов: количество строк со связями + количество объявлений
    # узлов в фигурных/квадратных скобках.
    node_count = 0
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("%%"):
            continue
        # Узлы в квадратных/фигурных/круглых скобках.
        node_count += len(re.findall(r"[\[{(][^\]})]*[\]})]", stripped))
        # Строки со связями.
        for pattern in EDGE_PATTERNS.values():
            if pattern.search(stripped):
                node_count += 1
                break

    if node_count > 20:
        issues.append(
            f"WARN: диаграмма содержит примерно {node_count} узлов — больше "
            f"20. Рекомендуется разбить на подграфы (subgraph) или несколько "
            f"диаграмм."
        )

    return issues


def build_markdown(diagram_type: str, title: str, mermaid_code: str) -> str:
    """Собирает markdown-файл с mermaid-блоком."""
    parts = []
    if title:
        parts.append(f"# {title}\n")
    parts.append(f"<!-- Тип диаграммы: {diagram_type} -->")
    parts.append("```mermaid")
    parts.append(mermaid_code.rstrip("\n"))
    parts.append("```")
    return "\n".join(parts) + "\n"


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Обёртка Mermaid-кода в markdown-файл с валидацией.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="файл с mermaid-кодом (по умолчанию — stdin)",
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=SUPPORTED_TYPES,
        help="тип диаграммы: flowchart, sequence, architecture, er",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="выходной markdown-файл (по умолчанию — stdout)",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="заголовок секции в markdown-файле",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    code = read_input(args)

    issues = validate(code)
    for issue in issues:
        print(issue, file=sys.stderr)

    has_errors = any(i.startswith("ERROR") for i in issues)
    if has_errors:
        print("Валидация не пройдена — markdown не сформирован.",
              file=sys.stderr)
        return 1

    markdown = build_markdown(args.type, args.title, code)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f"OK: {args.output} сформирован (тип: {args.type})",
              file=sys.stderr)
    else:
        sys.stdout.write(markdown)
    return 0


if __name__ == "__main__":
    sys.exit(main())