---
name: dewey
description: >
  Document classifier — assigns L1-L6 taxonomy level to each document, enforces required docs per level,
  detects missing required documents. Use when: "classify docs", "document classification", "missing docs",
  "required documents", "document taxonomy", "dewey".
license: MIT
metadata:
  version: 1.0.0
when_to_use: "Use for document classification: 'classify docs', 'document classification', 'missing docs', 'required documents', 'document taxonomy', 'dewey'."
---

# Dewey — Classifier

Assigns taxonomy level (L1-L6) to each document, enforces required documents per project level.

## Document Hierarchy (L1–L6)

| Level | Type | Examples |
|-------|------|----------|
| L1 | Contracts | `contracts/openapi/*.yaml`, `contracts/asyncapi/*.yaml` |
| L2 | Product Canon | `docs/VISION.md`, `docs/PRD.md`, `docs/ROADMAP.md`, `docs/FEATURES.md` |
| L3 | Engineering Canon | `docs/ARCHITECTURE.md`, `docs/ADR/`, `docs/SAGA/`, `docs/TEST_CASES.md` |
| L4 | Derived | `docs/REFERENCE.md`, `docs/DEV_GUIDE.md`, `docs/STATUS.md` |
| L5 | Artifacts | Generated files (API docs, changelogs, diagrams) |
| L6 | Auxiliary | `README.md`, `CONTRIBUTING.md`, `LICENSE`, templates |

## What it does

- Classifies every document by type and level
- Determines project maturity level (L1-L3 based on required docs present)
- Validates required documents exist for detected level

## Usage

```bash
# Via Chronos orchestrator
chronos --path . --preset standard

# Direct invocation
python -m chronos.agents.dewey --path .
```

## Output Format

```
[warning] missing: Required L2 document missing — docs/ROADMAP.md
[info] classified: docs/ARCHITECTURE.md → L3 Engineering Canon
[info] project_level: L2 (Product Canon) — 3/4 required docs present
```

## Required Documents per Level

| Level | Required |
|-------|----------|
| L1 | At least 1 contract file (OpenAPI/AsyncAPI/JSON Schema) |
| L2 | VISION.md, PRD.md, ROADMAP.md |
| L3 | ARCHITECTURE.md, ADR/ directory |

## Triggers

- `classify docs` / `document classification`
- `missing docs` / `required documents`
- `document taxonomy` / `doc hierarchy`
- `dewey`

## Integration

Loaded by Chronos as part of `standard` and `full` presets.