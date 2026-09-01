---
name: veles
description: >
  Documentation statistician — finds orphan documents (no inbound references), computes documentation metrics,
  detects dead zones (folders unlinked from main docs), validates link hierarchy L1→L2→L3→L4.
  Use when: "find orphans", "orphan docs", "unreferenced documents", "documentation stats", "doc metrics",
  "dead zones", "link hierarchy", "veles".
license: MIT
metadata:
  version: 1.0.0
when_to_use: "Use for documentation statistics and orphan detection: 'find orphans', 'orphan docs', 'unreferenced documents', 'documentation stats', 'doc metrics', 'dead zones', 'link hierarchy', 'veles'."
---

# Veles — Statistician

Finds orphan documents, computes documentation metrics, detects dead zones, validates link hierarchy.

## What it does

- **Orphans** — documents with zero inbound references from other docs
- **Statistics** — file count, word count, level distribution, link count
- **Dead zones** — folders with no references from main documentation tree
- **Hierarchy validation** — enforces L1→L2→L3→L4 reference direction

## Link Hierarchy

```
L1 (Contracts) → L2 (Product Canon) → L3 (Engineering Canon) → L4 (Derived)
```

Upper levels reference lower levels. Veles flags violations (e.g., L3 referencing L1 directly).

## Usage

```bash
# Via Chronos orchestrator
chronos --path . --preset full

# Direct invocation
python -m chronos.agents.veles --path .
```

## Output Format

```
[nit] orphan: CONTRIBUTING.md — no inbound references from other documents
[info] stats: 12 documents, 4500 words, 3 levels, 28 links
[warning] hierarchy_violation: docs/ADR/001.md (L3) references contracts/openapi.yaml (L1) directly
[info] dead_zone: docs/legacy/ — no references from L1-L4
```

## Metrics Computed

| Metric | Description |
|--------|-------------|
| `total_files` | Markdown files scanned |
| `total_words` | Aggregate word count |
| `level_distribution` | Count per L1-L6 |
| `link_count` | Total internal links |
| `orphan_count` | Documents with 0 inbound links |
| `dead_zone_count` | Unreferenced folders |

## Triggers

- `find orphans` / `orphan docs` / `unreferenced documents`
- `documentation stats` / `doc metrics` / `documentation statistics`
- `dead zones` / `unlinked folders`
- `link hierarchy` / `reference hierarchy`
- `veles`

## Integration

Loaded by Chronos as part of `full` preset only.