#!/usr/bin/env python3
"""commit_lint.py — validate git commit messages against Conventional Commits.

Usage:
    python3 commit_lint.py [PATH ...] [--repo REPO] [--count N] [--stdin] [--json]
                           [--max-subject N] [--max-header N] [--max-body-line N]
                           [--no-subject-case] [--no-trailing-dot]

Reads commit messages from `git log` (subprocess) of one or more git
repositories, or from stdin (--stdin, one commit per line:
[hash<TAB>]subject). Each commit is parsed and validated against the
Conventional Commits v1.0.0 format:

    <type>[optional scope][!]: <description>

Rules enforced (each violation is reported per commit):

  missing-type       no conventional-commit prefix found
  invalid-type       type not in the allowed set (conventional-commits.org)
  type-case          type must be lowercase (Feat: is a violation)
  scope-invalid      scope must be non-empty and contain no spaces
  empty-subject      no description after '<type>: '
  space-after-colon  exactly one space required after ':'
  subject-too-long   subject longer than --max-subject (default 50)
  header-too-long    full header longer than --max-header (default 100)
  subject-case       subject must start with a lowercase letter or digit
  trailing-dot       subject must not end with '.'
  trailing-space     subject must not end with whitespace
  body-line-too-long body line longer than --max-body-line (default 72)

The report is a plain-text Markdown-friendly listing (or JSON with --json)
with per-commit type/scope/subject, the violation list, and a summary.

Exit codes:
    0  all analyzed commits are clean
    1  at least one commit has violations
    2  error (not a git repo, git not installed, bad arguments, unreadable input)
"""
import argparse
import collections
import datetime
import json
import re
import subprocess
import sys

__version__ = "1.0.0"

# Friendly preset type set (conventional-commits.org v1.0.0).
ALLOWED_TYPES = [
    "feat", "fix", "docs", "style", "refactor",
    "test", "perf", "ci", "chore", "build", "revert",
]

HEADER_RE = re.compile(r"^([A-Za-z]+)(?:\(([^)]*)\))?(!)?:\s*(.*)$")

VIOLATION_DESCRIPTIONS = {
    "missing-type": "no conventional-commit prefix '<type>(<scope>)?(!)?: <subject>'",
    "invalid-type": "type not in allowed set: " + ", ".join(ALLOWED_TYPES),
    "type-case": "type must be lowercase",
    "scope-invalid": "scope must be non-empty and contain no spaces",
    "empty-subject": "no description after '<type>: '",
    "space-after-colon": "exactly one space required after ':'",
    "subject-too-long": "subject is longer than the configured maximum",
    "header-too-long": "full header is longer than the configured maximum",
    "subject-case": "subject must start with a lowercase letter or digit",
    "trailing-dot": "subject must not end with '.'",
    "trailing-space": "subject must not end with whitespace",
    "body-line-too-long": "body line is longer than the configured maximum",
}


class LintError(Exception):
    """Fatal, user-facing error (bad repo, missing git, bad input)."""


def parse_header(line: str) -> dict | None:
    """Parse one commit header into {type, scope, breaking, subject} or None."""
    m = HEADER_RE.match(line)
    if not m:
        return None
    return {
        "type": m.group(1),
        "scope": m.group(2),
        "breaking": m.group(3) == "!",
        "subject": m.group(4),
    }


def lint_commit(hash_: str, subject: str, body: str, opts: dict) -> dict:
    """Validate one commit; return a report dict with a violations list."""
    violations: list[str] = []
    parsed = parse_header(subject)
    if parsed is None:
        violations.append("missing-type")
        return {
            "hash": hash_, "subject": subject,
            "type": None, "scope": None, "breaking": False,
            "violations": violations,
        }

    ctype = parsed["type"]
    scope = parsed["scope"]
    breaking = parsed["breaking"]
    subject_text = parsed["subject"]

    if ctype.lower() not in ALLOWED_TYPES:
        violations.append("invalid-type")
    if ctype != ctype.lower():
        violations.append("type-case")
    if scope is not None and (scope == "" or " " in scope):
        violations.append("scope-invalid")
    if subject_text == "":
        violations.append("empty-subject")

    colon = subject.find(":")
    if colon != -1 and (colon + 1 >= len(subject) or subject[colon + 1] != " "):
        violations.append("space-after-colon")

    if len(subject) > opts["max_subject"]:
        violations.append("subject-too-long")
    if len(subject) > opts["max_header"]:
        violations.append("header-too-long")
    if opts["check_case"] and subject_text and subject_text[0].isupper():
        violations.append("subject-case")
    if opts["check_dot"] and subject_text.endswith("."):
        violations.append("trailing-dot")
    if subject_text != subject_text.rstrip():
        violations.append("trailing-space")
    for line in body.splitlines():
        if len(line) > opts["max_body_line"]:
            violations.append("body-line-too-long")
            break

    return {
        "hash": hash_, "subject": subject,
        "type": ctype, "scope": scope, "breaking": breaking,
        "violations": violations,
    }


def check_repo(repo: str) -> None:
    try:
        subprocess.run(
            ["git", "-C", repo, "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, check=True,
        )
    except FileNotFoundError:
        raise LintError("git executable not found in PATH")
    except subprocess.CalledProcessError:
        raise LintError(f"{repo} is not a git repository")


def detect_repo() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout
    except FileNotFoundError:
        raise LintError("git executable not found in PATH")
    except subprocess.CalledProcessError:
        raise LintError(
            "current directory is not inside a git repository; "
            "pass a PATH or use --repo"
        )
    return out.strip()


def git_log(repo: str, count: int) -> list[tuple[str, str, str]]:
    """Return [(hash, subject, body)] from git log, newest first."""
    cmd = ["git", "-C", repo, "log", "--format=%H%x00%s%x00%b%x1e"]
    if count and count > 0:
        cmd += ["-n", str(count)]
    try:
        out = subprocess.run(
            cmd, capture_output=True, text=True, check=True,
        ).stdout
    except FileNotFoundError:
        raise LintError("git executable not found in PATH")
    except subprocess.CalledProcessError as e:
        raise LintError(f"git log failed in {repo}: {e.stderr.strip()}")
    commits: list[tuple[str, str, str]] = []
    for record in out.split("\x1e"):
        # git log appends a newline after each record; strip only newlines so
        # that trailing whitespace inside a subject/body is preserved.
        record = record.strip("\n")
        if not record:
            continue
        parts = record.split("\x00")
        if len(parts) >= 2 and parts[0] and parts[1]:
            body = parts[2] if len(parts) > 2 else ""
            commits.append((parts[0], parts[1], body))
    return commits


def read_stdin() -> list[tuple[str, str, str]]:
    """Read commits from stdin: one per line, [hash<TAB>]subject."""
    commits: list[tuple[str, str, str]] = []
    for line in sys.stdin.read().splitlines():
        line = line.rstrip("\r")
        if not line.strip():
            continue
        if "\t" in line:
            hash_, subject = line.split("\t", 1)
        else:
            hash_, subject = "(stdin)", line
        commits.append((hash_, subject, ""))
    return commits


def build_report(repo: str, commits: list[tuple[str, str, str]], opts: dict) -> dict:
    analyzed = [lint_commit(h, s, b, opts) for h, s, b in commits]
    clean = sum(1 for c in analyzed if not c["violations"])
    counter: dict[str, int] = {}
    for c in analyzed:
        for v in c["violations"]:
            counter[v] = counter.get(v, 0) + 1
    return {
        "tool": "commit-lint",
        "version": __version__,
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "repo": repo,
        "commits_analyzed": len(analyzed),
        "clean": clean,
        "with_violations": len(analyzed) - clean,
        "commits": analyzed,
        "violations_by_type": dict(sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))),
    }


def render_text(report: dict) -> str:
    lines: list[str] = []
    lines.append("commit-lint report")
    lines.append("=" * 18)
    lines.append(f"repo: {report['repo']}")
    lines.append(f"generated: {report['generated']}")
    lines.append(f"commits_analyzed: {report['commits_analyzed']}")
    lines.append(f"clean: {report['clean']}")
    lines.append(f"with_violations: {report['with_violations']}")
    lines.append("")
    for c in report["commits"]:
        short = c["hash"][:7] if c["hash"] != "(stdin)" else "(stdin)"
        if c["violations"]:
            lines.append(f"[FAIL] {short} {c['subject']}")
            t = c["type"] or "(none)"
            s = c["scope"] or "(none)"
            b = "yes" if c["breaking"] else "no"
            lines.append(f"         type: {t} | scope: {s} | breaking: {b}")
            lines.append(f"         subject: {c['subject']}")
            lines.append("         violations:")
            for v in c["violations"]:
                lines.append(f"           - {v}: {VIOLATION_DESCRIPTIONS.get(v, v)}")
        else:
            lines.append(f"[OK]   {short} {c['subject']}")
    lines.append("")
    lines.append("=== Violations by type ===")
    if report["violations_by_type"]:
        for code, count in report["violations_by_type"].items():
            lines.append(f"{code}: {count}")
    else:
        lines.append("(none)")
    lines.append("")
    lines.append(f"exit: {1 if report['with_violations'] else 0}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="commit_lint.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exit codes:\n"
            "  0  all analyzed commits are clean\n"
            "  1  at least one commit has violations\n"
            "  2  error (not a git repo, git not installed, bad input)\n"
        ),
    )
    parser.add_argument(
        "paths", nargs="*", metavar="PATH",
        help="git repository path(s) to lint (default: auto-detect from cwd)",
    )
    parser.add_argument(
        "--repo", default="", metavar="REPO",
        help="override the auto-detected git repository (single repo)",
    )
    parser.add_argument(
        "--stdin", action="store_true",
        help="read commit messages from stdin instead of git log "
             "(one per line: [hash<TAB>]subject)",
    )
    parser.add_argument(
        "--count", type=int, default=0, metavar="N",
        help="analyze only the N most recent commits (default: all)",
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_out",
        help="emit a machine-readable JSON report",
    )
    parser.add_argument(
        "--max-subject", type=int, default=50, metavar="N",
        help="maximum subject length in chars (default: 50)",
    )
    parser.add_argument(
        "--max-header", type=int, default=100, metavar="N",
        help="maximum full header length in chars (default: 100)",
    )
    parser.add_argument(
        "--max-body-line", type=int, default=72, metavar="N",
        help="maximum body line length in chars (default: 72)",
    )
    parser.add_argument(
        "--no-subject-case", action="store_true",
        help="disable the subject-capitalization check",
    )
    parser.add_argument(
        "--no-trailing-dot", action="store_true",
        help="disable the trailing-dot check",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.paths and args.repo:
        parser.error("cannot combine positional PATH(s) with --repo")
    if args.stdin and (args.paths or args.repo):
        parser.error("--stdin cannot be combined with PATH(s) or --repo")

    opts = {
        "max_subject": args.max_subject,
        "max_header": args.max_header,
        "max_body_line": args.max_body_line,
        "check_case": not args.no_subject_case,
        "check_dot": not args.no_trailing_dot,
    }

    if args.stdin:
        repos: list[str] | None = None
    elif args.paths:
        repos = args.paths
    elif args.repo:
        repos = [args.repo]
    else:
        repos = [detect_repo()]

    had_error = False
    had_violations = False
    reports: list[dict] = []

    if args.stdin:
        commits = read_stdin()
        report = build_report("(stdin)", commits, opts)
        reports.append(report)
        if report["with_violations"]:
            had_violations = True
    else:
        for repo in repos:
            try:
                check_repo(repo)
                commits = git_log(repo, args.count)
            except LintError as e:
                print(f"error: {e}", file=sys.stderr)
                had_error = True
                continue
            report = build_report(repo, commits, opts)
            reports.append(report)
            if report["with_violations"]:
                had_violations = True

    for report in reports:
        if args.json_out:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(render_text(report))

    if had_error:
        sys.exit(2)
    if had_violations:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()