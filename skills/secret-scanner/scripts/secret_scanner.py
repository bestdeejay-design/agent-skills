#!/usr/bin/env python3
"""secret-scanner — static secret/token detection with Python 3 stdlib only.

Scans a file, directory tree, or git index for leaked credentials using a
pattern table derived from gitleaks v8.30.1 default config
(https://github.com/gitleaks/gitleaks/blob/b58d3f102/config/gitleaks.toml),
Shannon entropy gating (same algorithm as gitleaks detect/utils.go#L117-L134),
and allowlist filters that suppress known false positives.

Input sources (priority):
    --path PATH   file or directory to scan recursively
    --git REPO    scan "git ls-files" tracked files of a repo (uses git CLI)
    stdin         read a single blob from stdin (default)

Options:
    --json            machine-readable JSON report
    --markdown        Markdown report
    --redact N        mask values (keep first N chars, e.g. --redact 8)
    --max-mb N        skip files larger than N MB (default 10)
    --exit-code       exit 1 when findings present (CI gate); default 0
    --no-color        disable ANSI colors in text mode

Rules model (per pattern):
    id, provider, env var, regex, entropy (rule minimum; finding skipped when
    entropy <= rule.Entropy — strictly greater required, per
    detect/detect.go#L542-L555), risk (Critical/High/Medium).

Allowlists (from gitleaks global allowlist):
    placeholders  $VAR, ${VAR}, {{ }}, %VAR%, true/false/null, *****, EXAMPLE,
    xxxx, your-, placeholder, TODO, CHANGE_ME, REPLACE_ME
    paths        lockfiles, node_modules/, vendor/, .git/, binaries/images,
                 minified JS, fonts

Exit codes:
    0  no findings (always, unless --exit-code)
    1  findings present (only with --exit-code)
    2  usage / IO error

Dependencies: Python 3 stdlib only (re, math, collections, pathlib, argparse).
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


# --- Shannon entropy (verbatim algorithm from gitleaks detect/utils.go) ------
def shannon_entropy(data: str) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    inv_len = 1.0 / len(data)
    return -sum((c * inv_len) * math.log2(c * inv_len) for c in counts.values())


# --- Placeholder / example / noise allowlists --------------------------------
PLACEHOLDER_RULES = [
    r"^[$]?\{\{?[A-Za-z0-9_\-:.]+}?}?$",      # $VAR, ${VAR}, {{VAR}}, {:var}
    r"^%[A-Za-z0-9_]+%$",                     # %VAR% (Windows)
    r"^(true|false|null|None|undefined)$",
    r"^\*{4,}$",                              # redacted ****
    r"EXAMPLE", r"xxxx", r"your-", r"placeholder", r"TODO",
    r"CHANGE_ME", r"REPLACE_ME",
    r"^(change|sample|example|dummy|test|fake|secret|password|token|key|id)$",
]
PLACEHOLDER_RX = [re.compile(p, re.IGNORECASE) for p in PLACEHOLDER_RULES]
STOPWORDS = {
    "abcdefghijklmnopqrstuvwxyz", "0123456789", "aaaaaa", "bbbbbb",
    "testtest", "abcdef", "fabcde", "deadbeef", "feedface", "cafebabe",
    "00000000000000000000000000000000", "11111111111111111111111111111111",
    "12345678901234567890123456789012",
}
NOISE_DIRS = {
    "node_modules", "vendor", ".git", ".venv", "venv", "dist", "build",
    "__pycache__", "coverage", "htmlcov",
}
NOISE_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "go.sum",
    "composer.lock", "Gemfile.lock", "poetry.lock", "Cargo.lock",
    "Pipfile.lock", "requirements.txt",
}
NOISE_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".woff",
    ".woff2", ".ttf", ".otf", ".eot", ".pdf", ".zip", ".gz", ".tar",
    ".7z", ".jar", ".class", ".min.js", ".map", ".pyc", ".so", ".dll",
    ".dylib", ".exe",
}


# --- Rules -------------------------------------------------------------------
# Regexes quoted verbatim from gitleaks v8.30.1 default config/gitleaks.toml.
# entropy=None => fixed-structure rule, no entropy gate (private keys, anthropic).
RULES = [
    {
        "name": "aws-access-token",
        "provider": "AWS Access Key ID",
        "env": "AWS_ACCESS_KEY_ID",
        "regex": r"\b((?:A3T[A-Z0-9]|AKIA|ASIA|ABIA|ACCA)[A-Z2-7]{16})\b",
        "entropy": 3.0,
        "risk": "Critical",
    },
    {
        "name": "aws-secret-key",
        "provider": "AWS Secret Access Key",
        "env": "AWS_SECRET_ACCESS_KEY",
        "regex": r"(?i)\baws(.{0,20})?(['\"])([0-9a-zA-Z/+]{40})\2\b",
        "entropy": 3.5,
        "risk": "Critical",
    },
    {
        "name": "github-pat",
        "provider": "GitHub PAT (classic)",
        "env": "GITHUB_TOKEN",
        "regex": r"\b(ghp_[0-9a-zA-Z]{36})\b",
        "entropy": 3.0,
        "risk": "Critical",
    },
    {
        "name": "github-fine-grained-pat",
        "provider": "GitHub fine-grained PAT",
        "env": "GITHUB_TOKEN",
        "regex": r"\b(github_pat_\w{82})\b",
        "entropy": 3.0,
        "risk": "Critical",
    },
    {
        "name": "github-oauth",
        "provider": "GitHub OAuth token",
        "env": "GITHUB_TOKEN",
        "regex": r"\b(gho_[0-9a-zA-Z]{36})\b",
        "entropy": 3.0,
        "risk": "Critical",
    },
    {
        "name": "github-refresh-token",
        "provider": "GitHub refresh token",
        "env": "GITHUB_TOKEN",
        "regex": r"\b(ghr_[0-9a-zA-Z]{36})\b",
        "entropy": 3.0,
        "risk": "Critical",
    },
    {
        "name": "openai-api-key",
        "provider": "OpenAI API key",
        "env": "OPENAI_API_KEY",
        "regex": (
            r"\b(sk-(?:proj|svcacct|admin)-(?:[A-Za-z0-9_-]{74}|[A-Za-z0-9_-]{58})"
            r"T3BlbkFJ(?:[A-Za-z0-9_-]{74}|[A-Za-z0-9_-]{58})\b"
            r"|sk-[a-zA-Z0-9]{20}T3BlbkFJ[a-zA-Z0-9]{20})"
        ),
        "entropy": 3.0,
        "risk": "Critical",
    },
    {
        "name": "anthropic-api-key",
        "provider": "Anthropic API key",
        "env": "ANTHROPIC_API_KEY",
        "regex": r"\b(sk-ant-api03-[a-zA-Z0-9_\-]{93}AA)\b",
        "entropy": None,
        "risk": "Critical",
    },
    {
        "name": "anthropic-admin-key",
        "provider": "Anthropic admin key",
        "env": "ANTHROPIC_ADMIN_KEY",
        "regex": r"\b(sk-ant-admin01-[a-zA-Z0-9_\-]{93}AA)\b",
        "entropy": None,
        "risk": "Critical",
    },
    {
        "name": "stripe-secret-key",
        "provider": "Stripe secret/restricted key",
        "env": "STRIPE_SECRET_KEY",
        "regex": r"\b((?:sk|rk)_(?:test|live|prod)_[a-zA-Z0-9]{10,99})\b",
        "entropy": 2.0,
        "risk": "Critical",
    },
    {
        "name": "google-api-key",
        "provider": "Google API key",
        "env": "GOOGLE_API_KEY",
        "regex": r"\b(AIza[\w-]{35})\b",
        "entropy": 4.0,
        "risk": "Critical",
    },
    {
        "name": "slack-app-token",
        "provider": "Slack app token",
        "env": "SLACK_APP_TOKEN",
        "regex": r"(?i)xapp-\d-[A-Z0-9]+-\d+-[a-z0-9]+",
        "entropy": 2.0,
        "risk": "High",
    },
    {
        "name": "slack-bot-token",
        "provider": "Slack bot token",
        "env": "SLACK_BOT_TOKEN",
        "regex": r"\bxoxb-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*\b",
        "entropy": 3.0,
        "risk": "High",
    },
    {
        "name": "slack-user-token",
        "provider": "Slack user token",
        "env": "SLACK_USER_TOKEN",
        "regex": r"\bxox[pe](?:-[0-9]{10,13}){3}-[a-zA-Z0-9-]{28,34}\b",
        "entropy": 2.0,
        "risk": "High",
    },
    {
        "name": "slack-webhook-url",
        "provider": "Slack webhook",
        "env": "SLACK_WEBHOOK_URL",
        "regex": (
            r"(?:https?://)?hooks\.slack\.com/"
            r"(?:services|workflows|triggers)/[A-Za-z0-9+/]{43,56}"
        ),
        "entropy": None,
        "risk": "High",
    },
    {
        "name": "private-key",
        "provider": "Private key (PEM/OpenSSH/PGP)",
        "env": None,
        "regex": (
            r"(?i)-----BEGIN[ A-Z0-9_-]{0,100}PRIVATE KEY(?: BLOCK)?-----"
            r"[\s\S-]{64,}?KEY(?: BLOCK)?-----"
        ),
        "entropy": None,
        "risk": "Critical",
    },
    {
        "name": "jwt",
        "provider": "JWT",
        "env": None,
        "regex": (
            r"\b(ey[a-zA-Z0-9]{17,}\.ey[a-zA-Z0-9\/\\_-]{17,}\."
            r"(?:[a-zA-Z0-9\/\\_-]{10,}={0,2})?)\b"
        ),
        "entropy": 3.0,
        "risk": "Medium",
    },
    {
        "name": "perplexity-api-key",
        "provider": "Perplexity API key",
        "env": "PERPLEXITY_API_KEY",
        "regex": r"\b(pplx-[a-zA-Z0-9]{48})\b",
        "entropy": 4.0,
        "risk": "High",
    },
    {
        "name": "generic-api-key",
        "provider": "Generic API key (keyword-anchored)",
        "env": "*_API_KEY",
        # keyword near assignment + token-like value, gitleaks entropy 3.5
        "regex": (
            r"(?i)\b(?:api[_-]?key|access[_-]?(?:token|key)"
            r"|auth[_-]?(?:token|key)|client[_-]?secret|secret"
            r"|token|password|passwd|credential|creds)\b"
            r"[\s]*[=:>][\s]*['\"]?([\w.\-]{10,150})['\"]?"
        ),
        "entropy": 3.5,
        "risk": "Medium",
    },
]

# --- Helpers ------------------------------------------------------------------
def compile_rules():
    compiled = []
    for rule in RULES:
        try:
            compiled.append({**rule, "rx": re.compile(rule["regex"])})
        except re.error as exc:
            print(f"warning: bad regex in rule {rule['name']}: {exc}", file=sys.stderr)
    return compiled


def is_placeholder(value: str) -> bool:
    low = value.lower()
    if low in STOPWORDS:
        return True
    return any(rx.search(value) for rx in PLACEHOLDER_RX)


def is_noise_path(rel: str, is_git: bool = False) -> bool:
    parts = [p.lower() for p in Path(rel).parts]
    if any(d in NOISE_DIRS for d in parts):
        return True
    name = Path(rel).name.lower()
    if name in NOISE_FILES:
        return True
    if is_git and name in {".env", ".env.*"}:
        return False  # tracked .env files are exactly what we want
    if any(Path(rel).suffix.lower() == s for s in NOISE_SUFFIXES):
        return True
    if name.startswith(".") and name != ".env":
        return True
    return False


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def redact(value: str, keep: int) -> str:
    if keep is None or len(value) <= keep:
        return value
    return value[:keep] + "…" * (len(value) - keep)


# --- Scanning -----------------------------------------------------------------
def scan_text(path: str, text: str, rules, redact_keep):
    """Run all rules over one text blob. Returns list of finding dicts."""
    findings = []
    for rule in rules:
        for m in rule["rx"].finditer(text):
            # generic rule captures the value in group 1
            if rule["name"] == "generic-api-key" and m.lastindex:
                raw = m.group(1)
            else:
                raw = m.group(0)
            if is_placeholder(raw):
                continue
            ent = None
            if rule["entropy"] is not None:
                ent = shannon_entropy(raw)
                # strictly greater than the rule minimum (gitleaks semantics)
                if ent <= rule["entropy"]:
                    continue
            findings.append(
                {
                    "rule": rule["name"],
                    "provider": rule["provider"],
                    "severity": rule["risk"],
                    "secret": redact(raw, redact_keep),
                    "entropy": round(ent, 2) if ent is not None else None,
                    "path": path,
                    "line": line_of(text, m.start()),
                }
            )
    return findings


def scan_tree(root: str, rules, redact_keep, max_mb):
    findings = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d.lower() not in NOISE_DIRS]
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)
            if is_noise_path(rel):
                continue
            try:
                if os.path.getsize(full) > max_mb * 1024 * 1024:
                    continue
                with open(full, encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
            except OSError:
                continue
            findings.extend(scan_text(rel, text, rules, redact_keep))
    return findings


def scan_git(repo: str, rules, redact_keep, max_mb):
    try:
        proc = subprocess.run(
            ["git", "-C", repo, "ls-files"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        sys.exit("error: git не найден в PATH")
    if proc.returncode != 0:
        sys.exit(f"error: не удалось получить git ls-files из {repo}: {proc.stderr.strip()}")
    findings = []
    for rel in proc.stdout.splitlines():
        if not rel or is_noise_path(rel, is_git=True):
            continue
        full = os.path.join(repo, rel)
        try:
            if os.path.getsize(full) > max_mb * 1024 * 1024:
                continue
            with open(full, encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        except OSError:
            continue
        findings.extend(scan_text(rel, text, rules, redact_keep))
    return findings


# --- rendering ----------------------------------------------------------------
RISK_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
RISK_COLOR = {"Critical": "\033[31m", "High": "\033[33m", "Medium": "\033[36m"}


def render_text(findings, color):
    out = []
    for f in sorted(findings, key=lambda x: (RISK_ORDER.get(x["severity"], 9), x["path"], x["line"])):
        sev = f["severity"]
        if color:
            head = f"{RISK_COLOR.get(sev, '')}[{sev}]{'\033[0m'} {f['path']}:{f['line']} — {f['provider']} ({f['rule']})"
        else:
            head = f"[{sev}] {f['path']}:{f['line']} — {f['provider']} ({f['rule']})"
        ent = f", entropy={f['entropy']}" if f["entropy"] is not None else ""
        out.append(f"{head}\n    secret: {f['secret']}{ent}")
    return "\n".join(out)


def render_markdown(findings, target):
    lines = [
        f"# Secret Scan Report\n",
        f"**Target:** `{target}`  \n",
        f"**Date:** {datetime.now().isoformat(timespec='seconds')}  \n",
        f"**Findings:** {len(findings)}\n",
        "\n| Severity | File | Line | Provider | Secret | Entropy |",
        "|---|---|---|---|---|---|",
    ]
    for f in sorted(findings, key=lambda x: (RISK_ORDER.get(x["severity"], 9), x["path"], x["line"])):
        lines.append(
            f"| {f['severity']} | `{f['path']}` | {f['line']} | {f['provider']} "
            f"| `{f['secret']}` | {f['entropy'] if f['entropy'] is not None else '—'} |"
        )
    return "\n".join(lines)


def render_json(findings, target):
    return json.dumps(
        {
            "target": target,
            "generated": datetime.now().isoformat(timespec="seconds"),
            "total": len(findings),
            "findings": findings,
        },
        ensure_ascii=False,
        indent=2,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Static secret/token scanner (Python 3 stdlib, patterns from gitleaks v8.30.1)."
    )
    parser.add_argument("--path", help="file or directory to scan")
    parser.add_argument("--git", help="git repository: scan tracked files via git ls-files")
    parser.add_argument("--json", action="store_true", help="JSON report")
    parser.add_argument("--markdown", action="store_true", help="Markdown report")
    parser.add_argument("--redact", type=int, help="mask secret values, keep first N chars")
    parser.add_argument("--max-mb", type=int, default=10, help="skip files larger than N MB (default 10)")
    parser.add_argument("--exit-code", action="store_true", help="exit 1 when findings present (CI gate)")
    parser.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    args = parser.parse_args()

    rules = compile_rules()

    if args.path:
        target = args.path
        if os.path.isfile(target):
            with open(target, encoding="utf-8", errors="ignore") as fh:
                findings = scan_text(target, fh.read(), rules, args.redact)
        elif os.path.isdir(target):
            findings = scan_tree(target, rules, args.redact, args.max_mb)
        else:
            parser.error(f"путь не найден: {target}")
    elif args.git:
        target = args.git
        findings = scan_git(target, rules, args.redact, args.max_mb)
    else:
        target = "stdin"
        findings = scan_text("stdin", sys.stdin.read(), rules, args.redact)

    if args.json:
        print(render_json(findings, target))
    elif args.markdown:
        print(render_markdown(findings, target))
    else:
        print(render_text(findings, not args.no_color))
        print(f"\nTotal findings: {len(findings)}")

    if args.exit_code and findings:
        sys.exit(1)


if __name__ == "__main__":
    main()
