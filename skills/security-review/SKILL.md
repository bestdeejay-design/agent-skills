---
name: security-review
description: "Security review orchestrator for dependency lockfiles and source: inventory of lockfiles/manifests (npm, pip, cargo, go, gem, maven, gradle, composer), exit-code classifier for 13 security tools (semgrep, bandit, gitleaks, osv-scanner, pip-audit, trufflehog, checkov, trivy, grype, npm audit, cargo audit), JSON normalizer to a unified finding schema, and human-readable reports. Stdlib-only Python helper + workflow for OWASP-aligned security review."
license: MIT
metadata:
  author: best
  version: "1.0.0"
  compatibility: "Requires Python 3 stdlib only. External scanners (semgrep, osv-scanner, ...) optional and used via their own CLIs."
when_to_use: "Use when running a security review of a codebase: 'security review', 'dependency audit', 'scan lockfiles', 'normalize scanner reports', 'vulnerability review'. Example: \"review my repo's dependencies for vulns\" or 'run a security review and normalize the reports'."
---

# Security Review — dependency & static analysis orchestration

Load this skill when you need to run a **security review of a codebase**:
audit the dependency manifest/lockfile inventory, decide which scanner to run
per ecosystem, interpret scanner exit codes correctly (real findings vs.
infrastructure errors), and normalize reports from different tools into **one
unified schema** for a final report.

The helper script is **offline by design** — it inventories, classifies, and
normalizes. Actual scans are executed by the well-known external tools listed
below (install once locally or in CI).

---

## The helper script

`scripts/security_review.py` — pure Python 3 stdlib (no dependencies).

| Command | Purpose |
|---|---|
| `security_review.py inventory --dir . ` | List dependency locks with ecosystem + suggested tool |
| `security_review.py inventory --dir . --json` | Same, machine-readable |
| `security_review.py classify --tool semgrep --exit-code 1` | Explain what a tool exit code means |
| `security_review.py normalize --tool osv-scanner --input out.json` | Flatten a tool JSON report into unified findings |
| `security_review.py normalize --tool pip-audit --input pip.json --output report.json` | Save unified report |
| `security_review.py report --root .` | Report skeleton (markdown default, `--json` for JSON) |

### Lockfile inventory (per-ecosystem suggested tool)

| Lockfile / manifest | Ecosystem | Suggested tool |
|---|---|---|
| `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock` | npm / pnpm / yarn | `npm audit` / `osv-scanner` |
| `requirements*.txt`, `pyproject.toml`, `Pipfile.lock`, `poetry.lock` | pip | `pip-audit` |
| `Cargo.lock` | cargo | `cargo audit` |
| `go.mod`, `go.sum` | go | `osv-scanner` |
| `Gemfile.lock` | gem | `osv-scanner` |
| `pom.xml`, `build.gradle(.kts)` | maven / gradle | `osv-scanner` / `dependency-check` |
| `composer.lock` | composer | `osv-scanner` |

`package.json` alone (no lockfile) is still reported, so gate or scan it with `npm audit`.

---

## Exit-code semantics (verified August 2026)

Get each tool's meaning on the fly with `classify --tool X --exit-code N`.

| Tool | `0` | findings | error / other |
|---|---|---|---|
| semgrep | clean | `1` (findings) | `2` fatal; `3/4/5/7/8/13/99` specific errors |
| bandit | clean | `1` (issues) | `2` error |
| gitleaks | clean | `1` (leaks or error) | `126` unknown flag |
| pip-audit | clean | `1` (vulns) | — |
| osv-scanner v2 | clean | `1` (vulns) | `127` error, `128` no packages, `129` API failed, `130` config |
| npm audit | clean | `1` (vulns) | — |
| cargo audit | clean | non-zero (vulns / errors) | — |
| grype | clean | `2` (vulns ≥ fail-on) | `1` error, `100` DB update |
| truffle | clean | `183` (findings, only with `--fail`) | `1` error |
| checkov | clean | `1` (failed checks) | `2` error |
| trivy | clean | `1` (vulns, with `--exit-code`) | — |
| dependency-check | clean | `1` (vulns ≥ threshold) | — |

**Rule of thumb:** `exit 0` == "no findings" only for tools listed as clean=0; other codes are infra errors and must not be treated as "vulnerable".

---

## Workflow

1. **Inventory** — `security_review.py inventory --dir <project> --json` → know exactly which lockfiles exist and which tool applies.
2. **Scan** — run the suggested tool per row above with its JSON format (see `references/canonical-patterns.md` for exact CLI + JSON shapes; e.g. semgrep JSON with `--json`, osv-scanner `--json`, pip-audit `--format json`, gitleaks `--report-format json`, bandit `-f json`).
3. **Classify exits** — in CI, map exit codes via `classify` so `1 = findings`, `2+ = infra error`.
4. **Normalize** — `normalize --tool <t> --input <scanner.json>` → unified findings (ruleId/rule/level/message/path/line/col).
5. **Report** — merge all normalized findings into one report (markdown or JSON), present severity rollup.

## When NOT to use

- **Not a scanner itself** — it does not detect vulnerabilities; it orchestrates/normalizes the real scanners. Run the real tools.
- **Not a secret detector** — use the `secret-scanner` skill for credentials/tokens.
- **Not a web scanner** — OWASP Top-10 dynamic testing is out of scope.

## Success criteria

- `inventory` lists every lockfile in the target directory with correct ecosystem + suggested tool.
- `classify --exit-code` matches the verified table above for your installed tools.
- `normalize` produces a valid unified report for the 5 built-in formats (osv-scanner, pip-audit, semgrep, gitleaks, bandit).
- CI gate: exit `1` on real findings, `EXIT_NEUTRAL` (or `2`) on infra errors, clean on 0.
