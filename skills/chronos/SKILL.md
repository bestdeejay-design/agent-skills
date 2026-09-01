---
name: chronos
description: >
  Documentation Timekeeper — 5 AI agents (Chronos, Censor, Dewey, Veles, Canon) for documentation integrity.
  Checks: duplicates, broken links, missing required docs, orphans, classification (L1-L6), stale dates.
  Use when: "check documentation", "docs audit", "audit docs", "docs integrity", "find duplicates in docs",
  "broken links", "stale documentation", "classify docs", "documentation health", "orphan docs",
  "validate docs", "doc quality", "docs lint", "chronos".
license: MIT
metadata:
  version: 1.0.0
when_to_use: "Use for documentation integrity audits: 'check documentation', 'docs audit', 'audit docs', 'docs integrity', 'find duplicates in docs', 'broken links', 'stale documentation', 'classify docs', 'documentation health', 'orphan docs', 'validate docs', 'doc quality', 'docs lint', 'chronos'."
---

# Chronos — Documentation Timekeeper

5 AI agents for documentation integrity. Each agent is a focused skill invoked by the Chronos orchestrator.

## What it does

Chronos audits project documentation for:

- **Duplicates** — documents with high similarity (Censor)
- **Broken links** — references to non-existent files (Censor)
- **Missing required docs** — mandatory files per classification level (Dewey)
- **Orphans** — documents with no inbound references (Dewey)
- **Classification** — document type: L1 Contracts → L6 Auxiliary (Dewey + Canon)
- **Stale data** — dates older than threshold (Veles)

## Agents

| Agent | Role | Trigger |
|-------|------|---------|
| **Chronos** | Orchestrator — runs the full Pantheon | `chronos --preset full` |
| **Censor** | Fact-checker — duplicates + broken links | `chronos --preset minimal` |
| **Dewey** | Classifier — L1-L6 taxonomy + missing/orphans | `chronos --preset standard` |
| **Veles** | Statistician — staleness, metrics, trends | `chronos --preset full` |
| **Canon** | Truth-keeper — cross-ref validation against contracts | `chronos --preset standard` |

## Usage

```bash
# Basic audit (duplicates + links only)
chronos --path .

# Standard: check + classify (Censor + Dewey + Canon)
chronos --path . --preset standard

# Full Pantheon: all 5 agents
chronos --path . --preset full

# JSON output for CI
chronos --path . --output json --output-file report.json

# Fail on critical findings
chronos --path . --fail-on critical

# Single agent
chronos --path . --agent censor
```

## Presets

| Preset | Agents | Use case |
|--------|--------|----------|
| `minimal` | Censor | Quick CI gate — duplicates + broken links |
| `standard` | Censor + Dewey + Canon | PR validation — check + classify + cross-ref |
| `full` | All 5 agents | Release audit — complete integrity + staleness |

## Document Hierarchy (L1–L6)

```
L1: Contracts        — Machine truth (OpenAPI, AsyncAPI, JSON Schema)
L2: Product Canon    — Human truth (VISION, PRD, ROADMAP, FEATURES)
L3: Engineering Canon— Implementation truth (ARCHITECTURE, ADR, SAGA)
L4: Derived          — Synthesized (REFERENCE, TEST_CASES, DEV_GUIDE)
L5: Artifacts        — Generated (API docs, changelogs, diagrams)
L6: Auxiliary        — Supporting (README, CONTRIBUTING, templates)
```

Each level has required files. Dewey enforces presence; Canon validates L1→L3 consistency.

## Output Format

```markdown
# Docs Audit Report

**Project:** /path/to/project
**Total docs:** 24
**Preset:** standard

| Severity | Count |
|----------|-------|
| Critical | 1 |
| Warning  | 3 |
| Info     | 2 |
| **Total**| **6** |

### CRITICAL

**File:** docs/API.md:42
**Issue:** Endpoint GET /users documented as Deprecated, but contract shows Active.
**Fix:** Update docs/API.md to match OpenAPI contract.

### WARNING

**File:** docs/ARCHITECTURE.md
**Issue:** Orphan document — no inbound references from L2/L3.
**Fix:** Link from PRD or add to REFERENCE.md.

### INFO

**File:** docs/DEV_GUIDE.md
**Issue:** Last updated 2024-01-15 (stale >180 days).
**Fix:** Review and update or archive.
```

## Triggers

- `check documentation` / `docs audit` / `audit docs`
- `docs integrity` / `documentation health`
- `find duplicates in docs` / `duplicate docs`
- `broken links` / `broken references`
- `stale documentation` / `outdated docs`
- `classify docs` / `document classification`
- `orphan docs` / `unreferenced documents`
- `validate docs` / `doc quality` / `docs lint`
- `chronos`

## Installation

```bash
pip install chronos
```

Or run directly:

```bash
python -m chronos --path .
```

## Project Structure

```
skills/chronos/
├── SKILL.md              # This file
├── src/chronos/          # Python package
│   ├── __init__.py
│   ├── cli.py            # Entry point
│   ├── orchestrator.py   # Chronos agent
│   ├── agents/
│   │   ├── censor.py     # Duplicates + links
│   │   ├── dewey.py      # Classification L1-L6
│   │   ├── veles.py      # Staleness + metrics
│   │   └── canon.py      # Cross-ref validation
│   ├── models.py         # Data classes
│   └── utils.py          # Helpers
├── tests/                # 67 pytest tests
├── presets/              # JSON presets
│   ├── minimal.json
│   ├── standard.json
│   └── full.json
└── pyproject.toml
```

## Configuration

Create `.chronos.yml` in project root:

```yaml
path: "."
preset: "standard"
fail_on: "warning"
output: "markdown"
thresholds:
  duplicate_similarity: 0.85
  stale_days: 180
  required_levels:
    L1: ["contracts/openapi.yaml"]
    L2: ["VISION.md", "PRD.md", "ROADMAP.md"]
    L3: ["ARCHITECTURE.md", "ADR/"]
    L4: ["REFERENCE.md"]
    L6: ["README.md", "CONTRIBUTING.md"]
ignore:
  - "node_modules/**"
  - ".git/**"
  - "dist/**"
```

## CI Integration

```yaml
# .github/workflows/docs-audit.yml
- name: Chronos Docs Audit
  run: |
    pip install chronos
    chronos --path . --preset standard --fail-on warning --output json --output-file chronos-report.json
```

## Verification Gates

Every Chronos run must pass:

1. **Structural** — output is valid Markdown/JSON
2. **Content QA** — each finding has file:line, issue, fix
3. **Reproducibility** — same input → same output (deterministic hashing)

## References

- `references/CLASSIFICATION.md` — L1-L6 taxonomy details
- `references/AGENTS.md` — Agent prompt templates
- `references/CONFIG.md` — Full config schema