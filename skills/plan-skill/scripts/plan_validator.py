#!/usr/bin/env python3
"""Validate an implementation plan Markdown file (superpowers-style).

Checks the plan is execution-ready:
  1. Has Goal, Constraints, Steps, Verification sections.
  2. Contains no placeholder markers (TBD, TODO, "...", "решим потом").
  3. Each "Step N" subsection has a Files record with a concrete file path.
  4. Steps are bite-sized (no huge step bodies).
  5. Acceptance criteria are checkable (no subjective phrasing).

Returns exit code 0 when the plan is ready, 1 otherwise (with a list of issues).

Usage:
    python3 plan_validator.py <plan.md> [--verbose]
"""
import re
import sys

PLACEHOLDER_PATTERNS = [
    r"\bTBD\b",
    r"\bTODO\b",
    r"\bFIXME\b",
    r"\.\.\.\s*$",
    r"решим потом",
    r"доделать позже",
    r"в процессе",
    r"XXX",
]

SUBJECTIVE_PATTERNS = [
    r"хорошо[ея]\b",
    r"красив[оы]",
    r"правильно\b",
    r"оптимальн[оы]",
]

REQUIRED_SECTIONS = ["goal", "constraints", "steps", "verification"]
MAX_STEP_LINES = 8


def _heading_level(line: str) -> int:
    m = re.match(r"^(#{1,6})\s+", line.strip())
    return len(m.group(1)) if m else 0


def _split_sections(lines: list[str]) -> dict[str, list[int]]:
    headings: list[tuple[int, int, str]] = []
    for i, line in enumerate(lines):
        lvl = _heading_level(line)
        if lvl:
            headings.append((i, lvl, line.strip().lstrip("#").strip().lower()))

    sections: dict[str, list[int]] = {}
    for idx, (start, level, title) in enumerate(headings):
        end = start
        for nxt in headings[idx + 1 :]:
            if nxt[1] <= level:
                end = nxt[0]
                break
        else:
            end = len(lines)
        sections.setdefault(title, []).extend(range(start + 1, end))
    return sections


def find_issues(lines: list[str], verbose: bool) -> list[str]:
    issues: list[str] = []
    sections = _split_sections(lines)

    for req in REQUIRED_SECTIONS:
        if not any(req in header for header in sections):
            issues.append(f"Missing section: '{req}'")

    for lineno, line in enumerate(lines, 1):
        for pattern in PLACEHOLDER_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(f"Placeholder at line {lineno}: '{line.strip()[:60]}'")

    for lineno, line in enumerate(lines, 1):
        for pattern in SUBJECTIVE_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE) and "acceptance" not in line.lower():
                issues.append(f"Subjective wording at line {lineno}: '{line.strip()[:60]}'")

    step_headers = [h for h in sections if re.match(r"step\s*\d+", h)]
    if not step_headers:
        issues.append("No 'Step N' subsection found in Steps")

    for header in step_headers:
        body = [lines[i] for i in sections[header]]
        files_cell = next((l for l in body if l.strip().startswith("- Files:")), None)
        if files_cell is None:
            issues.append(f"{header}: missing 'Files:' record")
        elif not re.search(r"[A-Za-z0-9_\-./]+\.[A-Za-z0-9]+", files_cell):
            issues.append(f"{header}: 'Files:' record has no concrete file path")
        real = [l for l in body if l.strip() and not re.match(r"^\s*[-*]\s+\[[ xX]\]", l)]
        if len(real) > MAX_STEP_LINES:
            issues.append(f"{header}: step body too large ({len(real)} lines, max {MAX_STEP_LINES})")

    if verbose:
        print(f"[debug] {len(lines)} lines, sections={sorted(sections)}")
    return issues


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    verbose = "--verbose" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(2)

    path = args[0]
    try:
        with open(path, encoding="utf-8") as f:
            lines = [l.rstrip("\n") for l in f]
    except OSError as e:
        print(f"❌ Cannot read {path}: {e}")
        sys.exit(1)

    issues = find_issues(lines, verbose)
    if issues:
        print(f"❌ Plan {path} is NOT execution-ready ({len(issues)} issue(s)):")
        for i in issues:
            print(f"   - {i}")
        sys.exit(1)

    print(f"✅ Plan {path} is execution-ready")


if __name__ == "__main__":
    main()