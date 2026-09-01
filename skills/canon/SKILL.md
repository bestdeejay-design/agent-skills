---
name: canon
description: >
  Orchestrator for the Chronos Pantheon — runs agent presets (minimal/standard/full), aggregates reports,
  validates cross-references between L1-L3 (contracts → product → engineering). Use when: "run full audit",
  "chronos full", "cross-reference validation", "canon".
license: MIT
metadata:
  version: 1.0.0
when_to_use: "Use to orchestrate Chronos agents: 'run full audit', 'chronos full', 'cross-reference validation', 'canon'."
---

# Canon — Orchestrator

Runs Chronos agent presets, aggregates reports, validates cross-references between L1-L3.

## Presets

| Preset | Agents | Description |
|--------|--------|-------------|
| `minimal` | Censor | Duplicates + broken links only |
| `standard` | Censor + Dewey + Canon | Check + classify + cross-ref |
| `full` | All 5 agents | Complete Pantheon |

## What it does

1. Receives preset (minimal/standard/full)
2. Determines required agents
3. Executes agents in sequence
4. Aggregates findings into unified report
5. Validates L1→L2→L3 cross-references (contracts match docs)

## Usage

```bash
# Via Chronos orchestrator
chronos --path . --preset full

# Direct invocation
python -m chronos.agents.canon --path . --preset full
```

## Cross-Reference Validation

Canon checks consistency between levels:

- **L1→L2**: OpenAPI endpoints documented in PRD/FEATURES
- **L2→L3**: Architecture decisions trace to PRD requirements
- **L3→L1**: ADRs reference contract versions

## Output Format

```
[info] preset: full
[info] agents_run: censor, dewey, veles, canon
[warning] cross_ref: GET /users in openapi.yaml (v2.1) but PRD.md shows v2.0
[critical] cross_ref: ADR-005 references deprecated endpoint removed in v2.1
```

## Triggers

- `run full audit` / `full audit`
- `chronos full` / `chronos --preset full`
- `cross-reference validation` / `cross ref check`
- `canon`

## Integration

Loaded by Chronos as part of `standard` and `full` presets. Canon is both an agent and the preset orchestrator.