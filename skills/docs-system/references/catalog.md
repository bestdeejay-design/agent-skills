# Document Catalog — what files exist, why, when

The complete catalog of every document in the docs-system. Each entry answers:
**what** (file), **why** (purpose), **when** (fill order phase, see `order.md`),
**level** (which level requires it).

Legend: `L1` = minimal core · `L2` = canonical · `L3·<profile>` = required by that
profile · `+` = recommended.

---

## Root documents

| File | Purpose | Phase | Level |
|------|---------|:-----:|-------|
| `README.md` | Project overview: what it is, stack, status, quick start, structure | 1 (draft) → 10 (final) | **all** |
| `ENTRY.md` | **Entry point**: "start here", navigation table "topic → file", onboarding checklist | 9 | L2+ (recommended L1) |
| `AGENT.md` | Runbook for the autonomous build agent: phases, rules, Definition of Done, commit gate | 8 | L2+ |
| `DELIVERY.md` | Delivery gate: how to build/run/verify, what's included, what's NOT | 8 | L2+ |
| `LICENSE` | Legal license | 1 | all (public) |
| `CONTRIBUTING.md` | How to contribute (EN) | 9 | L2+ (public) |
| `CODE_OF_CONDUCT.md` | Community guidelines | 9 | L2+ (public) |
| `SECURITY.md` | Security policy: supported versions, reporting, sensitive areas | 9 | L2+ (public) |

## docs/ — project documentation

| File | Purpose | Phase | Level |
|------|---------|:-----:|-------|
| `docs/REFERENCE.md` | **The map.** Single documentation map: purpose/structure/facts/links for EVERY doc, hierarchy of truth, known drifts. Written **last**. | 10 | L2+ |
| `docs/ARCHITECTURE.md` | Overall architecture: components, communication, data flows, tech stack | 2 (draft) → 6 (final) | **all** |
| `docs/ADR/ADR-000.md` | Architecture Decision Records: one per significant decision | 2 (ongoing) | L2+ (L1: single `docs/DECISIONS.md`) |
| `docs/FEATURES.md` | Functional requirements catalog: every feature/module, ✅/📋 status | 4 | L2+ |
| `docs/SAGA.md` | Cross-module scenarios (choreography, events, compensation, idempotency) | 5 | L3·microservices (L2 if >1 module) |
| `docs/TEST_CASES.md` | Test cases (Gherkin-style) + coverage matrix | 6 | L2+ |
| `docs/DEV_GUIDE.md` | Local dev: prerequisites, run, env, migrations, debugging, add-a-module steps | 7 | L2+ (L1: keep in README) |
| `docs/IMPROVEMENTS.md` | Known issues / doc-vs-fact drift + prioritized fix plan | 8 (ongoing) | L2+ |
| `docs/TROUBLESHOOTING.md` | Runtime error diagnostics (E1…En) + startup checklist | 8 (ongoing) | L2+ |
| `docs/BACKLOG.md` | Ideas, deferred features, priorities | 1 (ongoing) | L2+ |
| `docs/REVIEW.md` | Doc audit: found problems, resolutions, per-service status matrix | 10 | L2+ |
| `docs/STATUS.md` | (L1 alternative to REVIEW) What's done / in progress / known limitations | 10 | L1 |

## contracts/ — machine truth (L3·microservices / API-first)

| File | Purpose | Phase | Level |
|------|---------|:-----:|-------|
| `contracts/openapi/*.yaml` | Per-service OpenAPI specs — **the HTTP truth** | 3 (**before code**) | L3·microservices |
| `contracts/asyncapi/events.yaml` | Event catalog — **the event truth** | 3 | L3·microservices |
| `contracts/test/` | Contract-conformance test fixtures/helpers | 6 | L3·microservices |

## Per-module (services/<name>/) — L3·microservices

| File | Purpose | Phase | Level |
|------|---------|:-----:|-------|
| `src/routes/index.ts` | Fastify typed routes (mirror the OpenAPI contract) | 3–4 | L3·microservices |
| `src/events/publish.ts` + `subscribe.ts` | Event emit + saga handlers | 4–5 | L3·microservices |
| `src/db/schema.ts` + `migrations/` | Drizzle schema + SQL migrations | 4 | L3·microservices |
| `test/health.test.ts`, `contract.test.ts`, `integration.*.test.ts` | Per-service tests | 6 | L3·microservices |

## scripts/ — generators (reproducibility)

| File | Purpose | Phase | Level |
|------|---------|:-----:|-------|
| `scaffold-*.mjs` | Scaffold new modules/services from template | 2+ | L2+ |
| `gen-*.mjs` | Generate contracts/schemas/routes/tests from truth | 3–6 | L2+ |

---

## Where things live (canonical layout)

```
<repo>/
├── README.md  ENTRY.md  AGENT.md  DELIVERY.md        # root (L2+; README always)
├── LICENSE  CONTRIBUTING.md  CODE_OF_CONDUCT.md  SECURITY.md
├── docs/
│   ├── REFERENCE.md  ARCHITECTURE.md  FEATURES.md  SAGA.md
│   ├── TEST_CASES.md  DEV_GUIDE.md  IMPROVEMENTS.md
│   ├── TROUBLESHOOTING.md  BACKLOG.md  REVIEW.md  STATUS.md (L1)
│   └── ADR/ADR-001.md … ADR-NNN.md
├── contracts/                 # L3·microservices
│   ├── openapi/<svc>.yaml
│   ├── asyncapi/events.yaml
│   └── test/
├── services/<name>/           # L3·microservices
├── scripts/                   # generators
└── template-module/           # scaffold source
```

> **The map rule:** every document in this catalog that you create must get a card in
> `docs/REFERENCE.md` (purpose → structure → key facts → links). That's how the map
> stays complete. See `templates/REFERENCE.tmpl`.
