#!/usr/bin/env python3
"""Generate pytest skeletons for a Python module from its AST.

Reads a .py file, collects public function signatures, and emits a pytest
module with @pytest.mark.parametrize cases for each function. Argument
values are derived from type annotations using ghostwriter-style heuristics:
  bool   -> True / False
  int    -> 0, -1, 1
  float  -> 0.0, -1.5
  str    -> "sample", ""
  list   -> []
  dict   -> {}
  Optional -> None

Private functions (leading underscore) are skipped. Output goes to stdout
unless --out FILE is given.

Usage:
    python3 test_gen.py --file module.py
    python3 test_gen.py --file module.py --out test_module.py
"""
import argparse
import ast
import sys
from dataclasses import dataclass, field


@dataclass
class FuncInfo:
    name: str
    args: list[str] = field(default_factory=list)
    anns: dict[str, str] = field(default_factory=dict)
    is_async: bool = False


def collect_functions(source: str) -> list[FuncInfo]:
    tree = ast.parse(source)
    funcs: list[FuncInfo] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("_"):
                continue
            args = [a.arg for a in node.args.args]
            anns = {
                a.arg: ast.unparse(a.annotation)
                for a in node.args.args
                if a.annotation is not None
            }
            funcs.append(
                FuncInfo(
                    name=node.name,
                    args=args,
                    anns=anns,
                    is_async=isinstance(node, ast.AsyncFunctionDef),
                )
            )
    return funcs


def values_for(annotation: str) -> list[str]:
    ann = (annotation or "").lower()
    if ann.startswith("optional"):
        return ["None"]
    if ann.startswith("list") or ann.startswith("tuple") or "seq" in ann:
        return ["[]" if ann.startswith("list") else "()"]
    if ann.startswith("dict") or "map" in ann or "mapping" in ann:
        return ["{}"]
    if ann in {"bool"}:
        return ["True", "False"]
    if "int" in ann:
        return ["0", "-1", "1"]
    if "float" in ann or "double" in ann:
        return ["0.0", "-1.5"]
    if "str" in ann or "string" in ann or "text" in ann:
        return ['"sample"', '""']
    return []


def _row_for(args: list[str], anns: dict[str, str]) -> str:
    cells = []
    for a in args:
        vals = values_for(anns.get(a, ""))
        cells.append(vals[0] if vals else "None")
    return ", ".join(cells)


def render_pytest(funcs: list[FuncInfo], module_name: str) -> str:
    lines = ['"""Auto-generated tests."""', "import pytest", f"import {module_name}", ""]
    for f in funcs:
        if f.is_async:
            lines.append("import asyncio" if not any(l.startswith("import asyncio") for l in lines) else "")
        call = f"{module_name}.{f.name}({', '.join(f.args)})"
        if f.is_async:
            call = f"asyncio.run({call})"
        if not f.args:
            lines += [
                f"def test_{f.name}():",
                f"    result = {call}",
                "    assert result is not None",
                "",
            ]
            continue
        rows = _row_for(f.args, f.anns)
        tuple_repr = f"({rows},)" if len(f.args) == 1 else f"({rows})"
        lines += [
            f"@pytest.mark.parametrize(",
            f"    {f.args!r},",
            f"    [{tuple_repr}],",
            f")",
            f"def test_{f.name}({', '.join(f.args)}):",
            f"    result = {call}",
            "    assert result is not None",
            "",
        ]
    return "\n".join(line for line in lines if line != "" or True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="Python module to analyze")
    parser.add_argument("--out", default="", help="Output file (default: stdout)")
    args = parser.parse_args()

    try:
        with open(args.file, encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        sys.exit(f"❌ Cannot read {args.file}: {e}")

    funcs = collect_functions(source)
    if not funcs:
        sys.exit(f"⚠️ No public functions found in {args.file}")

    module_name = args.file.rsplit("/", 1)[-1].rsplit(".py", 1)[0]
    code = render_pytest(funcs, module_name)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(code + "\n")
        print(f"✅ Wrote {args.out}")
    else:
        print(code)


if __name__ == "__main__":
    main()