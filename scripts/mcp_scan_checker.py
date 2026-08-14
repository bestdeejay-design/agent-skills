#!/usr/bin/env python3
"""
MCP-Scan security checker for AI-skill directories.

Wraps Invariant Labs' snyk-agent-scan (MCP-Scan) to scan each
skills/<name>/ directory individually for prompt injection (W011),
malware (W012), hard-coded secrets, and other issues.

This is a compact adaptation of the developer-kit reference checker
(MIT licensed). It is pure Python 3 stdlib, single file, CI-friendly
(plain ASCII output, no color codes).

Usage:
    # Scan every skills/<name>/ directory
    python3 scripts/mcp_scan_checker.py --all

    # Scan only skill folders touched since a base ref
    python3 scripts/mcp_scan_checker.py --changed --base origin/main

    # Machine-readable report
    python3 scripts/mcp_scan_checker.py --all --json

Exit codes:
    0 = clean, or only allowlisted findings
    1 = new (non-allowlisted) findings detected
    2 = system error (scanner unavailable / execution failure)
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse

# Allowlist file lives in the repo ROOT (not in scripts/).
ALLOWLIST_FILENAME = "mcp-scan-allowlist.json"

# Regex to extract HTTP(S) URLs from text.
URL_RE = re.compile(r"https?://[^\s\"'<>)\]},\`]+")

# Domains that are always treated as placeholders and excluded from validation.
PLACEHOLDER_DOMAINS = frozenset({"localhost"})

# Warning codes that are informational (not real security issues).
# W004 = "The MCP server is not in our registry" — expected for custom skills.
INFORMATIONAL_CODES = frozenset({"W004"})

# Scanner invocation timeout per skill (seconds).
SCAN_TIMEOUT = 120


@dataclass
class ScanResult:
    """Result of scanning a single skill directory."""

    scan_path: str
    component_name: str
    issues: List[dict] = field(default_factory=list)
    error: Optional[dict] = None
    servers_found: int = 0
    allowed_codes: frozenset = field(default_factory=frozenset)
    allowed_domains: frozenset = field(default_factory=frozenset)
    placeholder_domains: frozenset = field(default_factory=frozenset)
    file_domains: frozenset = field(default_factory=frozenset)
    uncensored_domains: frozenset = field(default_factory=frozenset)

    def _is_informational(self, code: str) -> bool:
        if code in INFORMATIONAL_CODES:
            return True
        if code not in self.allowed_codes:
            return False
        # Code is allowed — but a new (uncensored) domain re-enables the finding.
        if self.uncensored_domains:
            return False
        return True

    @property
    def has_critical_issues(self) -> bool:
        return any(not self._is_informational(i.get("code", "")) for i in self.issues)

    @property
    def security_issues(self) -> List[dict]:
        return [i for i in self.issues if not self._is_informational(i.get("code", ""))]

    @property
    def info_issues(self) -> List[dict]:
        return [i for i in self.issues if self._is_informational(i.get("code", ""))]


def find_repo_root() -> Path:
    """Return the repository root via git, falling back to cwd."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def load_allowlist(repo_root: Path) -> Tuple[dict, dict, frozenset]:
    """Load the per-component allowlist from the repo root.

    Returns (code_allowlist, domain_allowlist, placeholder_domains):
      - code_allowlist:   component path -> set of allowed warning codes
      - domain_allowlist: component path -> set of allowed external domains
      - placeholder_domains: domains to ignore during domain census
    """
    allowlist_path = repo_root / ALLOWLIST_FILENAME
    if not allowlist_path.exists():
        return {}, {}, PLACEHOLDER_DOMAINS

    try:
        data = json.loads(allowlist_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}, {}, PLACEHOLDER_DOMAINS

    file_placeholders = frozenset(d.lower() for d in data.get("_placeholder_domains", []))
    placeholders = PLACEHOLDER_DOMAINS | file_placeholders

    codes: dict = {}
    domains: dict = {}
    for entry in data.get("components", []):
        path = entry.get("path", "").rstrip("/")
        if not path:
            continue
        allow_codes = entry.get("allow", [])
        if allow_codes:
            codes[path] = frozenset(allow_codes)
        domains[path] = frozenset(d.lower() for d in entry.get("domains", []))

    return codes, domains, placeholders


def extract_domains_from_files(skill_path: Path) -> frozenset:
    """Extract all unique domains from HTTP(S) URLs in a skill's files."""
    found: set = set()
    scan_dir = skill_path if skill_path.is_dir() else skill_path.parent
    for f in scan_dir.rglob("*"):
        if not f.is_file() or f.suffix not in (".md", ".txt", ".yaml", ".yml", ".json"):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for url_match in URL_RE.findall(text):
            url_clean = url_match.rstrip(".,;:")
            if "${" in url_clean:  # skip template variables
                continue
            try:
                hostname = urlparse(url_clean).hostname
                if hostname and len(hostname) > 1 and "." in hostname:
                    found.add(hostname.lower())
            except Exception:
                continue
    return frozenset(found)


def check_scanner_available() -> Tuple[bool, str]:
    """Check if snyk-agent-scan can run via uvx or pipx."""
    if shutil.which("uvx"):
        return True, "uvx"
    if shutil.which("pipx"):
        return True, "pipx"
    return False, ""


def find_skill_directories(repo_root: Path) -> List[Path]:
    """Find every skills/<name>/ directory (contains SKILL.md)."""
    skills_dir = repo_root / "skills"
    if not skills_dir.exists():
        return []
    dirs: List[Path] = []
    for skill_md in sorted(skills_dir.rglob("SKILL.md")):
        dirs.append(skill_md.parent)
    return dirs


def find_changed_skill_directories(repo_root: Path, base_ref: Optional[str]) -> List[Path]:
    """Map changed files (git diff) to their skills/<name>/ folder."""
    if base_ref is None:
        for candidate in ["origin/main", "origin/develop", "HEAD~1"]:
            try:
                result = subprocess.run(
                    ["git", "merge-base", "HEAD", candidate],
                    capture_output=True, text=True, check=True, cwd=repo_root,
                )
                base_ref = result.stdout.strip()
                break
            except subprocess.CalledProcessError:
                continue
        if base_ref is None:
            base_ref = "HEAD~1"

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
            capture_output=True, text=True, check=True, cwd=repo_root,
        )
    except subprocess.CalledProcessError:
        print(f"Error: git diff failed against {base_ref}")
        return []

    skill_dirs: set = set()
    for changed in result.stdout.strip().splitlines():
        parts = Path(changed).parts
        # A skill folder is skills/<name> (the directory holding SKILL.md).
        if len(parts) >= 2 and parts[0] == "skills":
            candidate = repo_root / "skills" / parts[1]
            if (candidate / "SKILL.md").exists():
                skill_dirs.add(candidate)

    return sorted(skill_dirs)


def _parse_json_output(stdout: str, stderr: str) -> Optional[dict]:
    """Try to parse JSON from stdout, then stderr; return None if unparseable."""
    candidates = [stdout.strip(), stderr.strip()]
    for blob in candidates:
        if not blob:
            continue
        try:
            return json.loads(blob)
        except json.JSONDecodeError:
            # Try to locate a JSON object embedded in surrounding text.
            start = blob.find("{")
            end = blob.rfind("}")
            if start != -1 and end > start:
                try:
                    return json.loads(blob[start : end + 1])
                except json.JSONDecodeError:
                    continue
    return None


def scan_single_component(scan_path: Path, runner: str, verbose: bool = False) -> ScanResult:
    """Run snyk-agent-scan on a single skill directory."""
    result = ScanResult(scan_path=str(scan_path), component_name=scan_path.name)

    if runner == "uvx":
        cmd = ["uvx", "snyk-agent-scan@latest", "scan", "--json", "--skills", str(scan_path)]
    elif runner == "pipx":
        cmd = ["pipx", "run", "snyk-agent-scan@latest", "scan", "--json", "--skills", str(scan_path)]
    else:
        result.error = {"message": f"Unsupported runner: {runner}"}
        return result

    if verbose:
        print(f"  $ {' '.join(cmd)}")

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=SCAN_TIMEOUT)
        parsed = _parse_json_output(proc.stdout, proc.stderr)

        if parsed is None:
            raw = (proc.stdout or proc.stderr).strip()
            if raw:
                result.issues.append({
                    "code": "UNPARSED",
                    "message": "Scanner output could not be parsed as JSON",
                    "raw": raw[:500],
                })
            elif proc.returncode != 0:
                result.error = {"message": f"Scanner exited with code {proc.returncode}"}
            return result

        # snyk-agent-scan returns: { "<config_path>": { issues, labels, error, servers } }
        for _key, config_data in parsed.items():
            if not isinstance(config_data, dict):
                continue
            issues = config_data.get("issues", [])
            if issues:
                result.issues.extend(issues)
            error = config_data.get("error")
            if isinstance(error, dict) and error.get("message"):
                result.error = error
            servers = config_data.get("servers", [])
            result.servers_found += len(servers)
            for srv in servers:
                srv_error = srv.get("error")
                if isinstance(srv_error, dict) and srv_error.get("message"):
                    result.error = srv_error

    except FileNotFoundError:
        result.error = {"message": f"{runner} command not found"}
    except subprocess.TimeoutExpired:
        result.error = {"message": f"Scan timed out after {SCAN_TIMEOUT} seconds"}
    except Exception as e:  # noqa: BLE001 - surface any unexpected failure
        result.error = {"message": str(e)}

    return result


def print_scan_result(result: ScanResult, verbose: bool = False) -> None:
    """Print the result for a single skill scan (plain ASCII)."""
    security_issues = result.security_issues
    info_issues = result.info_issues

    if result.error:
        err_msg = result.error.get("message", "Unknown error")
        category = result.error.get("category", "")
        if category == "file_not_found":
            print(f"  SKIP  - {err_msg}")
        else:
            print(f"  ERROR - {err_msg}")
    elif security_issues:
        for issue in security_issues:
            code = issue.get("code", "???")
            msg = issue.get("message", "No description")
            print(f"  FAIL  [{code}] {msg}")
        if result.uncensored_domains:
            domains_str = ", ".join(sorted(result.uncensored_domains))
            print(f"         Uncensored domain(s): {domains_str}")
            print(f"         Add to {ALLOWLIST_FILENAME} to suppress")
    elif info_issues and verbose:
        for issue in info_issues:
            code = issue.get("code", "???")
            msg = issue.get("message", "No description")
            suffix = " (allowed)" if code in result.allowed_codes else ""
            print(f"  INFO  [{code}] {msg}{suffix}")
    else:
        print("  PASS")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="mcp-scan-checker",
        description="Security scan skills/<name>/ directories using snyk-agent-scan (Invariant Labs)",
    )
    parser.add_argument("--all", action="store_true", help="Scan every skills/<name>/ directory")
    parser.add_argument(
        "--changed", action="store_true",
        help="Scan only skill folders touched by git diff (use with --base)",
    )
    parser.add_argument(
        "--base", type=str, default=None,
        help="Base ref for --changed comparison (default: auto-detect merge-base)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable JSON report")

    args = parser.parse_args()

    if not args.all and not args.changed:
        parser.print_help()
        return 0

    print("MCP-Scan Security Checker for AI-skill directories")
    print("=" * 60)

    available, runner = check_scanner_available()
    if not available:
        msg = (
            "Error: Neither 'uvx' nor 'pipx' is available, so snyk-agent-scan "
            "cannot run. Install uv (https://astral.sh/uv) or pipx "
            "(pip install pipx) and ensure it is on PATH."
        )
        print(msg)
        if args.json:
            print(json.dumps({"exit_code": 2, "error": "scanner_unavailable", "results": []}))
        return 2

    print(f"Using runner: {runner}")

    repo_root = find_repo_root()
    print(f"Repository: {repo_root}")

    code_allowlist, domain_allowlist, placeholder_domains = load_allowlist(repo_root)

    if args.changed:
        skill_dirs = find_changed_skill_directories(repo_root, args.base)
        if not skill_dirs:
            print("No skill changes detected - nothing to scan.")
            if args.json:
                print(json.dumps({"exit_code": 0, "results": []}))
            return 0
    else:
        skill_dirs = find_skill_directories(repo_root)

    if not skill_dirs:
        print("No skills/ directories found to scan.")
        if args.json:
            print(json.dumps({"exit_code": 0, "results": []}))
        return 0

    print(f"Found {len(skill_dirs)} skill(s) to scan\n")

    results: List[ScanResult] = []
    passed = failed = errors = skipped = 0

    for i, skill_dir in enumerate(skill_dirs, 1):
        rel_path = skill_dir.relative_to(repo_root) if skill_dir.is_relative_to(repo_root) else skill_dir
        rel_str = str(rel_path).replace("\\", "/").rstrip("/")
        print(f"[{i}/{len(skill_dirs)}] {skill_dir.name} ({rel_path})")

        scan_result = scan_single_component(skill_dir, runner, args.verbose)

        # Apply per-component allowlist with domain census.
        if rel_str in code_allowlist:
            scan_result.allowed_codes = code_allowlist[rel_str]
            scan_result.allowed_domains = domain_allowlist.get(rel_str, frozenset())
            scan_result.placeholder_domains = placeholder_domains

            file_domains = extract_domains_from_files(skill_dir)
            real_domains = frozenset(
                d for d in file_domains
                if d not in placeholder_domains
                and not any(d.endswith("." + p) for p in placeholder_domains)
            )
            scan_result.file_domains = real_domains
            scan_result.uncensored_domains = real_domains - scan_result.allowed_domains

        results.append(scan_result)
        print_scan_result(scan_result, args.verbose)

        if scan_result.error:
            if scan_result.error.get("category") == "file_not_found":
                skipped += 1
            else:
                errors += 1
        elif scan_result.has_critical_issues:
            failed += 1
        else:
            passed += 1

    print("\n" + "-" * 60)
    parts = []
    if passed:
        parts.append(f"{passed} passed")
    if failed:
        parts.append(f"{failed} failed")
    if errors:
        parts.append(f"{errors} error(s)")
    if skipped:
        parts.append(f"{skipped} skipped")
    print(f"Results: {', '.join(parts)} ({len(results)} total)")

    if args.json:
        report = {
            "exit_code": 1 if failed else 0,
            "summary": {"passed": passed, "failed": failed, "errors": errors, "skipped": skipped},
            "results": [
                {
                    "component": r.component_name,
                    "path": r.scan_path,
                    "status": (
                        "error" if r.error else ("fail" if r.has_critical_issues else "pass")
                    ),
                    "error": r.error.get("message") if r.error else None,
                    "issues": r.security_issues,
                }
                for r in results
            ],
        }
        print(json.dumps(report, indent=2))

    if failed:
        print(f"\nSecurity scan FAILED: {failed} skill(s) with security issues.")
        return 1

    print("\nSecurity scan passed: all scanned skills are clean (or allowlisted).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
