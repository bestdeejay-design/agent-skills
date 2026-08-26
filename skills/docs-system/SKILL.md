---
name: docs-system
description: "Meta-guide + router for documentation: the two branches (docs-product for 'why/what', docs-project for 'how'), the phase order, completeness levels L1/L2/L3, and the completeness checklist. Load a branch directly when the task is clearly product or engineering; load this skill for the big picture, ordering and completeness gates. Triggers: 'документация', 'набор документации', 'каталог документов', 'документация структура', 'полная документация', 'docs catalog', 'documentation structure', 'какую документацию писать'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "2.0.0"
compatibility: "No scripts — guide + router"
when_to_use: "Use when user asks about the documentation system as a whole: 'документация', 'набор документации', 'каталог документов', 'docs catalog', 'documentation structure', 'какую документацию писать', 'полная документация'. Examples: 'what docs should this project have', 'какую документацию написать для стартапа'."
---

# Docs System — meta-guide & router

> **This skill is now the meta-guide.** The two branches live in focused skills:
> load them directly. Use this skill for the big picture: which docs to write,
> in which order, and how complete the set must be.

## Two branches of documentation

| Branch | Answers | Skill |
|---|---|---|
| **Product docs** — «why» and «what» | VISION → PRD → ROADMAP → FEATURES | `docs-product` |
| **Project docs** — «how» | README/ENTRY/ARCHITECTURE/ADR/contracts/tests + REFERENCE map | `docs-project` |

Rule: product docs answer «why» and «what»; engineering docs answer «how».
If a doc has no reader and no question it answers — it does not belong.

## When to use this skill (router)

- The task is about the documentation SYSTEM as a whole: what to write, in what
  order, how complete.
- The phases / levels / completeness gates need to be applied.
- The task is clearly product OR engineering → load the branch directly instead.

## Order and levels

- **Phase order** (when to write each doc): `references/order.md`.
- **Levels L1/L2/L3** (how deep a doc set must be for the system size):
  `references/levels.md`.
- **Completeness checklist** (what a complete doc set looks like):
  `references/completeness.md`.

## Golden rules

- Nothing is written "from the end": VISION → PRD → ROADMAP → FEATURES, then
  engineering docs.
- Contracts (OpenAPI/AsyncAPI) are written BEFORE code.
- The map (`REFERENCE.md`) is written last — it describes everything above it.
- Example monorepo that follows all rules: `examples/example-monorepo/`.
- Skill roadmap: `ROADMAP.md`.

## Removal plan

Keep as the meta-guide (not deprecated — it still carries order/levels/
completeness). The two branches are the focused entry points.
