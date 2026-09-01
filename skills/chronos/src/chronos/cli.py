import argparse
import sys
from pathlib import Path
from .core.reader import discover
from .core.reporter import generate_report
from .agents.canon import Canon


def main():
    parser = argparse.ArgumentParser(
        description="Chronos — AI agents for documentation integrity"
    )
    parser.add_argument("--path", default=".", help="Path to project")
    parser.add_argument(
        "--preset",
        choices=["minimal", "standard", "full"],
        default="minimal",
        help="Agent preset"
    )
    parser.add_argument(
        "--output",
        choices=["json", "markdown", "both"],
        default="both",
        help="Output format"
    )
    parser.add_argument("--output-file", help="Output file path")
    parser.add_argument("--fail-on", choices=["critical", "warning", "nit"], help="Fail if issues found")
    
    args = parser.parse_args()
    
    path = Path(args.path).resolve()
    if not path.exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        sys.exit(2)
    
    documents = discover(str(path))
    
    canon = Canon()
    context = {"preset": args.preset, "project_path": str(path)}
    issues = canon.orchestrate(documents, context)
    
    meta = {
        "project_path": str(path),
        "preset": args.preset,
        "total_docs": len(documents)
    }
    
    reports = generate_report(meta, issues, args.output)
    
    if args.output_file:
        output_path = Path(args.output_file)
        for fmt, content in reports.items():
            if args.output == "both":
                file_path = output_path.with_suffix(f".{fmt}")
            else:
                file_path = output_path
            file_path.write_text(content, encoding="utf-8")
            print(f"Report saved to {file_path}")
    else:
        for content in reports.values():
            print(content)
    
    if args.fail_on:
        severity_order = {"critical": 0, "warning": 1, "nit": 2}
        fail_level = severity_order.get(args.fail_on, 2)
        for issue in issues:
            if severity_order.get(issue.severity, 2) <= fail_level:
                sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
