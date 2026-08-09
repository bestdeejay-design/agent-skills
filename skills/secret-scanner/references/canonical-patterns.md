# Secret Scanner — Canonical Patterns

Deep dive behind `scripts/secret_scanner.py`. Everything below is grounded in
source-verified research (July 2026), not invented from memory:

- **gitleaks v8.30.1** — MIT — default config `config/gitleaks.toml`
  (the de-facto standard regex set), entropy function `detect/utils.go#L117-L134`,
  entropy gate `detect/detect.go#L542-L555`
- **TruffleHog v3** (Truffle Security) — 800+ typed detectors, API verification
- **detect-secrets** (Yelp) — entropy plugins (hex limit 3.0, base64 4.5)
- **git-secrets** (AWS Labs) — provider allowlist approach
- **NVIDIA SkillSpector** — two-stage analysis, baseline suppression
- **GitHub secret scanning** — partner patterns + generic entropy
- **ggshield** (GitGuardian) — managed pattern feed

---

## 0. Critical distinction: SkillSpector is NOT a secret scanner

NVIDIA/SkillSpector scans **AI agent skills** for prompt injection, MCP tool
poisoning, data exfiltration and privilege escalation — not for leaked tokens.
It contributes **methodology** only:

- Two-stage analysis: fast static pass → optional LLM semantic pass
- Severity scoring 0–100 with risk classes
- Baseline/false-positive suppression: re-scans surface only *new* findings

Our scanner borrows the methodology; the actual secret patterns come from
**gitleaks**, because SkillSpector's pattern coverage does not cover tokens.

---

## 1. Detection model (as in this skill)

```
raw text ──▶ 19 typed regex rules ──▶ allowlist filters ──▶ Shannon entropy gate ──▶ finding
                                          │                        │
                      placeholder/example               entropy <= rule.Entropy → skip
                      noise path/extension              (strictly greater required)
```

Key properties:

- **Offline by default.** A format match = *potential* secret, never *verified*.
- **Typed rules first**, generic rule last (keyword-anchored + entropy 3.5).
- **Rule-level entropy minimums** mimic gitleaks per-rule `entropy` values.

## 3. High-signal pattern table (verbatim from gitleaks v8.30.1)

| Provider | Env var (common) | Regex / prefix | Entropy | Risk in skill |
|---|---|---|---|---|
| AWS Access Key ID | `AWS_ACCESS_KEY_ID` | `\b((?:A3T[A-Z0-9]|AKIA|ASIA|ABIA|ACCA)[A-Z2-7]{16})\b` | 3.0 | Critical |
| AWS Secret Access Key | `AWS_SECRET_ACCESS_KEY` | keyword-anchored + 40-char base64 (no stable prefix) | 3.5 | Critical |
| GitHub PAT (classic) | `GITHUB_TOKEN` | `ghp_[0-9a-zA-Z]{36}` | 3.0 | Critical |
| GitHub fine-grained | — | `github_pat_\w{82}` | 3.0 | Critical |
| GitHub OAuth / refresh | `GH_TOKEN` | `gho_[0-9a-zA-Z]{36}` / `ghr_[0-9a-zA-Z]{36}` | 3.0 | Critical |
| OpenAI API key | `OPENAI_API_KEY` | `sk-(proj\|svcacct\|admin)-…T3BlbkFJ…` or legacy `sk-…T3BlbkFJ…` (fixed marker = base64 of "sk-") | 3.0 | Critical |
| Anthropic API / admin | `ANTHROPIC_API_KEY` | `sk-ant-api03-…AA` / `sk-ant-admin01-…AA` (fixed structure, **no entropy gate**) | — | Critical |
| Stripe secret/restricted | `STRIPE_SECRET_KEY` | `(sk|rk)_(test|live|prod)_…` | 2.0 | Critical (live) |
| Google API key (GCP) | `GOOGLE_API_KEY` | `AIza[\w-]{35}` | 3.5/4.0 | Critical |
| Slack app-level / bot / user | `SLACK_*_TOKEN` | `xapp-\d-…` / `xoxb-…` / `xoxp-…` / `xoxe-…` | 2.0–3.0 | High |
| Slack webhook | `SLACK_WEBHOOK_URL` | `hooks.slack.com/{services\|workflows\|triggers}/…` | — | High |
| Private key (PEM/OpenSSH/PGP) | — | `-----BEGIN … PRIVATE KEY…-----` block | **no entropy gate** | Critical |
| JWT | — | `ey…\.ey…\....` | 3.0 | Medium |
| Perplexity | `PERPLEXITY_API_KEY` | `pplx-[a-zA-Z0-9]{48}` | 4.0 | High |
| Generic API key (fallback) | any `*_KEY` | keyword anchor + `[\w.\-]{10,150}` | 3.5 | Medium |

### Fixed-format (no entropy) rules — the important detail

`entropy=None` for: private keys, Anthropic `sk-ant-*`, Slack webhooks. The
**structure itself** is the signal, entropy adds nothing. This follows
gitleaks exactly.

---

## 4. Shannon entropy (verbatim reference)

From gitleaks `detect/utils.go#L117-L134`:

```go
func shannonEntropy(data string) (entropy float64) {
	if data == "" { return 0 }
	charCounts := make(map[rune]int)
	for _, char := range data { charCounts[char]++ }
	invLength := 1.0 / float64(len(data))
	for _, count := range charCounts {
		freq := float64(count) * invLength
		entropy -= freq * math.Log2(freq)
	}
	return entropy
}
```

Python stdlib equivalent (implemented in this skill):

```python
import math
from collections import Counter

def shannon_entropy(data: str) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    inv_len = 1.0 / len(data)
    return -sum((c * inv_len) * math.log2(c * inv_len) for c in counts.values())
```

Threshold semantics (verified): **skip the finding when `entropy <= r.Entropy`**,
i.e. strictly greater than the rule minimum is required to report
(`detect.go#L546-L547`).

Reference thresholds:
- gitleaks per-rule: `{2.0, 2.75, 3.0, 3.5, 4.0, 4.5}`
- detect-secrets: `HexStringDetector(limit=3.0)`, `Base64StringDetector(limit=4.5)`;
  matches must be **strictly above**; scans **quoted strings only** to cut noise;
  all-digit hex penalty `entropy -= 1.2 / log2(len)`
- TruffleHog: `--filter-entropy=3.0`

Entropy is the fallback when providers change token formats. It is FP-prone,
so we only use it anchored (keyword context, assignment operators) and always
pair it with allowlists.

---

## 5. Allowlists (false-positive mitigation)

Verbatim-derived from gitleaks global/path allowlists + top FP sources:

| Category | Rules applied |
|---|---|
| Placeholders | `$VAR`, `${VAR}`, `{{ … }}`, `%VAR%`, `true/false/null/None`, `****`, `EXAMPLE`, `xxxx`, `your-`, `placeholder`, `TODO`, `CHANGE_ME`, `REPLACE_ME` |
| Example/known-keys | `AKIAIOSFODNN7EXAMPLE` (AWS docs), GCP `AIza…` demo keys, `.+EXAMPLE$` suffix |
| Noisy paths | `node_modules/`, `vendor/`, `.git/`, `dist/`, `build/`, `.venv/`, `__pycache__/` |
| Noisy files | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `go.sum`, `composer.lock`, `requirements.txt`, `Pipfile.lock`, `poetry.lock`, `Cargo.lock`, `Gemfile.lock` |
| Binaries/media | `.min.js`, `.map`, images, fonts, PDFs, archives, `.pyc`, `.class`, executables |
| Stopwords (generic rule only) | hex UUIDs, `000000`, `aaaaaa`, dictionary triples, … |

Additional heuristic filters (from TruffleHog/detect-secrets):

1. **Quoted-only entropy**: never bare-scan bare high-entropy outside quoted
   strings (detect-secrets).
2. **severity by context**: `sk_test_` < `sk_live_`; `testdata/`, `fixtures/`,
   `*.md` = verify-before-report; `.env.example` = FP unless committed for real.
3. **Don't scan compressed blobs** (default `--max-mb 10` for this skill /
   gitleaks `--max-target-megabytes` + `--max-archive-depth 0`).
4. **Line-level ignore comments** (gitleaks `gitleaks:allow`, detect-secrets
   `# pragma: allowlist secret`).

---

## 6. Exit-code & CI model

gitleaks CI model (adapted to stdlib):

```bash
gitleaks dir . --report-format=json --report-path=report.json --exit-code 1
```

Our mirror:

```bash
python3 secret_scanner.py --path . --json --exit-code   # exit 1 when findings present
```

Exit codes: `0` clean (default) · `1` findings (only with `--exit-code`) ·
`2` usage/IO error.

---

## 7. Baseline / suppression (SkillSpector & gitleaks)

Both gitleaks (`--baseline-path`, `.gitleaksignore`) and SkillSpector use the
same idea: **store known findings, re-scan surfaces only new ones**. This skill
implements the *operator-facing* equivalent — write the JSON report to a file,
re-scan and diff findings by finger (path+line+rule+secret-hash). Keep
suppressions reviewable (committed baseline file), never silent.

---

## 8. Verification is the operator's job

A format match ≠ live credential. The scanner stays offline, but the
`canonical-patterns.md` documents the verification commands the *operator*
should run before alarming:

- **AWS** — `aws sts get-caller-identity` (TruffleHog does exactly this)
- **GitHub** — `GET /user` with `Authorization: Bearer <token>`
- **OpenAI/Anthropic/Stripe/Google** — provider `/v1/me` endpoints
- **Offline heuristics (bundled)** — token length/grammar, `T3BlbkFJ` marker for
  OpenAI, `AA` suffix for Anthropic, 82 chars after `github_pat_`, `EXAMPLE` suffix

---

## 9. Remediation workflow (in order)

1. **Rotate first, scrub second** — a committed secret lives in forks, caches,
   CI logs, bots. Revoke in provider console, issue new key, redeploy config.
2. **Scrub history**:
   - `git filter-repo` (preferred — `git clone --mirror`, `--invert-paths`, push
     filtered refs with repo-admin coordination)
   - BFG Repo-Cleaner (JVM alternative) or `git-secrets --scan-history`
3. **Expire stored copies** — GitHub cached views of forks/blobs (support), CI
   caches, artifact stores.
4. **Prevent recurrence** — scanner in CI with exit-code gate, pre-commit hooks
   (`git-secrets --install --register-aws`), GitHub push protection, `.env` in
   `.gitignore`.
5. **Log the incident** — repo/commit/author/time/severity/blast radius; a
   secret-rotation ticket for every Critical finding.

---

## Sources

- gitleaks: <https://github.com/gitleaks/gitleaks> — `config/gitleaks.toml`,
  `detect/utils.go#L117-L134`, `detect/detect.go#L542-L547`, `README.md`
- TruffleHog: <https://github.com/trufflesecurity/trufflehog> (800+ detectors,
  `--filter-entropy=3.0`, verification statuses)
- detect-secrets: <https://github.com/Yelp/detect-secrets> —
  `detect_secrets/plugins/high_entropy_strings.py`, `private_key.py`
- git-secrets (AWS Labs): <https://github.com/awslabs/git-secrets> —
  `--register-aws`, `.gitallowed`
- ggshield: <https://github.com/GitGuardian/ggshield>
- GitHub secret scanning: <https://docs.github.com/en/code-security/secret-scanning>
- NVIDIA SkillSpector: <https://github.com/NVIDIA/SkillSpector> —
  `static_patterns_data_exfiltration.py` (env harvesting), `docs/SUPPRESSION.md`