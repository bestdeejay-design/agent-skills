#!/usr/bin/env python3
"""
Local security checker for AI-skill directories.

Performs static, offline security analysis of each skills/<name>/
directory: hard-coded secrets (private keys, API tokens), prompt
injection patterns, and dangerous shell-command constructs. External
URLs are checked against a per-component domain allowlist
(mcp-scan-allowlist.json). No network access, no external scanner,
no third-party dependencies -- pure Python 3 stdlib.

Designed as a drop-in local replacement for the snyk-agent-scan
(MCP-Scan) based checker: same CLI, same exit codes, same allowlist
file, so existing CI invocations keep working without SNYK_TOKEN.

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
    2 = system error (analysis failure)
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple, Union
from urllib.parse import urlparse

# Allowlist file lives in the repo ROOT (not in scripts/).
ALLOWLIST_FILENAME = "mcp-scan-allowlist.json"

# Regex to extract HTTP(S) URLs from text.
URL_RE = re.compile(r"https?://[^\s\"'<>)\]},\`]+")

# Domains that are always treated as placeholders and excluded from validation.
PLACEHOLDER_DOMAINS = frozenset({"localhost"})

# Issue codes that are informational (not real security issues).
INFORMATIONAL_CODES = frozenset()

# ---------------------------------------------------------------------------
# Secret patterns. Each entry: (compiled regex, code, label).
# Matcher extraction is line-based; placeholder-guard (_is_placeholder)
# filters out documentation examples (…, ..., EXAMPLE, XXX, <...>, ${...}).
# ---------------------------------------------------------------------------

# Full PEM private keys (RSA/EC/OPENSSH/DSA/PGP/ENCRYPTED). A real key block
# is long and free of ellipses / placeholder markers.
_PRIVATE_KEY_HEADER = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP |ENCRYPTED |)PRIVATE KEY-----"
)

# Well-known high-entropy token formats.
_TOKEN_PATTERNS = [
    (re.compile(r"\bghp_[A-Za-z0-9]{36}\b"), "SECRET", "GitHub personal access token"),
    (re.compile(r"\bgho_[A-Za-z0-9]{36}\b"), "SECRET", "GitHub OAuth token"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b"), "SECRET", "GitHub fine-grained token"),
    (re.compile(r"\bglpat-[A-Za-z0-9_\-]{20,}\b"), "SECRET", "GitLab personal access token"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}\b"), "SECRET", "Slack token"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "SECRET", "AWS access key ID"),
    (re.compile(r"\bASIA[0-9A-Z]{16}\b"), "SECRET", "AWS temporary access key ID"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}\b"), "SECRET", "Google API key"),
    (
        re.compile(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+"),
        "SECRET",
        "JWT token",
    ),
    (re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b"), "SECRET", "API key (sk- prefix)"),
]

# Sensitive key-value assignments, e.g. `api_key = "..."`, `TOKEN: "..."`.
# The value must be a quoted literal of sufficient length and must not look
# like a documentation placeholder.
_ASSIGN_PATTERN = re.compile(
    r"\b(?:api[_-]?key|apikey|password|passwd|secret|token|"
    r"access[_-]?key|auth[_-]?token|private[_-]?key)\b"
    r"\s*[=:]\s*[\"']([^\"'\s]{12,})[\"']",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Prompt injection patterns.
# ---------------------------------------------------------------------------
_INJECTION_PATTERNS = [
    (
        re.compile(
            r"\bignore (?:all |any |every )?(?:previous|prior|above|earlier) "
            r"(?:instructions|directives|prompts?|messages|commands)\b",
            re.IGNORECASE,
        ),
        "INJECT",
        "prompt injection: instruction to ignore earlier instructions",
    ),
    (
        re.compile(
            r"\bignore (?:the )?(?:system|developer|original) (?:prompt|instructions)\b",
            re.IGNORECASE,
        ),
        "INJECT",
        "prompt injection: instruction to ignore the system prompt",
    ),
    (
        re.compile(
            r"\b(?:disregard|forget) (?:all )?(?:previous|prior) (?:instructions|directives)\b",
            re.IGNORECASE,
        ),
        "INJECT",
        "prompt injection: instruction to disregard earlier directives",
    ),
    (
        re.compile(
            r"\breveal (?:your |the )(?:system |internal |full |original )?prompt\b",
            re.IGNORECASE,
        ),
        "INJECT",
        "prompt injection: request to leak the system prompt",
    ),
    (
        re.compile(
            r"\b(?:override|bypass) (?:the |your |any )?(?:system|safety|security|original) "
            r"(?:prompt|policy|rules|instructions)\b",
            re.IGNORECASE,
        ),
        "INJECT",
        "prompt injection: attempt to override safety policy",
    ),
]

# ---------------------------------------------------------------------------
# Dangerous command constructs (remote code / shell piping / decoding).
# ---------------------------------------------------------------------------
_DANGEROUS_COMMANDS = [
    (
        re.compile(r"\bcurl\s+[^;\n|]*\|\s*(?:sudo\s+)?(?:ba|z)sh\b", re.IGNORECASE),
        "EXEC",
        "download-and-execute: curl piped to shell",
    ),
    (
        re.compile(r"\bwget\s+[^;\n|]*\|\s*(?:sudo\s+)?(?:ba|z)sh\b", re.IGNORECASE),
        "EXEC",
        "download-and-execute: wget piped to shell",
    ),
    (
        re.compile(r"\b(?:ba|z)sh\s*<\s*<\(\s*(?:curl|wget)\b", re.IGNORECASE),
        "EXEC",
        "download-and-execute: process substitution of remote fetch",
    ),
    (
        re.compile(r"\bcurl\s+[^;\n|]*\|\s*(?:sudo\s+)?sh\b", re.IGNORECASE),
        "EXEC",
        "download-and-execute: curl piped to sh",
    ),
    (
        re.compile(r"\bIEX\s*\(\s*(?:New-Object|Invoke-WebRequest|curl|wget)", re.IGNORECASE),
        "EXEC",
        "PowerShell download-and-execute",
    ),
    (
        re.compile(r"\b(?:eval|exec)\s*\(\s*(?:\"[^\"]*\"|'[^']*')\s*\)", re.IGNORECASE),
        "EXEC",
        "dynamic code evaluation with a literal payload",
    ),
]

# Placeholder markers that indicate a documentation example, not a real secret.
_PLACEHOLDER_MARKERS = (
    "…",
    "...",
    "EXAMPLE",
    "XXXX",
    "xxxx",
    "xxx",
    "YOUR_",
    "your_",
    "Your_",
    "changeme",
    "CHANGE_ME",
    "placeholder",
    "<api",
    "<your",
    "<token",
    "$",
    "{",
    "}",
)


def _is_placeholder(text: str) -> bool:
    """Return True if the matched token looks like a documentation placeholder."""
    return any(marker in text for marker in _PLACEHOLDER_MARKERS)


def _plain_code_content(text: str) -> bool:
    """Heuristic: text is likely code, not prose/documentation."""
    return text.count("\n") > 0 and (
        "=" in text or ";" in text or "def " in text or "import " in text or "#" in text
    )


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


# File extensions treated as code when deciding whether a token assignment is
# a real secret vs. a documentation example.
_CODE_SUFFIXES = frozenset({".py", ".sh", ".js", ".ts", ".rb", ".go", ".rs", ".java", ".pl", ".php", ".ps1"})


def _scan_text(text: str, rel_path: str) -> List[dict]:
    """Run all local heuristics over file content; return issue dicts."""
    issues: List[dict] = []
    is_code = Path(rel_path).suffix in _CODE_SUFFIXES or _plain_code_content(text[:2000])

    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()

        # Full private key blocks (any language). Placeholder guard: a real key
        # block's second line is a long base64 run; skip doc examples containing
        # ellipses/placeholder markers.
        if _PRIVATE_KEY_HEADER.search(stripped):
            # Look ahead in the next few lines for a long base64 payload; if the
            # block is documented with ellipses, it is not a real key.
            window = stripped + "\n" + "\n".join(
                l for l in text.splitlines()[line_no : line_no + 4]
            )
            if _is_placeholder(window) or len(re.sub(r"[^A-Za-z0-9+/=]", "", window)) < 128:
                continue
            issues.append({
                "code": "SECRET",
                "file": rel_path,
                "line": line_no,
                "message": "private key material found",
            })
            continue

        for regex, code, label in _TOKEN_PATTERNS:
            for m in regex.finditer(stripped):
                token = m.group(0)
                if _is_placeholder(token):
                    continue
                issues.append({
                    "code": code,
                    "file": rel_path,
                    "line": line_no,
                    "message": f"{label} found",
                })
                break  # one secret issue per line

        for m in _ASSIGN_PATTERN.finditer(stripped):
            value = m.group(1)
            if _is_placeholder(value):
                continue
            # In prose, `password = "..."` is usually documentation; in code it
            # is a hard-coded secret.
            if not is_code:
                continue
            if re.fullmatch(r"[A-Za-z0-9+/=_.\-]{12,}", value) is None:
                continue
            issues.append({
                "code": "SECRET",
                "file": rel_path,
                "line": line_no,
                "message": f"hard-coded {m.group(0).split(':')[0].split('=')[0].strip().lower()} value",
            })

    # Prompt injection and dangerous commands over the whole text.
    for regex, code, label in _INJECTION_PATTERNS:
        for m in regex.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            issues.append({
                "code": code,
                "file": rel_path,
                "line": line_no,
                "message": label,
            })

    for regex, code, label in _DANGEROUS_COMMANDS:
        for m in regex.finditer(text):
            # Flag only executable code or shell snippets, not prose that merely
            # *mentions* the pattern (e.g. a security checklist).
            snippet = text[m.start() : m.end()]
            if not is_code and not any(tok in snippet for tok in (">", "|", "$(")):
                continue
            line_no = text[: m.start()].count("\n") + 1
            issues.append({
                "code": code,
                "file": rel_path,
                "line": line_no,
                "message": label,
            })

    return issues


# VCS metadata / build artifacts that must never be scanned.
_IGNORE_DIRS = frozenset({".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"})
_IGNORE_FILES = frozenset({"*.pyc", ".DS_Store"})


def scan_skill_directory(skill_dir: Path) -> ScanResult:
    """Run the local static analysis over every file in the skill directory."""
    result = ScanResult(scan_path=str(skill_dir), component_name=skill_dir.name)

    files = [f for f in skill_dir.rglob("*") if f.is_file()]
    if not files:
        result.error = {
            "message": "No files found in skill directory",
            "category": "file_not_found",
        }
        return result

    for f in sorted(files):
        if any(part in _IGNORE_DIRS for part in f.parts):
            continue
        if any(f.match(pattern) for pattern in _IGNORE_FILES):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if not text.strip():
            continue
        try:
            rel_path = str(f.relative_to(skill_dir))
        except ValueError:
            rel_path = f.name
        result.issues.extend(_scan_text(text, rel_path))

    return result


def print_scan_result(result: ScanResult, verbose: bool = False, file=None) -> None:
    """Print the result for a single skill scan (plain ASCII)."""
    out = file or sys.stdout
    security_issues = result.security_issues
    info_issues = result.info_issues

    if result.error:
        err_msg = result.error.get("message", "Unknown error")
        category = result.error.get("category", "")
        if category == "file_not_found":
            print(f"  SKIP  - {err_msg}", file=out)
        else:
            print(f"  ERROR - {err_msg}", file=out)
    elif security_issues:
        for issue in security_issues:
            code = issue.get("code", "???")
            msg = issue.get("message", "No description")
            loc = issue.get("file", "")
            line = issue.get("line")
            location = f" {loc}:{line}" if loc and line else (f" {loc}" if loc else "")
            print(f"  FAIL  [{code}] {msg}{location}", file=out)
        if result.uncensored_domains:
            domains_str = ", ".join(sorted(result.uncensored_domains))
            print(f"         Uncensored domain(s): {domains_str}", file=out)
            print(f"         Add to {ALLOWLIST_FILENAME} to suppress", file=out)
    elif info_issues and verbose:
        for issue in info_issues:
            code = issue.get("code", "???")
            msg = issue.get("message", "No description")
            suffix = " (allowed)" if code in result.allowed_codes else ""
            print(f"  INFO  [{code}] {msg}{suffix}", file=out)
    else:
        print("  PASS", file=out)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="mcp-scan-checker",
        description="Local offline security scan of skills/<name>/ directories (no external scanner)",
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

    # Human-readable progress goes to stderr in --json mode so that stdout
    # carries ONLY the machine-readable report.
    log = sys.stderr if args.json else sys.stdout

    print("Local Skill Security Checker (offline, no external scanner)", file=log)
    print("=" * 60, file=log)

    repo_root = find_repo_root()
    print(f"Repository: {repo_root}", file=log)

    code_allowlist, domain_allowlist, placeholder_domains = load_allowlist(repo_root)

    if args.changed:
        skill_dirs = find_changed_skill_directories(repo_root, args.base)
        if not skill_dirs:
            print("No skill changes detected - nothing to scan.", file=log)
            if args.json:
                print(json.dumps({"exit_code": 0, "results": []}))
            return 0
    else:
        skill_dirs = find_skill_directories(repo_root)

    if not skill_dirs:
        print("No skills/ directories found to scan.", file=log)
        if args.json:
            print(json.dumps({"exit_code": 0, "results": []}))
        return 0

    print(f"Found {len(skill_dirs)} skill(s) to scan\n", file=log)

    results: List[ScanResult] = []
    passed = failed = errors = skipped = 0

    for i, skill_dir in enumerate(skill_dirs, 1):
        rel_path = skill_dir.relative_to(repo_root) if skill_dir.is_relative_to(repo_root) else skill_dir
        rel_str = str(rel_path).replace("\\", "/").rstrip("/")
        print(f"[{i}/{len(skill_dirs)}] {skill_dir.name} ({rel_path})", file=log)

        scan_result = scan_skill_directory(skill_dir)

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
        print_scan_result(scan_result, args.verbose, file=log)

        if scan_result.error:
            if scan_result.error.get("category") == "file_not_found":
                skipped += 1
            else:
                errors += 1
        elif scan_result.has_critical_issues:
            failed += 1
        else:
            passed += 1

    print("\n" + "-" * 60, file=log)
    parts = []
    if passed:
        parts.append(f"{passed} passed")
    if failed:
        parts.append(f"{failed} failed")
    if errors:
        parts.append(f"{errors} error(s)")
    if skipped:
        parts.append(f"{skipped} skipped")
    print(f"Results: {', '.join(parts)} ({len(results)} total)", file=log)

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
        print(f"\nSecurity scan FAILED: {failed} skill(s) with security issues.", file=log)
        return 1

    print("\nSecurity scan passed: all scanned skills are clean (or allowlisted).", file=log)
    return 0


if __name__ == "__main__":
    sys.exit(main())