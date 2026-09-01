---
name: censor
description: >
  Fact-checker for documentation — detects duplicates (similarity >70%) and broken internal links in markdown files.
  Skips code blocks, inline code, and external URLs. Use when: "check duplicates", "find duplicate docs",
  "broken links", "broken references", "validate links", "censor".
license: MIT
metadata:
  version: 1.0.0
when_to_use: "Use for documentation fact-checking: 'check duplicates', 'find duplicate docs', 'broken links', 'broken references', 'validate links', 'censor'."
---

# Censor — Fact-Checker

Detects duplicate documents and broken internal links in markdown documentation.

## What it does

- **Duplicates** — finds documents with similarity above threshold (default 70%)
- **Broken links** — validates relative markdown links; skips code blocks, inline code, external URLs (http/https/mailto)

## Usage

```bash
# Via Chronos orchestrator
chronos --path . --preset minimal

# Direct invocation
python -m chronos.agents.censor --path .
```

## Output Format

```
[warning] duplicate: High similarity (85%) with docs/ROADMAP.md
[warning] broken_link: Broken link: missing.md
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `duplicate_threshold` | 0.7 | Similarity threshold for duplicates (0.0-1.0) |
| `ignore_patterns` | [] | Glob patterns to exclude from checks |

## Triggers

- `check duplicates` / `find duplicate docs`
- `broken links` / `broken references`
- `validate links` / `link check`
- `censor`

## Integration

Loaded by Chronos as part of `minimal`, `standard`, and `full` presets.