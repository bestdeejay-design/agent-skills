#!/usr/bin/env python3
"""Generate a structured debug report (Iron Law debugging process).

Collects environment facts and phases into a Markdown report:
Environment / Command / Expected / Actual / Hypotheses (1..3) / Regression plan.

Usage:
    python3 debug_log.py --label "auth_flow" \
        --command "pytest tests/test_auth.py -k login" \
        --expected "login succeeds" --actual "401 Unauthorized"
"""
import argparse
import platform
import sys
import datetime


def env_snapshot() -> dict[str, str]:
    return {
        "os": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    }


def render_report(
    label: str,
    command: str,
    expected: str,
    actual: str,
    hypotheses: list[str],
) -> str:
    lines = [
        f"# Debug report: {label}",
        "",
        f"> Generated: {datetime.date.today().isoformat()}",
        "",
        "## Environment",
    ]
    for k, v in env_snapshot().items():
        lines.append(f"- {k}: {v}")
    lines += ["", "## Command", f"```bash\n{command}\n```", "", "## Expected", f"- {expected}", "", "## Actual", f"- {actual}", ""]
    lines += ["## Hypotheses (to verify one at a time)"]
    for i, h in enumerate(hypotheses, 1):
        lines.append(f"{i}. {h} — check: (how to verify), expected: (result)")
    lines += ["", "## Regression plan", "- [ ] Add a test that would have caught this bug", "- [ ] Run related test suite after fix"]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True, help="Short bug name")
    parser.add_argument("--command", default="", help="Command/file that reproduces")
    parser.add_argument("--expected", default="", help="Expected behavior")
    parser.add_argument("--actual", default="", help="Actual behavior")
    opts, extra = parser.parse_known_args()
    hypotheses = extra or ["hypothesis one", "hypothesis two", "hypothesis three"]
    print(render_report(opts.label, opts.command, opts.expected, opts.actual, hypotheses))
    return 0


if __name__ == "__main__":
    sys.exit(main())