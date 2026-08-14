#!/usr/bin/env python3
"""Validator for the agent-skills repository.

Pure Python 3 standard library only (no PyYAML, no requests, no third-party
dependencies). Validates the global catalog ``index.json`` and every skill
folder (``skill.json`` + ``SKILL.md``) for structural and consistency errors.

Exit codes:
  * 0 - no errors found (warnings are allowed)
  * 1 - one or more errors found
  * 2 - system error (missing files, unparseable index, bad arguments)

Usage:
  python3 scripts/validate_skills.py --all
  python3 scripts/validate_skills.py --files skills/secret-scanner/SKILL.md
  python3 scripts/validate_skills.py --all --json
  python3 scripts/validate_skills.py --all -q
"""

import argparse
import json
import os
import re
import sys

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

ALLOWED_CATEGORIES = {"code", "repository", "data", "media", "social"}
ALLOWED_SUBDIRS = {"references", "scripts", "assets", "templates", "examples", "commands"}
ALLOWED_TOPLEVEL_FILES = {
    "SKILL.md",
    "skill.json",
    "README.md",
    "README.ru.md",
    "readme.md",
    "readme.ru.md",
    "LICENSE",
    "ROADMAP.md",
    "showcase.md",
    "CHANGELOG.md",
}
IGNORED_TOPLEVEL_FILES = {".DS_Store", ".gitkeep"}

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PATH_CHARSET = set(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._/-"
)

REQUIRED_INDEX_ROOT_KEYS = (
    "name",
    "description",
    "version",
    "author",
    "license",
    "repository",
    "skills",
)

REQUIRED_SKILL_JSON_KEYS = (
    "name",
    "version",
    "description",
    "author",
    "license",
    "keywords",
    "triggers",
    "category",
    "entrypoint",
    "files",
)

# Progressive disclosure thresholds.
WARN_LINES = 500
WARN_CHARS = 20000
ERROR_LINES = 1500


# --------------------------------------------------------------------------- #
# Issue model
# --------------------------------------------------------------------------- #


class Issue:
    """A single validation finding."""

    __slots__ = ("severity", "message", "file")

    def __init__(self, severity, message, file):
        self.severity = severity  # "ERROR" or "WARNING"
        self.message = message
        self.file = file

    def to_dict(self):
        return {"severity": self.severity, "message": self.message, "file": self.file}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def rel_path(repo_root, absolute):
    """Return *absolute* expressed relative to *repo_root*."""
    return os.path.relpath(absolute, repo_root)


def unquote(value):
    """Strip a single pair of matching surrounding quotes from *value*."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def parse_frontmatter(text):
    """Parse a simple YAML frontmatter block.

    Returns a tuple ``(data, body)`` where *data* is a dict mapping both
    top-level keys and one level of nested keys (dotted, e.g. ``metadata.version``)
    to their (unquoted) string values, and *body* is the text after the closing
    ``---``. Returns ``(None, text)`` when no frontmatter block is present.
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        return None, text
    frontmatter = match.group(1)
    body = text[match.end():]
    data = {}
    parent = None
    for raw_line in frontmatter.splitlines():
        if not raw_line.strip():
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        key_match = re.match(r"^([A-Za-z0-9_.-]+):\s*(.*)$", raw_line.strip())
        if not key_match:
            parent = None
            continue
        key = key_match.group(1)
        value = unquote(key_match.group(2).strip())
        if indent == 0:
            data[key] = value
            parent = key
        elif parent is not None:
            data["{}.{}".format(parent, key)] = value
    return data, body


# --------------------------------------------------------------------------- #
# Index validation
# --------------------------------------------------------------------------- #


def validate_index(index, repo_root, skills_dir):
    """Validate the global catalog. Returns a list of Issue."""
    issues = []

    if not isinstance(index, dict):
        issues.append(Issue("ERROR", "index.json root is not a JSON object", "index.json"))
        return issues

    for key in REQUIRED_INDEX_ROOT_KEYS:
        if key not in index:
            issues.append(Issue("ERROR", "missing required root key: {}".format(key), "index.json"))

    name = index.get("name")
    if not isinstance(name, str) or not name.strip():
        issues.append(Issue("ERROR", "root 'name' must be a non-empty string", "index.json"))

    version = index.get("version")
    if not isinstance(version, str) or not SEMVER_RE.match(version or ""):
        issues.append(
            Issue("ERROR", "root 'version' must be semver (e.g. 1.7.2)", "index.json")
        )

    description = index.get("description")
    if not isinstance(description, str) or not description.strip():
        issues.append(
            Issue("ERROR", "root 'description' must be a non-empty string", "index.json")
        )

    skills = index.get("skills")
    if not isinstance(skills, list) or not skills:
        issues.append(Issue("ERROR", "root 'skills' must be a non-empty array", "index.json"))
        return issues

    registered = set()
    for entry in skills:
        if not isinstance(entry, dict):
            issues.append(Issue("ERROR", "skill entry is not an object", "index.json"))
            continue
        entry_issues = _validate_index_entry(entry, repo_root, skills_dir)
        issues.extend(entry_issues)
        if isinstance(entry.get("name"), str):
            registered.add(entry["name"])

    # Reverse registration: every folder under skills/ must be registered.
    if os.path.isdir(skills_dir):
        for folder in sorted(os.listdir(skills_dir)):
            folder_path = os.path.join(skills_dir, folder)
            if not os.path.isdir(folder_path):
                continue
            if folder not in registered:
                issues.append(
                    Issue(
                        "ERROR",
                        "skill folder '{}' is not registered in index.json".format(folder),
                        rel_path(repo_root, folder_path),
                    )
                )
    return issues


def _validate_index_entry(entry, repo_root, skills_dir):
    issues = []
    name = entry.get("name")
    if not isinstance(name, str) or not name.strip():
        issues.append(Issue("ERROR", "skill entry 'name' must be a non-empty string", "index.json"))
    elif not KEBAB_RE.match(name):
        issues.append(
            Issue("ERROR", "skill name '{}' is not kebab-case".format(name), "index.json")
        )

    version = entry.get("version")
    if not isinstance(version, str) or not SEMVER_RE.match(version or ""):
        issues.append(
            Issue(
                "ERROR",
                "skill entry '{}' version '{}' is not semver".format(name, version),
                "index.json",
            )
        )

    category = entry.get("category")
    if category not in ALLOWED_CATEGORIES:
        issues.append(
            Issue(
                "ERROR",
                "skill entry '{}' category '{}' not in allowed set {}".format(
                    name, category, sorted(ALLOWED_CATEGORIES)
                ),
                "index.json",
            )
        )

    description = entry.get("description")
    if not isinstance(description, str) or not description.strip():
        issues.append(
            Issue(
                "ERROR",
                "skill entry '{}' description must be non-empty".format(name),
                "index.json",
            )
        )

    path = entry.get("path")
    if path:
        abs_path = os.path.join(repo_root, path)
        if not os.path.isdir(abs_path):
            issues.append(
                Issue(
                    "ERROR",
                    "skill entry '{}' path '{}' does not exist".format(name, path),
                    rel_path(repo_root, abs_path),
                )
            )
        else:
            folder_name = os.path.basename(os.path.normpath(path))
            if isinstance(name, str) and folder_name != name:
                issues.append(
                    Issue(
                        "ERROR",
                        "folder name '{}' != index name '{}'".format(folder_name, name),
                        rel_path(repo_root, abs_path),
                    )
                )
    return issues


# --------------------------------------------------------------------------- #
# Skill folder validation
# --------------------------------------------------------------------------- #


def validate_skill(name, repo_root, skills_dir, index_entry):
    """Validate one skill folder. Returns a list of Issue."""
    issues = []
    skill_dir = os.path.join(skills_dir, name)
    skill_rel = rel_path(repo_root, skill_dir)

    if not os.path.isdir(skill_dir):
        issues.append(Issue("ERROR", "skill folder does not exist", skill_rel))
        return issues

    if not KEBAB_RE.match(name):
        issues.append(
            Issue("ERROR", "skill folder name '{}' is not kebab-case".format(name), skill_rel)
        )

    skill_json_path = os.path.join(skill_dir, "skill.json")
    skill_md_path = os.path.join(skill_dir, "SKILL.md")

    # --- skill.json ------------------------------------------------------- #
    if not os.path.isfile(skill_json_path):
        issues.append(
            Issue("ERROR", "missing skill.json", rel_path(repo_root, skill_json_path))
        )
        skill_json = None
    else:
        try:
            with open(skill_json_path, encoding="utf-8") as handle:
                skill_json = json.load(handle)
        except (OSError, ValueError) as exc:
            issues.append(
                Issue(
                    "ERROR",
                    "skill.json is not valid JSON: {}".format(exc),
                    rel_path(repo_root, skill_json_path),
                )
            )
            skill_json = None

    if isinstance(skill_json, dict):
        issues.extend(
            _validate_skill_json(name, skill_json, skill_dir, repo_root, index_entry)
        )

    # --- SKILL.md --------------------------------------------------------- #
    if not os.path.isfile(skill_md_path):
        issues.append(
            Issue("ERROR", "missing SKILL.md", rel_path(repo_root, skill_md_path))
        )
    else:
        issues.extend(_validate_skill_md(name, skill_md_path, skill_dir, repo_root, skill_json))

    # --- folder layout ---------------------------------------------------- #
    issues.extend(_validate_layout(name, skill_dir, repo_root))
    return issues


def _validate_skill_json(name, skill_json, skill_dir, repo_root, index_entry):
    issues = []
    rel = lambda p: rel_path(repo_root, os.path.join(skill_dir, p))

    for key in REQUIRED_SKILL_JSON_KEYS:
        if key not in skill_json:
            issues.append(
                Issue("ERROR", "skill.json missing required key: {}".format(key), rel("skill.json"))
            )

    version = skill_json.get("version")
    if isinstance(version, str) and not SEMVER_RE.match(version):
        issues.append(
            Issue("ERROR", "skill.json version '{}' is not semver".format(version), rel("skill.json"))
        )

    index_version = index_entry.get("version") if isinstance(index_entry, dict) else None
    if isinstance(version, str) and isinstance(index_version, str) and version != index_version:
        issues.append(
            Issue(
                "ERROR",
                "skill.json version '{}' != index.json version '{}'".format(version, index_version),
                rel("skill.json"),
            )
        )

    entrypoint = skill_json.get("entrypoint")
    if entrypoint != "SKILL.md":
        issues.append(
            Issue(
                "ERROR",
                "skill.json entrypoint must be 'SKILL.md', got '{}'".format(entrypoint),
                rel("skill.json"),
            )
        )

    category = skill_json.get("category")
    if category not in ALLOWED_CATEGORIES:
        issues.append(
            Issue(
                "ERROR",
                "skill.json category '{}' not in allowed set {}".format(
                    category, sorted(ALLOWED_CATEGORIES)
                ),
                rel("skill.json"),
            )
        )

    files = skill_json.get("files")
    if isinstance(files, list):
        for entry in files:
            if not isinstance(entry, str):
                issues.append(
                    Issue("ERROR", "skill.json files[] entry is not a string", rel("skill.json"))
                )
                continue
            if entry.startswith("/") or "../" in entry:
                issues.append(
                    Issue(
                        "ERROR",
                        "skill.json files[] entry '{}' must be a relative unix path".format(entry),
                        rel("skill.json"),
                    )
                )
                continue
            target = os.path.normpath(os.path.join(skill_dir, entry))
            if not os.path.exists(target):
                issues.append(
                    Issue("ERROR", "skill.json files[] missing: '{}'".format(entry), rel(entry))
                )
    return issues


def _validate_skill_md(name, skill_md_path, skill_dir, repo_root, skill_json):
    issues = []
    rel = lambda p: rel_path(repo_root, os.path.join(skill_dir, p))
    try:
        with open(skill_md_path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:
        issues.append(Issue("ERROR", "cannot read SKILL.md: {}".format(exc), rel("SKILL.md")))
        return issues

    data, body = parse_frontmatter(text)
    if data is None:
        issues.append(Issue("ERROR", "SKILL.md has no YAML frontmatter block", rel("SKILL.md")))
        return issues

    for key in ("name", "description", "license"):
        if not data.get(key):
            issues.append(
                Issue("ERROR", "SKILL.md frontmatter missing '{}'".format(key), rel("SKILL.md"))
            )

    md_version = data.get("metadata.version")
    if not md_version:
        issues.append(
            Issue("ERROR", "SKILL.md frontmatter missing 'metadata.version'", rel("SKILL.md"))
        )
    else:
        json_version = skill_json.get("version") if isinstance(skill_json, dict) else None
        if isinstance(json_version, str) and md_version != json_version:
            issues.append(
                Issue(
                    "ERROR",
                    "SKILL.md metadata.version '{}' != skill.json version '{}'".format(
                        md_version, json_version
                    ),
                    rel("SKILL.md"),
                )
            )

    # Progressive disclosure.
    line_count = text.count("\n") + (0 if text.endswith("\n") else 1)
    char_count = len(text)
    if line_count > ERROR_LINES:
        issues.append(
            Issue(
                "ERROR",
                "SKILL.md is {} lines (>{}); move details into references/".format(
                    line_count, ERROR_LINES
                ),
                rel("SKILL.md"),
            )
        )
    elif line_count > WARN_LINES or char_count > WARN_CHARS:
        issues.append(
            Issue(
                "WARNING",
                "SKILL.md is large ({} lines, {} chars); consider trimming".format(
                    line_count, char_count
                ),
                rel("SKILL.md"),
            )
        )

    issues.extend(_validate_references(name, body, skill_dir, repo_root))
    return issues


def _validate_references(name, body, skill_dir, repo_root):
    """Check local file references in SKILL.md body. Returns a list of Issue."""
    issues = []
    rel = lambda p: rel_path(repo_root, os.path.join(skill_dir, p))
    skill_names = set()

    # Strip fenced code blocks and inline code before scanning links: template
    # examples (e.g. `[English](README.md)` inside a code fence) are illustrative,
    # not real local references.
    scan = re.sub(r"```.*?```", " ", body, flags=re.DOTALL)
    scan = re.sub(r"`[^`\n]*`", " ", scan)

    # Markdown links: [text](target)
    for link in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", scan):
        target = link.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        path_part = target.split("#", 1)[0]
        if not path_part or path_part.startswith("/"):
            continue
        if any(ch not in PATH_CHARSET for ch in path_part):
            continue
        resolved = os.path.normpath(os.path.join(skill_dir, path_part))
        if not os.path.exists(resolved):
            issues.append(
                Issue(
                    "ERROR",
                    "SKILL.md references missing local file: '{}'".format(target),
                    rel(path_part),
                )
            )

    # Plain paths mentioning references/... or scripts/... (file references only).
    for plain in re.finditer(r"(?:references|scripts)/(?:[\w./-]+\.\w+)", scan):
        target = plain.group(0)
        if target.startswith("../") or "../" in target:
            continue
        first = target.split("/", 1)[0]
        if first in skill_names and first != name:
            continue
        resolved = os.path.normpath(os.path.join(skill_dir, target))
        if not os.path.exists(resolved):
            issues.append(
                Issue(
                    "ERROR",
                    "SKILL.md references missing local file: '{}'".format(target),
                    rel(target),
                )
            )
    return issues


def _validate_layout(name, skill_dir, repo_root):
    issues = []
    rel = lambda p: rel_path(repo_root, os.path.join(skill_dir, p))

    for entry in sorted(os.listdir(skill_dir)):
        entry_path = os.path.join(skill_dir, entry)
        if os.path.isdir(entry_path):
            if entry not in ALLOWED_SUBDIRS:
                issues.append(
                    Issue(
                        "WARNING",
                        "unexpected subdirectory '{}' (allowed: {})".format(
                            entry, sorted(ALLOWED_SUBDIRS)
                        ),
                        rel(entry),
                    )
                )
        else:
            if entry in IGNORED_TOPLEVEL_FILES:
                continue
            if entry not in ALLOWED_TOPLEVEL_FILES:
                issues.append(
                    Issue("WARNING", "unexpected top-level file: '{}'".format(entry), rel(entry))
                )
    return issues


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #


def collect_targets(args, repo_root, skills_dir, index):
    """Resolve the set of skill names to validate. Returns (names, system_error)."""
    if args.all:
        return [s["name"] for s in index.get("skills", []) if isinstance(s, dict)], False

    if args.files:
        names = []
        for raw in args.files:
            absolute = os.path.abspath(raw)
            matched = None
            for skill in index.get("skills", []):
                if not isinstance(skill, dict):
                    continue
                skill_name = skill.get("name")
                if not skill_name:
                    continue
                candidate = os.path.join(skills_dir, skill_name)
                if absolute == candidate or absolute.startswith(candidate + os.sep):
                    matched = skill_name
                    break
            if matched and matched not in names:
                names.append(matched)
        if not names:
            return [], True
        return names, False

    return [], True


def build_report(repo_root, skills_dir, index, names):
    """Run all checks and assemble the report structure."""
    per_skill = {}
    total_errors = 0
    total_warnings = 0

    index_issues = validate_index(index, repo_root, skills_dir)
    # Index-level issues are attributed to index.json itself.
    if index_issues:
        per_skill["__index__"] = {
            "status": "FAIL" if any(i.severity == "ERROR" for i in index_issues) else "PASS",
            "issues": [i.to_dict() for i in index_issues],
        }
        total_errors += sum(1 for i in index_issues if i.severity == "ERROR")
        total_warnings += sum(1 for i in index_issues if i.severity == "WARNING")

    index_by_name = {s["name"]: s for s in index.get("skills", []) if isinstance(s, dict)}

    for name in names:
        issues = validate_skill(name, repo_root, skills_dir, index_by_name.get(name, {}))
        has_error = any(i.severity == "ERROR" for i in issues)
        per_skill[name] = {
            "status": "FAIL" if has_error else "PASS",
            "issues": [i.to_dict() for i in issues],
        }
        total_errors += sum(1 for i in issues if i.severity == "ERROR")
        total_warnings += sum(1 for i in issues if i.severity == "WARNING")

    return {
        "total_skills": len(names),
        "errors": total_errors,
        "warnings": total_warnings,
        "per_skill": per_skill,
    }


def print_human(report, quiet):
    per_skill = report["per_skill"]
    for name in sorted(per_skill.keys()):
        info = per_skill[name]
        issues = info["issues"]
        errors = [i for i in issues if i["severity"] == "ERROR"]
        warnings = [i for i in issues if i["severity"] == "WARNING"]

        if name == "__index__":
            label = "index.json"
        else:
            label = name

        if info["status"] == "PASS":
            if not quiet:
                print("{}: PASS".format(label))
                if warnings:
                    for issue in warnings:
                        print("  [WARNING] {} ({})".format(issue["message"], issue["file"]))
            continue

        print("{}: FAIL".format(label))
        if errors:
            for issue in errors:
                print("  [ERROR] {} ({})".format(issue["message"], issue["file"]))
        if warnings and not quiet:
            for issue in warnings:
                print("  [WARNING] {} ({})".format(issue["message"], issue["file"]))

    print("")
    print("=== SUMMARY ===")
    print(
        "Total skills: {} | Errors: {} | Warnings: {}".format(
            report["total_skills"], report["errors"], report["warnings"]
        )
    )
    result = "PASS" if report["errors"] == 0 else "FAIL"
    exit_code = 0 if report["errors"] == 0 else 1
    print("Result: {} (exit {})".format(result, exit_code))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate agent-skills catalog and skill folders."
    )
    parser.add_argument(
        "--all", action="store_true", help="validate every skill listed in index.json"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        metavar="PATH",
        help="validate only the skill(s) containing the given path(s)",
    )
    parser.add_argument("--json", action="store_true", help="emit a machine-readable report")
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress PASS and warning output")
    args = parser.parse_args(argv)

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_dir = os.path.join(repo_root, "skills")
    index_path = os.path.join(repo_root, "index.json")

    if not os.path.isfile(index_path):
        sys.stderr.write("system error: index.json not found at {}\n".format(index_path))
        return 2
    try:
        with open(index_path, encoding="utf-8") as handle:
            index = json.load(handle)
    except (OSError, ValueError) as exc:
        sys.stderr.write("system error: cannot parse index.json: {}\n".format(exc))
        return 2

    names, system_error = collect_targets(args, repo_root, skills_dir, index)
    if system_error:
        sys.stderr.write(
            "system error: no skills matched (provide --all or valid --files paths)\n"
        )
        return 2

    report = build_report(repo_root, skills_dir, index, names)
    exit_code = 0 if report["errors"] == 0 else 1

    if args.json:
        output = dict(report)
        output["exit_code"] = exit_code
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print_human(report, args.quiet)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
