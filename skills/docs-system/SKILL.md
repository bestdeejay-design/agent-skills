---
name: docs-system
description: "Guide for an AI agent on composing product and project documentation and its composition: what documents exist (catalog), why, and in what order to create them (fill order). Two branches — product docs (VISION/PRD/ROADMAP/FEATURES) and project docs (ARCHITECTURE/ADR/TEST_CASES/REFERENCE/map) — with templates and a completeness checklist. Use when starting a new repo, creating documentation from scratch, auditing existing docs, or when a project needs a documentation map. Triggers: 'документация', 'набор документации', 'каталог документов', 'docs catalog', 'documentation structure', 'из идеи в документацию', 'полная документация', 'docs for new project', 'documentation plan', 'системная документация'."
---

# docs-system — Guide: product & project documentation

A guide for an AI agent (and a human) on **how to compose product and project
documentation and what belongs in it**. It answers two questions:

1. **What documents exist** — the catalog, split into product docs (why/what)
   and project docs (how).
2. **In what order to create them** — the fill order, from an idea to a complete,
   consistent set.

> **RU:** это гайд, как правильно составлять продуктовую и проектную документацию
> и её состав: какие документы существуют (каталог) и в каком порядке их создавать
> (порядок заполнения).

## Why this skill exists

Most projects either have no docs (agents and humans get lost) or have *lots* of docs
with no system (contradictions, drift, nobody knows which file is authoritative).
This skill codifies the *system* that makes documentation useful:

- a **catalog** — what files exist, why, when they are created;
- a **fill order** — the phases from idea to a complete set;
- **templates** — copy-paste skeletons for every document;
- a **completeness checklist** — proof that nothing was forgotten;
- **levels** (optional reference) — right-sizing for small vs large systems.

The reference model behind this skill is the example monorepo (`examples/example-monorepo/`):
a microservices project whose docs stayed consistent for hundreds of commits
because every file had a purpose, there was an explicit hierarchy of truth, a
single entry point (`ENTRY.md`), a documentation map (`REFERENCE.md`), and a
delivery gate.

## When to use

- Starting a new repository / project — generate the docs skeleton **before** or
  **in parallel with** the first code.
- Turning a raw idea into a full documentation set.
- Auditing an existing project with missing/chaotic documentation.
- Adding a feature or service and needing to know *which docs to update*.

## Two branches of documentation

### 1. Product docs — «why» and «what»

| Document | Answers | When |
|----------|---------|------|
| `docs/VISION.md` | Why does the product exist? For whom? | First — stays stable |
| `docs/PRD.md` | What exactly are we building? (requirements, priorities, metrics) | After VISION |
| `docs/ROADMAP.md` | What ships when? (milestones + proof) | Phase 2+, each milestone |
| `docs/FEATURES.md` | Feature catalog + status (✅/📋) | Phase 4, kept current |

> **RU:** продуктовая ветка отвечает «зачем» и «что»: видение → требования → план →
> каталог фич. Подробности — в `references/product-docs.md`.

### 2. Project docs — «how»

| Document | Answers | When |
|----------|---------|------|
| `README.md` | What is the project, how to run, status | 1 → 10 (final) |
| `ENTRY.md` (L2+) | Where to start; navigation «topic → file» | 9 |
| `docs/ARCHITECTURE.md` | Components, communication, data flows | 2 (draft) → 6 (final) |
| `docs/ADR/*` (L1: `DECISIONS.md`) | Architecture decision records | 2, ongoing |
| `docs/SAGA.md` (multi-module) | Cross-module scenarios, compensation | 5 |
| `docs/TEST_CASES.md` (L1: `TEST_PLAN.md`) | How correctness is proven | 6 |
| `docs/DEV_GUIDE.md` (L2+) | Local dev: run, env, debug, add-a-module | 7 |
| `docs/TROUBLESHOOTING.md` (L2+) | Errors E1…En + startup checklist | 8 |
| `docs/IMPROVEMENTS.md` (L2+) | Known issues, doc-vs-fact drift, fix plan | 8 |
| `docs/BACKLOG.md` (L2+) | Ideas, deferred features | 1, ongoing |
| `docs/REVIEW.md` / `STATUS.md` | Doc audit / state at delivery | 10 |
| `docs/REFERENCE.md` (L2+) | **The map** — written **last** | 10 |
| `contracts/openapi/*`, `contracts/asyncapi/` | Machine truth, **before code** | 3 |
| `AGENT.md`, `DELIVERY.md` (L2+) | Agent runbook + delivery gate | 8 |

> **RU:** проектная ветка отвечает «как»: архитектура, решения, контракты, тесты,
> гайды. Подробности — в `references/project-docs.md`.

## How to use this skill (TL;DR)

1. **Separate product from project.** Start with VISION/PRD («why/what»), never
   jump into architecture («how») first.
2. **Follow the fill order** (`references/order.md`): phases 1→10 from idea to
   complete set. Two golden rules: **contracts before code**, **map last**.
3. **Use the templates** (`templates/product/`, `templates/project/`): copy the
   skeleton, fill the sections.
4. **Finish with the completeness checklist** (`references/completeness.md`) —
   prove nothing was forgotten.
5. **Size the effort** (`references/levels.md`, optional): L1 minimal for small
   projects, L2 canonical, L3 hard per-profile layouts for large systems.
6. If auditing an existing project: first map what exists, then fill gaps in
   catalog order (see `references/project-docs.md` → map rule).

## Two golden rules (from example monorepo)

1. **Machine truth before code.** Contracts/OpenAPI/events (anything that *is* the
   interface) are written **before** implementation. Code implements the contract,
   not the other way around.
2. **The map comes last.** `REFERENCE.md` (the documentation map) is written last,
   because it describes everything above it. Writing it forces you to verify the
   whole set is consistent.

> **RU:** два золотых правила: контракты — до кода; карта документации — последней.

## References index

| File | Purpose |
|------|---------|
| `references/product-docs.md` | Product branch: VISION/PRD/ROADMAP/FEATURES — why, order, links |
| `references/project-docs.md` | Project branch: engineering docs, contracts, the map rule |
| `references/order.md` | Fill order: phases from idea to complete set |
| `references/completeness.md` | Checklist: «nothing forgotten» before delivery |
| `references/levels.md` | (Reference) L1/L2/L3 + profile layouts for large systems |
| `templates/product/*.tmpl` | Skeletons: VISION, PRD, ROADMAP |
| `templates/project/*.tmpl` | Skeletons: README, ARCHITECTURE, ADR, SAGA, TEST_CASES, DEV_GUIDE, IMPROVEMENTS, TROUBLESHOOTING, BACKLOG, REVIEW, STATUS, REFERENCE, ENTRY, FEATURES |
| `examples/example-monorepo/` | Real-world canonical reference (example monorepo) |
