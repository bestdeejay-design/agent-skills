#!/usr/bin/env python3
"""coverage-analyzer — parse coverage.py XML reports into a readable analysis.

Reads a coverage.py XML report (produced by `coverage xml`, typically after
`coverage run -m pytest`) and prints a markdown-friendly summary:

  * total line-rate (and branch-rate when the report measured branches)
  * count of files with zero coverage (line-rate == 0)
  * the 10 worst files (lowest line-rate, ascending)
  * a delta table vs an optional stored JSON baseline (before -> after -> delta)
  * a PASS/FAIL verdict against an optional --threshold (CI gate)

Baseline JSON format (written by --save-baseline, read by --baseline):

    {"files": [{"name": "src/foo.py", "line_rate": 0.42}, ...], "total": 0.42}

Usage:

    python3 coverage_analyzer.py --xml coverage.xml
    python3 coverage_analyzer.py --xml coverage.xml --baseline baseline.json
    python3 coverage_analyzer.py --xml coverage.xml --threshold 80
    python3 coverage_analyzer.py --xml coverage.xml --save-baseline baseline.json

Exit codes:
    0  analysis succeeded (threshold PASS, or no threshold given)
    1  parse/read error, or threshold FAIL
    2  internal error

Dependencies: Python 3 stdlib only (xml.etree.ElementTree, json, argparse).
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional


class ParseError(Exception):
    """Unreadable or malformed input (XML report or baseline JSON)."""


def parse_rate(value: Optional[str]) -> Optional[float]:
    """Parse a coverage.py rate attribute ('0.87') to float; None if absent."""
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_xml(path: Path) -> ET.Element:
    """Parse the XML report; raise ParseError on malformed/unreadable input."""
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        raise ParseError(f"malformed XML in {path}: {exc}") from exc
    except OSError as exc:
        raise ParseError(f"cannot read {path}: {exc}") from exc
    return tree.getroot()


def extract(root: ET.Element) -> dict:
    """Flatten total + per-file rates out of a coverage.py XML root element."""
    total_rate = parse_rate(root.get("line-rate"))
    branch_rate = parse_rate(root.get("branch-rate"))
    # A branch-rate of 0 with 0 valid branches means branches were never
    # measured (coverage.py default) — treat it as absent, not as 0%.
    if parse_rate(root.get("branches-valid")) == 0:
        branch_rate = None
    files = []
    for cls in root.iter("class"):
        name = cls.get("name") or cls.get("filename") or "<unknown>"
        files.append(
            {
                "name": name,
                "line_rate": parse_rate(cls.get("line-rate")) or 0.0,
                "branch_rate": parse_rate(cls.get("branch-rate")),
            }
        )
    files.sort(key=lambda f: (f["line_rate"], f["name"]))
    return {"total_rate": total_rate, "branch_rate": branch_rate, "files": files}


def load_baseline(path: Path) -> dict:
    """Read a baseline JSON; raise ParseError on unreadable/invalid input."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ParseError(f"cannot read baseline {path}: {exc}") from exc
    files = payload.get("files", [])
    if not isinstance(files, list):
        raise ParseError(f"baseline {path}: 'files' must be a list")
    return {"files": files, "total": payload.get("total")}


def save_baseline(path: Path, data: dict) -> None:
    """Persist current totals as a baseline JSON ({files:[...], total:x})."""
    payload = {
        "files": [{"name": f["name"], "line_rate": f["line_rate"]} for f in data["files"]],
        "total": data["total_rate"],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def pct(rate: Optional[float]) -> str:
    return "n/a" if rate is None else f"{rate * 100:.1f}%"


def verdict(total: Optional[float], threshold: float) -> tuple[str, int]:
    """PASS/FAIL verdict text + exit code for a threshold gate."""
    if total is None:
        return "FAIL — report has no line-rate attribute", 1
    if total * 100 >= threshold:
        return f"PASS — total {pct(total)} >= threshold {threshold:.0f}%", 0
    return f"FAIL — total {pct(total)} < threshold {threshold:.0f}%", 1


def build_report(xml_path: str, data: dict, baseline: Optional[dict], threshold: Optional[float]) -> str:
    total = data["total_rate"]
    lines = [f"# Coverage analysis: {xml_path}", ""]

    lines.append("## Total")
    lines.append(f"- line-rate: {total:.4f} ({pct(total)})")
    if data["branch_rate"] is not None:
        lines.append(f"- branch-rate: {data['branch_rate']:.4f} ({pct(data['branch_rate'])})")
    lines.append(f"- files: {len(data['files'])}")
    zero = [f for f in data["files"] if f["line_rate"] == 0.0]
    lines.append(f"- files_with_zero_lines: {len(zero)}")
    if zero:
        names = ", ".join(f["name"] for f in zero[:10])
        suffix = "…" if len(zero) > 10 else ""
        lines.append(f"  (zero-coverage files: {names}{suffix})")
    lines.append("")

    lines.append("## Worst 10 files (lowest line-rate)")
    lines.append("| # | file | line-rate |")
    lines.append("|---|------|-----------|")
    for i, f in enumerate(data["files"][:10], start=1):
        lines.append(f"| {i} | {f['name']} | {f['line_rate']:.4f} ({pct(f['line_rate'])}) |")
    lines.append("")

    if baseline is not None:
        lines.append("## Delta vs baseline")
        lines.append("| file | before | after | Δ |")
        lines.append("|------|--------|-------|---|")
        base = {f.get("name"): f.get("line_rate") for f in baseline["files"]}
        for f in data["files"]:
            before = base.get(f["name"])
            after = f["line_rate"]
            delta = "new" if before is None else f"{(after - before) * 100:+.1f} pp"
            lines.append(f"| {f['name']} | {pct(before)} | {pct(after)} | {delta} |")
        base_total = baseline.get("total")
        if base_total is not None and total is not None:
            lines.append(f"| **total** | {pct(base_total)} | {pct(total)} | {(total - base_total) * 100:+.1f} pp |")
        lines.append("")

    if threshold is not None:
        text, _ = verdict(total, threshold)
        lines.append(f"## Verdict\n{text}")

    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="coverage_analyzer.py",
        description="Analyze a coverage.py XML report: totals, zero-coverage files, worst-10 ranking, baseline delta, threshold verdict.",
    )
    parser.add_argument("--xml", default="coverage.xml", help="coverage.py XML report (default: coverage.xml)")
    parser.add_argument("--baseline", metavar="FILE.json", help="stored baseline JSON to diff against")
    parser.add_argument("--threshold", type=float, metavar="N", help="minimum total line-rate percent (0-100); FAIL exits 1")
    parser.add_argument("--save-baseline", metavar="FILE.json", help="write current totals as a baseline JSON and exit")
    args = parser.parse_args(argv)

    try:
        data = extract(parse_xml(Path(args.xml)))
    except ParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # unexpected — internal error
        print(f"internal error: {exc}", file=sys.stderr)
        return 2

    if args.save_baseline:
        try:
            save_baseline(Path(args.save_baseline), data)
        except OSError as exc:
            print(f"error: cannot write baseline {args.save_baseline}: {exc}", file=sys.stderr)
            return 1
        print(f"baseline saved to {args.save_baseline} (total {data['total_rate']:.4f})")
        return 0

    baseline = None
    if args.baseline:
        try:
            baseline = load_baseline(Path(args.baseline))
        except ParseError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    print(build_report(args.xml, data, baseline, args.threshold))
    if args.threshold is not None:
        _, code = verdict(data["total_rate"], args.threshold)
        return code
    return 0


if __name__ == "__main__":
    sys.exit(main())