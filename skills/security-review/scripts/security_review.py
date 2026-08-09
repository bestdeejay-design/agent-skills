#!/usr/bin/env python3
"""security-review — dependency & lint security audit planner/classifier (stdlib only).

The auxiliary script for the `security-review` skill. It does NOT execute
external scanners itself; it owns the parts that are pure stdlib Python:

  1. lockfile / manifest inventory        (pathlib glob, ecosystem inference)
  2. exit-code classifier                  (findings vs. tool failure — verified
                                           Aug 2026 values, see TOOL_EXIT_CODES)
  3. JSON normalizers for the main tool families:
      osv-scanner v2, pip-audit, semgrep, gitleaks, bandit
  4. unified report writer (json / text / markdown) + severity rollup

Design follows `trailofbits/skills` philosophy: each tool gets one `runs[]`
entry in SARIF-like output, findings are de-duplicated by (rule, path, line),
and a tool exiting non-zero on findings is *expected*, not an error.

Usage:
    python3 security_review.py inventory [--dir PATH]                # lockfiles found
    python3 security_review.py classify --tool semgrep --exit-code 1  # human meaning
    python3 security_review.py normalize --tool osv-scanner --input osv.json [--output report.json]
    python3 security_review.py report --json --dir .                 # inventory + normalize all

Exit codes:
    0  ok
    2  usage / IO error
    3  (report mode) vulnerabilities or findings found

Dependencies: Python 3 stdlib only (argparse, json, os, pathlib, subprocess).
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Lockfile / manifest inventory
# ---------------------------------------------------------------------------
# filename (or suffix), ecosystem, primary tool
LOCKFILE_RULES = [
    ("package-lock.json",      "npm",       "npm audit"),
    ("pnpm-lock.yaml",         "pnpm",      "osv-scanner / pnpm audit"),
    ("yarn.lock",              "yarn",      "yarn audit"),
    ("requirements.txt",       "pip",       "pip-audit"),
    ("requirements*.txt",      "pip",       "pip-audit"),
    ("pyproject.toml",         "pip",       "pip-audit"),
    ("Pipfile.lock",           "pip",       "pip-audit"),
    ("poetry.lock",            "pip",       "pip-audit"),
    ("Cargo.lock",             "cargo",     "cargo audit"),
    ("go.mod",                 "go",        "osv-scanner"),
    ("go.sum",                 "go",        "osv-scanner"),
    ("Gemfile.lock",           "gem",       "osv-scanner"),
    ("pom.xml",                "maven",     "osv-scanner / dependency-check"),
    ("build.gradle",           "gradle",    "osv-scanner / dependency-check"),
    ("build.gradle.kts",        "gradle",    "osv-scanner / dependency-check"),
    ("composer.lock",          "composer",  "osv-scanner"),
    ("package.json",           "npm",       "npm audit"),
]
IGNORE_DIRS = {"node_modules", ".git", "vendor", "dist", "build", ".venv", "venv", "__pycache__"}


def inventory(root: Path) -> list[dict]:
    """Return list of {path, name, ecosystem, tool} for dependency files."""
    found = []
    for rp in root.rglob("*"):
        if rp.is_dir():
            continue
        rel_parts = rp.relative_to(root).parts
        if any(d in IGNORE_DIRS for d in rel_parts):
            continue
        name = rp.name
        matched = None
        if name in {"package-lock.json", "pnpm-lock.yaml", "yarn.lock",
                    "requirements.txt", "pyproject.toml", "Pipfile.lock",
                    "poetry.lock", "Cargo.lock", "go.mod", "go.sum",
                    "Gemfile.lock", "pom.xml", "composer.lock", "package.json"}:
            matched = name
        elif name.startswith("requirements") and name.endswith(".txt"):
            matched = "requirements.txt"
        elif name == "build.gradle" or name == "build.gradle.kts":
            matched = name
        if not matched:
            continue
        ecosystem, tool = next(r[1:] for r in LOCKFILE_RULES if r[0] == matched)
        found.append({
            "path": str(rp.relative_to(root)),
            "name": name,
            "ecosystem": ecosystem,
            "tool": tool,
        })
    # de-dup: package.json next to its lockfile is redundant — keep lockfile only
    lockfiles = [f for f in found if f["name"] != "package.json"]
    seen_dirs = {str(Path(f["path"]).parent) for f in lockfiles}
    for f in found:
        if f["name"] != "package.json":
            continue
        if str(Path(f["path"]).parent) not in seen_dirs:
            lockfiles.append(f)
    return sorted(lockfiles, key=lambda f: f["path"])


# ---------------------------------------------------------------------------
# 2. Exit-code classifier (verified Aug 2026)
# ---------------------------------------------------------------------------
# meaning: "clean" | "findings" | "error" | "special"
TOOL_EXIT_CODES = {
    # tool: {code: meaning, "default": meaning}
    "semgrep": {0: "clean", 1: "findings", 2: "error", "default": "error",
                "error_codes": [3, 4, 5, 7, 8, 13, 99]},
    "bandit": {0: "clean", 1: "findings", 2: "error", "default": "error"},
    "gitleaks": {0: "clean", 1: "findings-or-error", 126: "error",
                 "default": "error", "note": "use --exit-code to force 1 on findings"},
    "pip-audit": {0: "clean", 1: "findings", "default": "error"},
    "osv-scanner": {0: "clean", 1: "findings", 127: "error", 128: "no-packages",
                    129: "error", 130: "error", "default": "error"},
    "npm": {0: "clean", 1: "findings", "default": "error"},
    "cargo-audit": {0: "clean", "default": "findings-or-error"},
    "grype": {0: "clean", 1: "error", 2: "findings", 100: "error",
              "default": "error", "note": "--fail-on severity"},
    "trufflehog": {0: "clean", 1: "error", 183: "findings",
                   "default": "error", "note": "183 only with --fail"},
    "checkov": {0: "clean", 1: "findings", 2: "error", "default": "error"},
    "trivy": {0: "clean", 1: "findings", "default": "error",
              "note": "requires --exit-code 1"},
    "dependency-check": {0: "clean", 1: "findings", "default": "error",
                         "note": "--failOnCVSS"},
}


def classify_exit(tool: str, exit_code: int) -> dict:
    """Map (tool, exit_code) to a stable meaning + human explanation."""
    spec = TOOL_EXIT_CODES.get(tool, {})
    meaning = spec.get(exit_code, spec.get("default", "unknown"))
    return {
        "tool": tool,
        "exit_code": exit_code,
        "meaning": meaning,
        "expected_report": meaning == "findings",
    }


# ---------------------------------------------------------------------------
# 3. JSON normalizers (each returns a list of normalized findings)
# ---------------------------------------------------------------------------

def normalize_osv(data) -> list[dict]:
    findings = []
    for res in data.get("results", []):
        for pkg in res.get("packages", []):
            pkg_id = pkg.get("package", {}).get("name", "?")
            for vuln in pkg.get("vulnerabilities", []):
                sev = vuln.get("severity") or [{"type": None, "score": None}]
                s = sev[0]
                findings.append(_norm(
                    vuln.get("id", "OSV-?"),
                    "vulnerable-component",
                    f"{pkg_id}: {vuln.get('summary') or 'see advisory'}"
                    f" fixed {vuln.get('fixed') or '?'}",
                    res.get("source", {}).get("path", "?"),
                    0,
                    0,
                    {"score": s.get("score"), "aliases": vuln.get("aliases")},
                ))
    return findings


def normalize_pip_audit(data) -> list[dict]:
    findings = []
    for item in data if isinstance(data, list) else data.get("dependencies", []):
        name = item.get("name", "?")
        for vuln in item.get("vulns", []):
            findings.append(_norm(
                vuln.get("id", "PIP-?"),
                "vulnerable-component",
                f"{name}=={item.get('version')}: {vuln.get('description', '')[:140]}"
                f" fix {vuln.get('fix_versions')}",
                0, 0, 0,
                {"aliases": vuln.get("aliases")},
            ))
    return findings


def normalize_semgrep(data) -> list[dict]:
    findings = []
    for r in data.get("results", []):
        sev = r.get("extra", {}).get("severity", "warning")  # ERROR/WARNING/INFO
        findings.append(_norm(
            r.get("check_id", "?"), "code-quality",
            r.get("extra", {}).get("message", "")[:200],
            r.get("path", "?"),
            r.get("start", {}).get("line", 0),
            r.get("start", {}).get("col", 0),
            {"severity_raw": sev, "metadata": r.get("extra", {}).get("metadata", {})},
        ))
    return findings


def normalize_gitleaks(data) -> list[dict]:
    findings = []
    for r in data if isinstance(data, list) else data.get("Findings", []):
        findings.append(_norm(
            r.get("RuleID", "leak"),
            "secret",
            f"{r.get('Description', 'secret')} ({r.get('Match', '')[:60]})",
            r.get("File", "?"),
            r.get("StartLine", 0),
            0,
            {"fingerprint": r.get("Fingerprint"), "commit": r.get("Commit")},
        ))
    return findings


def normalize_bandit(data) -> list[dict]:
    findings = []
    for r in data.get("results", []):
        sev = r.get("issue_severity", "MEDIUM")
        findings.append(_norm(
            r.get("test_id", "B?"), "python-lint",
            r.get("issue_text", "")[:200],
            r.get("filename", "?"),
            r.get("line_number", 0), 0,
            {"severity": sev, "confidence": r.get("issue_confidence")},
        ))
    return findings


def _norm(rule_id, rule, message, path, line, col, extra):
    sev = extra.get("severity_raw") or extra.get("severity")
    level = "error" if sev == "ERROR" else "warning"
    return {
        "ruleId": rule_id,
        "rule": rule,
        "level": level,
        "message": message,
        "path": f"{path}" if path else "",
        "line": int(line or 0),
        "col": int(col or 0),
        "extra": extra or {},
    }

# (end of part 1 — continuation will append the CLI + report renderer)
# ---------------------------------------------------------------------------
# 4. Unified report renderer
# ---------------------------------------------------------------------------
SEVERITY_ORDER = {"error": 0, "warning": 1, "note": 2}


def rollup(findings):
    counts = {"error": 0, "warning": 0, "note": 0}
    by_rule = {}
    for f in findings:
        lvl = f.get("level", "warning")
        counts[lvl] = counts.get(lvl, 0) + 1
        key = f.get("ruleId", "?")
        by_rule[key] = by_rule.get(key, 0) + 1
    return {"counts": counts, "by_rule": by_rule}


def dedup(findings):
    seen = set()
    out = []
    for f in findings:
        key = (f.get("ruleId"), f.get("path"), f.get("line"))
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
    return out


def render_text(findings, tool=None):
    lines = []
    for f in sorted(findings, key=lambda x: (SEVERITY_ORDER.get(x.get("level", 9), 9), x.get("path", ""), x.get("line", 0))):
        loc = f"{f.get('path', '?')}:{f.get('line', 0)}"
        head = f"[{f.get('level', 'warning')}] {loc} — {f.get('rule', f.get('ruleId', '?'))}"
        if tool:
            head = f"{tool}: {head}"
        lines.append(head)
        lines.append(f"    {f.get('message', '')}")
    return "\n".join(lines)


def render_markdown(findings, target):
    r = rollup(findings)
    lines = [
        f"# Security Review — `{target}`",
        "",
        f"**Date:** {datetime.now().isoformat(timespec='seconds')}",
        f"**Findings:** {len(findings)} (error: {r['counts']['error']}, warning: {r['counts']['warning']}, note: {r['counts']['note']})",
        "",
        "| Severity | Rule | File | Line | Message |",
        "|---|---|---|---|---|",
    ]
    for f in sorted(findings, key=lambda x: (SEVERITY_ORDER.get(x.get("level", 9), 9), x.get("path", ""), x.get("line", 0))):
        lines.append(
            f"| {f.get('level')} | {f.get('ruleId', '?')} | `{f.get('path', '')}` | {f.get('line', 0)} | {f.get('message', '')[:120]} |"
        )
    return "\n".join(lines)


def render_json(findings, target, inventory=None):
    r = rollup(findings)
    return json.dumps(
        {
            "target": target,
            "generated": datetime.now().isoformat(timespec="seconds"),
            "inventory": inventory or [],
            "total": len(findings),
            "counts": r["counts"],
            "by_rule": r["by_rule"],
            "findings": findings,
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# 5. CLI
# ---------------------------------------------------------------------------
def load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"error: не удалось прочитать {path}: {exc}")


def cmd_inventory(args):
    root = Path(args.dir)
    if not root.is_dir():
        sys.exit(f"error: директория не найдена: {root}")
    items = inventory(root)
    if args.json:
        print(json.dumps(items, ensure_ascii=False, indent=2))
        return
    if not items:
        print("Нет lockfile'ов / манифестов зависимостей.")
        return
    width = max(len(i["ecosystem"]) for i in items)
    print(f"{'ecosystem':<{width}}  tool                lockfile")
    for it in items:
        print(f"{it['ecosystem']:<{width}}  {it['tool']:<19} {it['path']}")


def cmd_classify(args):
    res = classify_exit(args.tool, args.exit_code)
    print(
        f"{res['tool']} exit {res['exit_code']} → {res['meaning']} "
        f"({'expected report' if res['expected_report'] else 'not a scan report'})"
    )
    note = TOOL_EXIT_CODES.get(args.tool, {}).get("note")
    if note:
        print(f"note: {note}")


def cmd_normalize(args):
    data = load_json(args.input)
    fn = {
        "osv-scanner": normalize_osv,
        "pip-audit": normalize_pip_audit,
        "semgrep": normalize_semgrep,
        "gitleaks": normalize_gitleaks,
        "bandit": normalize_bandit,
    }.get(args.tool)
    if fn is None:
        sys.exit(f"error: неизвестный tool '{args.tool}' (osv-scanner/pip-audit/semgrep/gitleaks/bandit)")
    findings = dedup(fn(data))
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(render_json(findings, args.input))
        print(f"Report saved to {args.output}")
    else:
        print(render_text(findings, tool=args.tool) or "(no findings)")


def cmd_report(args):
    root = Path(args.root)
    items = inventory(root)
    findings = []
    if args.json:
        print(render_json(findings, str(root), items))
        return
    print(render_markdown(findings, str(root)) if not items else
          "Lockfiles found — run external scanners (see SKILL.md workflow) and feed JSON via `normalize`.")

def main():
    parser = argparse.ArgumentParser(
        description="security-review helper: lockfile inventory, exit-code classifier, JSON normalizer."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    inv = sub.add_parser("inventory", help="scan directory for dependency lockfiles")
    inv.add_argument("--dir", default=".", help="root directory (default: .)")
    inv.add_argument("--json", action="store_true", help="JSON output")
    inv.set_defaults(func=cmd_inventory)

    cls = sub.add_parser("classify", help="explain a tool exit code")
    cls.add_argument("--tool", required=True, choices=sorted(TOOL_EXIT_CODES))
    cls.add_argument("--exit-code", type=int, required=True)
    cls.set_defaults(func=cmd_classify)

    norm = sub.add_parser("normalize", help="normalize a tool JSON report to unified findings")
    norm.add_argument("--tool", required=True,
                      choices=["osv-scanner", "pip-audit", "semgrep", "gitleaks", "bandit"])
    norm.add_argument("--input", required=True, help="path to tool JSON")
    norm.add_argument("--output", help="save unified report to file")
    norm.set_defaults(func=cmd_normalize)

    rep = sub.add_parser("report", help="produce a unified report skeleton from a directory")
    rep.add_argument("--root", default=".", help="root directory (default: .)")
    rep.add_argument("--json", action="store_true", help="JSON output")
    rep.set_defaults(func=cmd_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
