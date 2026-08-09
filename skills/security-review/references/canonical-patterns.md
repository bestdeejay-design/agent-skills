# Security Review — Canonical Patterns

Deep dive behind `scripts/security_review.py`. Tool versions and exit codes
verified against upstream docs/CLI (August 2026). Patterns are the lockfile
inventory, the exit-code classifier, and the 5 built-in JSON normalizers.

---

## 1. Lockfile inventory

Directory walk (recursive, skipping `node_modules`, `.git`, `vendor`, `dist`,
`build`, `.venv`, `venv`, `__pycache__`). A `package.json` is reported only
when it has no sibling lockfile (otherwise the lockfile wins).

| Filename | Ecosystem | Primary tool |
|---|---|---|
| `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock` | npm/pnpm/yarn | `npm audit` / `osv-scanner` |
| `requirements*.txt` / `pyproject.toml` / `Pipfile.lock` / `poetry.lock` | pip | `pip-audit` |
| `Cargo.lock` | cargo | `cargo audit` |
| `go.mod` / `go.sum` | go | `osv-scanner` |
| `Gemfile.lock` | gem | `osv-scanner` |
| `pom.xml` / `build.gradle.kts` | maven/gradle | `osv-scanner` / `dependency-check` |
| `composer.lock` | composer | `osv-scanner` |

Notes:

- Prefer lockfiles over manifests: they pin exact versions, needed by
  vulnerability databases.
- `package.json` lockfile-less is legal (pure front-end) — audit it directly
  with `npm audit`, it is not a build-time dependency manifest.

---

## 2. Exit-code classifier (verified August 2026)

| Tool | 0 | 1 | 2 | other |
|---|---|---|---|---|
| semgrep | clean | findings | fatal error | `3/4/5/7/8/13/99` specific errors |
| bandit | clean | issues | error | — |
| gitleaks | clean | leaks OR error | — | `126` unknown flag |
| pip-audit | clean | vulns | — | — |
| osv-scanner v2 | clean | vulns | — | `127` error, `128` no packages, `129` API failed, `130` config |
| npm audit | clean | vulns | — | — |
| cargo audit | clean | vulns/error | — | — |
| grype | clean | error | vulns ≥ fail-on | `100` DB update required |
| trufflehog | clean | error | — | `183` findings only with `--fail` |
| checkov | clean | failed checks | error | — |
| trivy | clean | vulns `--exit-code` | — | — |
| dependency-check | clean | vulns ≥ threshold | — | — |

**CI rule:** exit `0` is trustworthy "no findings" for all except grype/trivy
where you need `--fail-on`.

---

## 3. JSON report shapes (normalizer inputs)

### osv-scanner (`osv-scanner --json --format json ...`)

```json
{"results": [{"source": {"path": "package-lock.json", "type": "lockfile"},
  "packages": [{"package": {"name": "lodash", "version": "4.17.20", "ecosystem": "npm"},
    "vulnerabilities": [{"id": "GHSA-xxx", "summary": "Prototype Pollution",
      "severity": [{"type": "GHSA", "severity": "HIGH"}], "aliases": ["CVE-2021-23337"]}]}]}]}
```

### pip-audit

```json
{"dependencies": [{"name": "requests", "version": "2.25.0",
  "vulns": [{"id": "CVE-2023-32681", "fix_versions": ["2.31.0"]}]}]}
```

### semgrep

```json
{"results": [{"check_id": "python.lang.security.audit.eval-use", "path": "app.py",
  "start": {"line": 42, "col": 5}, "end": {"line": 42, "col": 20},
  "extra": {"message": "...", "severity": "ERROR", "metadata": {"cwe": ["CWE-95"]}}}],
 "errors": []}
```

### gitleaks

```json
{"findings": [{"RuleID": "aws-access-token", "File": "config.js", "Secret": "AKIA…",
  "Match": "AKIA…", "StartLine": 10, "StartColumn": 20}]}
```

(Note: legacy `{"Findings": [...]}` capitalized key is also accepted.)

### bandit `-f json`

```json
{"errors": [], "results": [{"test_id": "B608", "issue_severity": "HIGH",
  "issue_confidence": "HIGH", "filename": "web.py", "line_number": 12,
  "test_name": "hardcoded_password_funcarg", "issue_text": "…"}]}
```

### SARIF 2.1.0 (bonus)

semgrep 1.x can emit `--sarif`; parsing path:

```json
{"runs": [{"results": [{"ruleId": "…", "level": "error",
  "locations": [{"physicalLocation": {"artifactLocation": {"uri": "app.py"},
    "region": {"startLine": 42, "startColumn": 5}}}],
  "message": {"text": "…"}}], "tool": {"driver": {"name": "semgrep"}}}]}
```

---

## 4. Severity mapping

Unified findings use `level` ∈ {error|warning|note}:

- semgrep `ERROR` / bandit `HIGH` → `error`
- semgrep `WARNING`, gitleaks secret, osv/pip-audit vulnerable-component → `warning`
- everything else staying a `note` for metadata.

---

## 5. GitHub & OWASP context

- **GitHub security features** to refresh data from: Dependabot alerts,
  Code scanning (SARIF upload), Secret scanning, and the `alerts` REST API.
- **OWASP Dependency-Check**: NVD-based SCA with a vulnerability threshold.
- Semgrep ruleset: *Trail of Bits* / **semgrep-rules** are canonical
  security-specific rules for code scanning; `--metrics=off`, `--json` for CI.
- Reference methodology: **NVIDIA SkillSpector** two-stage analysis,
  baseline suppression — borrowed for *interpretation*, not patterns.
