#!/usr/bin/env python3
"""Suggest a Conventional Commits message from a staged git diff.

Usage:
    python3 suggest.py [--cached|--unstaged] [--scope <s>] [--emoji] [-c]

Reads `git diff` (staged by default), infers the commit type and scope from
the changed paths, and prints a ready-to-paste commit message. Never commits.

Exit codes: 0 = message printed; 1 = nothing staged / not a git repo.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# --- Type heuristics ----------------------------------------------------
# (regex on lowercased changed path, gitmoji, type)

PATH_RULES: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"(^|/)(docs?|README(\.ru)?\.md|CHANGELOG|guides?)(/|$|\.)"), "", "docs"),
    (re.compile(r"(^|/)(tests?|specs?|__tests__|\.test\.|\.spec\.)(/|$|\.)"), "", "test"),
    (re.compile(r"(^|/)(\.github|workflows?|ci|\.gitlab-ci|azure-pipelines)(/|$|\.)"), "", "ci"),
    (re.compile(r"(^|/)(Dockerfile|docker-compose|Makefile|\.dockerignore|\.nvmrc)(/|$|\.)"), "", "build"),
    (re.compile(r"(^|/)(build|dist|vendor)(/|$|\.)"), "", "build"),
    (re.compile(r"(^|/)(package\.json|pnpm-lock\.yaml|yarn\.lock|package-lock\.json|poetry\.lock)(/|$|\.)"), "", "build"),
    (re.compile(r"(^|/)(perf|benchmarks?)(/|$|\.)"), "", "perf"),
    (re.compile(r"(^|/)(refactor|internal|core)(/|$|\.)"), "", "refactor"),
]


SCOPE_HINTS: dict[str, str] = {
    "routes/": "api",
    "controllers/": "api",
    "endpoints/": "api",
    "handlers/": "api",
    "services/": "core",
    "core/": "core",
    "components/": "ui",
    "styles/": "ui",
    "pages/": "ui",
    "app/": "app",
}

GITMOJI: dict[str, str] = {
    "feat": "✨",
    "fix": "🐛",
    "docs": "📚",
    "test": "✅",
    "ci": "🔧",
    "build": "📦",
    "perf": "⚡",
    "refactor": "♻️",
    "chore": "🧹",
}


# --- git helpers -------------------------------------------------------


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    """Run git, swallow errors."""
    return subprocess.run(
        ["git", *args],
        capture_output=True, text=True, check=False,
    )


def get_changed_paths(cached: bool) -> list[str]:
    base = ["--cached"] if cached else []
    res = run_git("diff", *base, "--name-only", "-z")
    if res.returncode != 0:
        return []
    return [p for p in res.stdout.split("\0") if p]


def get_diff(cached: bool) -> str:
    base = ["--cached"] if cached else []
    res = run_git("diff", *base, "--no-ext-diff", "--unified=0")
    if res.returncode != 0:
        return ""
    return res.stdout


def detect_breaking(diff: str) -> bool:
    if re.search(r"BREAKING CHANGE:", diff):
        return True
    # Heuristic: removal of a public function/class definition (a `-` line).
    if re.search(r"^-\s*(export )?(async )?(function|class|def)\s+\w+", diff, re.M):
        return True
    return False


def detect_type(paths: list[str]) -> str:
    """Score types by path hints; fall back to 'chore'."""
    scores: dict[str, int] = {}
    for p in paths:
        low = p.lower()
        for regex_p, _emoji, typ in PATH_RULES:
            if regex_p.search(low):
                scores[typ] = scores.get(typ, 0) + 1
        for hint, typ in SCOPE_HINTS.items():
            if hint in low:
                scores[typ] = scores.get(typ, 0) + 1
        if not scores:
            scores["chore"] = scores.get("chore", 0) + 1
    if not scores:
        return "chore"
    return max(scores, key=scores.get)  # type: ignore[arg-type]


def detect_scope(paths: list[str]) -> str | None:
    scopes: dict[str, int] = {}
    for p in paths:
        low = p.lower()
        for hint, scope in SCOPE_HINTS.items():
            if hint in low:
                scopes[scope] = scopes.get(scope, 0) + 1
    if not scopes:
        return None
    return max(scopes, key=scopes.get)  # type: ignore[arg-type]


def summarize(paths: list[str]) -> str:
    """One-line imperative summary built from the most symbolic changed path."""
    for p in sorted(paths):
        stem = Path(p).stem.replace("_", " ").replace("-", " ").strip()
        if stem and stem not in ("index", "app", "main", "bootstrap"):
            return f"update {stem}"
    return "update repository content"


def build_message(
    scope: str | None, typ: str, emoji: bool, subject: str, diff: str, paths: list[str]
) -> str:
    breaking = detect_breaking(diff)
    prefix = f"{typ}{'!' if breaking else ''}"
    if emoji:
        prefix = f"{GITMOJI.get(typ, '')} {prefix}"
    sc = f"({scope})" if scope else ""
    lines = [f"{prefix}{sc}: {subject}"]
    if breaking:
        lines.append("")
        lines.append("BREAKING CHANGE: this change is not backwards compatible.")
    if len(paths) > 1:
        lines.append("")
        lines.append("Affects:")
        for p in sorted(paths)[:6]:
            lines.append(f"- {p}")
        if len(paths) > 6:
            lines.append(f"- …and {len(paths) - 6} more")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Suggest a Conventional Commits message")
    ap.add_argument("--cached", action="store_true", help="use staged changes (default)")
    ap.add_argument("--unstaged", action="store_true", help="use working-tree diff instead")
    ap.add_argument("--scope", help="force a scope instead of detecting")
    ap.add_argument("--emoji", action="store_true", help="prefix with gitmoji")
    ap.add_argument("-c", "--copy", action="store_true", help="copy to clipboard (pbcopy/xclip)")
    args = ap.parse_args()

    if not (os.path.isdir(".git") or run_git("rev-parse", "--is-inside-work-tree").stdout.strip()):
        print("error: not inside a git working tree", file=sys.stderr)
        return 1

    cached = args.cached and not args.unstaged
    paths = get_changed_paths(cached)
    if not paths:
        print(
            "error: no changes to analyze"
            + (" (run 'git add' first)" if cached else ""),
            file=sys.stderr,
        )
        return 1

    diff = get_diff(cached)
    typ = detect_type(paths)
    scope = args.scope or detect_scope(paths)
    subject = summarize(paths)
    msg = build_message(scope, typ, args.emoji, subject, diff, paths)

    print(msg)
    if args.copy:
        try:
            subprocess.run(["pbcopy"], input=msg, text=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            try:
                subprocess.run(["xclip", "-selection", "clipboard"], input=msg, text=True, check=True)
            except Exception:
                pass
    return 0


if __name__ == "__main__":
    sys.exit(main())