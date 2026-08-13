---
name: docs-project
description: "Project (engineering) documentation branch — the 'how': README, ENTRY, AGENT/DELIVERY runbooks, and docs/ (REFERENCE map, ARCHITECTURE, ADR, SAGA, TEST_CASES, DEV_GUIDE, IMPROVEMENTS, TROUBLESHOOTING, BACKLOG, REVIEW, STATUS) plus contracts/ (OpenAPI/AsyncAPI — machine truth written BEFORE code). The map rule: every doc gets a card in REFERENCE.md. Full catalog + checklist in references/project-docs.md. Triggers: 'проектная документация', 'архитектура документация', 'adr', 'engineering docs', 'документация разработчика', 'контракты openapi', 'project docs', 'инженерная документация'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.0.0"
compatibility: "No scripts — template-driven authoring"
---

# Docs Project — engineering documentation («how»)

Use this skill to write the **engineering** documents: architecture, decisions
(ADR), contracts, dev guides, tests, and the documentation map. Assumes the
product docs exist (`docs-product`: VISION/PRD/ROADMAP/FEATURES).

## When to use

- A project needs its engineering docs: README, ENTRY, ARCHITECTURE, ADR, tests.
- User asks for "проектная документация", "архитектура документация", "adr",
  "инженерная документация", "контракты openapi", "engineering docs".
- Contracts (OpenAPI/AsyncAPI) must be written **before** code.

## Do NOT use

- For product docs (VISION/PRD/ROADMAP/FEATURES) — that is `docs-product`.
- For the meta-guide (phases, levels L1/L2/L3, completeness checklist) — `docs-system`.

## Root documents

| File | Purpose | Phase | Template |
|------|---------|:-----:|----------|
| `README.md` | Overview: what it is, stack, status, quick start, structure | 1 → 10 | `templates/project/README.tmpl` |
| `ENTRY.md` | Entry point: "start here", navigation "topic → file", onboarding checklist | 9 | `templates/project/ENTRY.tmpl` |
| `AGENT.md` | Runbook for the autonomous build agent: phases, rules, DoD, commit gate | 8 | — |
| `DELIVERY.md` | Delivery gate: build/run/verify, what's in, what's NOT | 8 | — |
| Legal/community | LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY | 1/9 | — |

## docs/ — engineering documents

| File | Purpose | Phase | Template |
|------|---------|:-----:|----------|
| `docs/REFERENCE.md` | **The map.** Card for EVERY doc: purpose/structure/facts/links, hierarchy of truth, drift table. Written **last**. | 10 | `templates/project/REFERENCE.tmpl` |
| `docs/ARCHITECTURE.md` | Components, communication, data flows, tech stack | 2 → 6 | `templates/project/ARCHITECTURE.tmpl` |
| `docs/ADR/ADR-000.md` | Architecture Decision Records — one per significant decision | 2 (ongoing) | `templates/project/ADR-000.tmpl` |
| `docs/SAGA.md` | Cross-module scenarios (choreography, events, compensation, idempotency) | 5 | `templates/project/SAGA.tmpl` |
| `docs/TEST_CASES.md` | Test cases (Gherkin-style) + coverage matrix | 6 | `templates/project/TEST_CASES.tmpl` |
| `docs/DEV_GUIDE.md` | Local dev: prerequisites, run, env, migrations, debugging | 7 | `templates/project/DEV_GUIDE.tmpl` |
| `docs/IMPROVEMENTS.md` | Known issues / doc-vs-fact drift + prioritized fix plan | 8 | `templates/project/IMPROVEMENTS.tmpl` |
| `docs/TROUBLESHOOTING.md` | Runtime error diagnostics (E1…En) + startup checklist | 8 | `templates/project/TROUBLESHOOTING.tmpl` |
| `docs/BACKLOG.md` | Ideas, deferred features, priorities | 1 | `templates/project/BACKLOG.tmpl` |
| `docs/REVIEW.md` | Doc audit: problems, resolutions, per-service status | 10 | `templates/project/REVIEW.tmpl` |
| `docs/STATUS.md` | L1 alternative to REVIEW: done / in progress / limitations | 10 | `templates/project/STATUS.tmpl` |

## contracts/ — machine truth (API-first / microservices)

| Path | Purpose | When |
|------|---------|:----:|
| `contracts/openapi/*.yaml` | Per-service OpenAPI specs — **the HTTP truth** | **before code** |
| `contracts/asyncapi/events.yaml` | Event catalog — **the event truth** | before code |
| `contracts/test/` | Contract-conformance test fixtures | with tests |

> Contracts are written BEFORE code. The code implements the contract, not the
> other way around — «machine truth before code».

## The map rule

Every document that exists gets a card in `docs/REFERENCE.md`
(purpose → structure → key facts → links). Written **last**, maintained on every
change: *touch a doc → update its card*.

## Checklist (project side)

- [ ] One entry point exists (`ENTRY.md`) and routes "topic → file".
- [ ] Every doc has a card in `REFERENCE.md` (including REFERENCE itself).
- [ ] Hierarchy of truth declared (which doc wins on conflict).
- [ ] Drift table (doc-vs-fact) populated — no silent inconsistencies.
- [ ] Contracts exist **before** code for every API/event (API-first projects).
- [ ] `DELIVERY.md` states how to build/verify/what's in/what's NOT.

> Rule: engineering docs answer «how»; the map (`REFERENCE.md`) is written last
> because it describes everything above it.
