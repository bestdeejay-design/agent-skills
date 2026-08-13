# Project documentation — catalog

> **What this is:** the **engineering** documents — the «how» of the project:
> architecture, decisions, contracts, dev guides, tests, and the map.
> Assumes the product docs exist (VISION/PRD/ROADMAP — see `product-docs.md`).
>
> **RU:** проектные (инженерные) документы — «как»: архитектура, решения (ADR),
> контракты, гайды разработчика, тесты, карта документации. Опираются на
> продуктовые документы.

## Root documents

| File | Purpose | Phase | Template |
|------|---------|:-----:|----------|
| `README.md` | Project overview: what it is, stack, status, quick start, structure | 1 (draft) → 10 (final) | `templates/project/README.tmpl` |
| `ENTRY.md` | **Entry point**: "start here", navigation table "topic → file", onboarding checklist | 9 | `templates/project/ENTRY.tmpl` |
| `AGENT.md` | Runbook for the autonomous build agent: phases, rules, Definition of Done, commit gate | 8 | — |
| `DELIVERY.md` | Delivery gate: how to build/run/verify, what's included, what's NOT | 8 | — |
| `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` | Legal + community docs | 1/9 | — |

## docs/ — engineering documents

| File | Purpose | Phase | Template |
|------|---------|:-----:|----------|
| `docs/REFERENCE.md` | **The map.** Purpose/structure/facts/links for EVERY doc, hierarchy of truth, drift table. Written **last**. | 10 | `templates/project/REFERENCE.tmpl` |
| `docs/ARCHITECTURE.md` | Overall architecture: components, communication, data flows, tech stack | 2 (draft) → 6 (final) | `templates/project/ARCHITECTURE.tmpl` |
| `docs/ADR/ADR-000.md` | Architecture Decision Records — one per significant decision (L1: single `docs/DECISIONS.md`) | 2 (ongoing) | `templates/project/ADR-000.tmpl` |
| `docs/SAGA.md` | Cross-module scenarios (choreography, events, compensation, idempotency) | 5 | `templates/project/SAGA.tmpl` |
| `docs/TEST_CASES.md` | Test cases (Gherkin-style) + coverage matrix | 6 | `templates/project/TEST_CASES.tmpl` |
| `docs/DEV_GUIDE.md` | Local dev: prerequisites, run, env, migrations, debugging, add-a-module steps | 7 | `templates/project/DEV_GUIDE.tmpl` |
| `docs/IMPROVEMENTS.md` | Known issues / doc-vs-fact drift + prioritized fix plan | 8 (ongoing) | `templates/project/IMPROVEMENTS.tmpl` |
| `docs/TROUBLESHOOTING.md` | Runtime error diagnostics (E1…En) + startup checklist | 8 (ongoing) | `templates/project/TROUBLESHOOTING.tmpl` |
| `docs/BACKLOG.md` | Ideas, deferred features, priorities | 1 (ongoing) | `templates/project/BACKLOG.tmpl` |
| `docs/REVIEW.md` | Doc audit: found problems, resolutions, per-service status matrix | 10 | `templates/project/REVIEW.tmpl` |
| `docs/STATUS.md` | (L1 alternative to REVIEW) What's done / in progress / known limitations | 10 | `templates/project/STATUS.tmpl` |

## contracts/ — machine truth (API-first / microservices)

| Path | Purpose | Phase | Template |
|------|---------|:-----:|----------|
| `contracts/openapi/*.yaml` | Per-service OpenAPI specs — **the HTTP truth** | 3 (**before code**) | — |
| `contracts/asyncapi/events.yaml` | Event catalog — **the event truth** | 3 | — |
| `contracts/test/` | Contract-conformance test fixtures/helpers | 6 | — |

> **RU:** контракты (OpenAPI/AsyncAPI) пишутся ДО кода. Код реализует контракт,
> а не наоборот. Это правило «machine truth before code».

## The map rule

> Every document that exists must get a card in `docs/REFERENCE.md`
> (purpose → structure → key facts → links). Written **last**, maintained on every
> change: *touch a doc → update its card*.

## Checklist (project side)

- [ ] One entry point exists (`ENTRY.md`) and routes "topic → file".
- [ ] Every doc has a card in `REFERENCE.md` (including REFERENCE itself).
- [ ] Hierarchy of truth declared (which doc wins on conflict).
- [ ] Drift table (doc-vs-fact) populated — no silent inconsistencies.
- [ ] Contracts exist **before** code for every API/event (API-first projects).
- [ ] `DELIVERY.md` states how to build/verify/what's in/what's NOT.

---
> **Rule:** engineering docs answer «how»; the map (`REFERENCE.md`) is the last
> document written because it describes everything above it.
> **RU:** инженерная документация отвечает «как»; карта (REFERENCE) пишется
> последней, потому что описывает всё, что выше неё.