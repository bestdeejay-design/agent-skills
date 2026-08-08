#!/usr/bin/env python3
"""Generate a Keep-a-Changelog section from git history (Conventional Commits).

Run inside a git repository:
    python3 changelog_gen.py --repo . --from-tag v1.0.0 --version 1.1.0
    python3 changelog_gen.py --repo . --top (unreleased, latest tag..HEAD)

Parses `git log --format=%H%x00%an%x00%aI%x00%s%x00%b%x1e <tag>..HEAD`,
classifies commits by Conventional Commits type, and renders Markdown
sections: Added / Fixed / Changed / Breaking.

Mappings (default):
    feat             -> Added
    fix              -> Fixed
    perf, refactor   -> Changed
    breaking (!) or BREAKING CHANGE footer -> Breaking Changes
    docs/style/test/build/ci/chore/revert  -> hidden (can be forced with --all)
"""
import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass

TYPE_SECTIONS = {
    "feat": "Added",
    "fix": "Fixed",
    "perf": "Changed",
    "refactor": "Changed",
    "revert": "Reverts",
}
HIDE_TYPES = {"docs", "style", "test", "build", "ci", "chore", "merge"}


@dataclass
class Commit:
    hash: str
    author: str
    date: str
    subject: str
    body: str
    breaking: bool = False

    @property
    def short_hash(self) -> str:
        return self.hash[:7]

    @property
    def type(self) -> str:
        m = re.match(r"^(\w+)(\(.+\))?(!)?:", self.subject)
        return m.group(1) if m else ""

    @property
    def description(self) -> str:
        m = re.match(r"^(\w+)(\(.+\))?(!)?:\s*(.+)", self.subject, re.DOTALL)
        return m.group(4).strip() if m else self.subject.strip()

    @property
    def scope(self) -> str:
        m = re.match(r"^(\w+)\(([^)]+)\)", self.subject)
        return m.group(2) if m else ""


def run_git(repo: str, args: list[str]) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", repo, *args],
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout
    except subprocess.CalledProcessError as e:
        sys.exit(f"❌ git error: {e.stderr.strip()}")


def find_previous_tag(repo: str) -> str:
    tags = run_git(repo, ["tag", "--sort=-version:refname"]).splitlines()
    return tags[0] if tags else ""


def parse_commits(repo: str, since: str) -> list[Commit]:
    RS, FS = "\x1e", "\x00"
    git_fmt = "%H%x00%an%x00%aI%x00%s%x00%b%x1e"
    raw = run_git(repo, ["log", "--format=" + git_fmt, f"{since}..HEAD"])
    commits: list[Commit] = []
    for record in raw.split(RS):
        record = record.strip()
        if not record:
            continue
        fields = record.split(FS)
        if len(fields) < 4:
            continue
        h, author, date, subject = fields[:4]
        body = fields[4] if len(fields) > 4 else ""
        result = Commit(hash=h, author=author, date=date, subject=subject, body=body)
        result.breaking = bool(
            re.search(r"BREAKING CHANGE\s*:", body, re.IGNORECASE)
            or re.search(r"!:$", subject)
        )
        commits.append(result)
    return commits


def render_changelog(commits: list[Commit], version: str, date: str, all_types: bool) -> str:
    sections: dict[str, list[str]] = {s: [] for s in ["Added", "Changed", "Fixed", "Breaking", "Reverts"]}
    hidden: set[str] = HIDE_TYPES
    for c in commits:
        if c.type in hidden and not all_types:
            continue
        if c.breaking:
            line = f"- {c.description}"
            if c.scope:
                line += f" ({c.scope})"
            line += f" ([{c.short_hash}](https://github.com/bestdeejay-design/agent-skills/commit/{c.hash}))"
            sections["Breaking"].append(line)
            continue
        target = TYPE_SECTIONS.get(c.type, "Changed")
        if target not in sections:
            if all_types:
                sections[target] = []
            else:
                continue
        line = f"- {c.description} ([{c.short_hash}](https://github.com/bestdeejay-design/agent-skills/commit/{c.hash}))"
        sections[target].append(line)

    out = [f"## {version} — {date}", ""]
    any_content = False
    for name in ["Added", "Changed", "Fixed", "Breaking", "Reverts"]:
        if sections[name]:
            out.append(f"### {name}")
            out.extend(sorted(sections[name]))
            out.append("")
            any_content = True
    if not any_content:
        out.append("_Нет изменений в этом диапазоне._")
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Path to git repository")
    parser.add_argument("--from-tag", default="", help="Compare tag..HEAD (default: latest tag)")
    parser.add_argument("--version", default="Unreleased", help="Version header text")
    parser.add_argument("--date", default="", help="Date (default: today)")
    parser.add_argument("--top", action="store_true", help="Print only the unreleased section")
    parser.add_argument("--all", action="store_true", help="Include hidden types (docs/ci/chore/...)")
    parser.add_argument("--out", default="", help="Write to file instead of stdout")
    args = parser.parse_args()

    since = args.from_tag or find_previous_tag(args.repo)
    if not since:
        sys.exit("❌ No tag found. Pass --from-tag explicitly.")
    commits = parse_commits(args.repo, since)
    date = args.date or os.popen("date +%Y-%m-%d").read().strip()
    text = render_changelog(commits, args.version, date, args.all)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"✅ Wrote {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()