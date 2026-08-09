#!/usr/bin/env python3
"""Suggest the next semantic version from Conventional Commits in git history.

Usage:
    python3 bumper.py [--path REPO] [--current X.Y.Z | --from-tags] [--dry-run] [-s]
    python3 bumper.py --commits FILE --current X.Y.Z   # no git required

Reads commit subjects from `git log` (subprocess). For testability the commit
list can come from the COMMITS environment variable or a file passed with
--commits (one subject per line). Classifies each commit by Conventional
Commits type and prints the current version, the next version and a suggested
release tag.

Bump rules (Conventional Commits v1.0.0):
    breaking (! marker or "BREAKING CHANGE:" footer)  -> MAJOR
    feat                                              -> MINOR
    fix, perf, refactor                               -> PATCH
    docs, style, test, chore, build, ci, revert, other -> no bump

The tool is read-only: it never creates tags. --dry-run is accepted for
pipeline compatibility and is the default behavior.

Exit codes: 0 on success with meaningful output, 1 on error (missing git
repo, invalid --current, unreadable --commits file, git not installed).
"""
import argparse
import os
import re
import subprocess
import sys

# Preset Conventional Commits types, in stable output order.
KNOWN_TYPES = [
    "feat", "fix", "perf", "refactor",
    "docs", "style", "test", "chore",
    "build", "ci", "revert",
]
# Types that trigger a version bump.
BUMP_TYPES = {"feat": "minor", "fix": "patch", "perf": "patch", "refactor": "patch"}

SUBJECT_RE = re.compile(r"^([a-zA-Z]+)(?:\([^)]*\))?(!)?:\s*(.*)$")
SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$")
BREAKING_RE = re.compile(r"BREAKING CHANGE\s*:", re.IGNORECASE)


def parse_version(text: str) -> tuple[int, int, int] | None:
    """Parse 'X.Y.Z' or 'vX.Y.Z' into (major, minor, patch)."""
    m = SEMVER_RE.match(text.strip())
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def format_version(version: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in version)


def classify(subject: str, body: str = "") -> tuple[str, bool]:
    """Return (type, breaking) for one commit subject + optional body."""
    breaking = bool(BREAKING_RE.search(body))
    m = SUBJECT_RE.match(subject.strip())
    if not m:
        return ("other", breaking)
    ctype = m.group(1).lower()
    if m.group(2) == "!":
        breaking = True
    if ctype not in KNOWN_TYPES:
        return ("other", breaking)
    return (ctype, breaking)


def compute_bump(commits: list[tuple[str, bool]]) -> str:
    """Return 'major' | 'minor' | 'patch' | 'none' for the commit list."""
    if any(breaking for _, breaking in commits):
        return "major"
    if any(ctype == "feat" for ctype, _ in commits):
        return "minor"
    if any(ctype in ("fix", "perf", "refactor") for ctype, _ in commits):
        return "patch"
    return "none"


def bump_version(current: tuple[int, int, int], level: str) -> tuple[int, int, int]:
    major, minor, patch = current
    if level == "major":
        return (major + 1, 0, 0)
    if level == "minor":
        return (major, minor + 1, 0)
    if level == "patch":
        return (major, minor, patch + 1)
    return current


def check_repo(repo: str) -> None:
    try:
        subprocess.run(
            ["git", "-C", repo, "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, check=True,
        )
    except FileNotFoundError:
        sys.exit("error: git executable not found in PATH")
    except subprocess.CalledProcessError:
        sys.exit(f"error: {repo} is not a git repository")


def git_log(repo: str) -> list[tuple[str, str]]:
    """Return [(subject, body)] from git log, newest first."""
    fmt = "%s%x00%b%x1e"
    try:
        out = subprocess.run(
            ["git", "-C", repo, "log", "--format=" + fmt],
            capture_output=True, text=True, check=True,
        ).stdout
    except FileNotFoundError:
        sys.exit("error: git executable not found in PATH")
    except subprocess.CalledProcessError as e:
        sys.exit(f"error: git log failed in {repo}: {e.stderr.strip()}")
    commits: list[tuple[str, str]] = []
    for record in out.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        parts = record.split("\x00")
        subject = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else ""
        if subject:
            commits.append((subject, body))
    return commits


def latest_tag(repo: str) -> tuple[str, tuple[int, int, int]] | None:
    """Return (tag, version) of the highest semver tag, or None."""
    try:
        out = subprocess.run(
            ["git", "-C", repo, "tag", "--list"],
            capture_output=True, text=True, check=True,
        ).stdout
    except subprocess.CalledProcessError as e:
        sys.exit(f"error: cannot list tags in {repo}: {e.stderr.strip()}")
    best: tuple[str, tuple[int, int, int]] | None = None
    for tag in out.splitlines():
        m = SEMVER_RE.match(tag.strip())
        if not m:
            continue
        version = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if best is None or version > best[1]:
            best = (tag.strip(), version)
    return best


def read_commits_file(path: str) -> list[tuple[str, str]]:
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError as e:
        sys.exit(f"error: cannot read commits file {path}: {e}")
    return [(line.strip(), "") for line in lines if line.strip()]


def read_commits_env() -> list[tuple[str, str]]:
    raw = os.environ.get("COMMITS", "")
    return [(line.strip(), "") for line in raw.splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", default=".", help="Path to git repository (default: .)")
    parser.add_argument("--current", default="", help="Current version X.Y.Z (default: latest tag)")
    parser.add_argument("--from-tags", action="store_true",
                        help="Take the current version from the latest semver tag")
    parser.add_argument("--commits", default="",
                        help="Read commit subjects from FILE (one per line) instead of git log")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the suggestion without creating anything (default; tool is read-only)")
    parser.add_argument("-s", "--stable", action="store_true",
                        help="Deterministic output: sort commits, assert stable next_version for identical input")
    args = parser.parse_args()

    # Resolve the current version.
    if args.current:
        current = parse_version(args.current)
        if current is None:
            sys.exit(f"error: invalid --current {args.current!r}; expected X.Y.Z")
        latest = args.current.strip()
    elif args.from_tags or not args.commits:
        check_repo(args.path)
        tag = latest_tag(args.path)
        if tag is None:
            print(f"warning: no semver tags found in {args.path}; starting from 0.0.0",
                  file=sys.stderr)
            latest, current = "none", (0, 0, 0)
        else:
            latest, current = tag
    else:
        latest, current = "none", (0, 0, 0)

    # Resolve the commit list.
    if args.commits:
        commits = read_commits_file(args.commits)
    elif os.environ.get("COMMITS"):
        commits = read_commits_env()
    else:
        check_repo(args.path)
        commits = git_log(args.path)

    classified = [classify(subject, body) for subject, body in commits]
    if args.stable:
        classified.sort(key=lambda item: (item[0], item[1]))

    counts = {ctype: 0 for ctype in KNOWN_TYPES}
    counts["breaking"] = 0
    counts["other"] = 0
    for ctype, breaking in classified:
        counts[ctype] += 1
        if breaking:
            counts["breaking"] += 1

    bump = compute_bump(classified)
    next_version = bump_version(current, bump)
    counts_line = ", ".join(f"{k}={counts[k]}" for k in [*KNOWN_TYPES, "breaking", "other"])

    print(f"latest_tag: {latest}")
    print(f"current_version: {format_version(current)}")
    print(f"next_version: {format_version(next_version)}")
    print(f"suggested_tag: v{format_version(next_version)}")
    print(f"bump: {bump}")
    print(f"commits_analyzed: {len(classified)}")
    print(f"counts: {counts_line}")
    if args.stable:
        print("stable: true")
    if args.dry_run:
        print("dry_run: true")


if __name__ == "__main__":
    main()