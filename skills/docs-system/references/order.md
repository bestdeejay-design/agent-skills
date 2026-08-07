# Fill Order — from idea to complete documentation set

The order in which documents are created matters. It is the difference between a
folder of files and a coherent, drivable system. Follow these phases **in order**.
Later phases often reveal gaps in earlier ones — that's normal and healthy.

> **RU:** порядок создания файлов важен: сначала продуктовая документация, потом
> контракты, карта — последней. Поздние фазы вскрывают дыры в ранних — это норма.

## Golden rules

1. **Product before engineering** — VISION/PRD come before ARCHITECTURE. You
   cannot design «how» before you know «why» and «what».
2. **Machine truth before code** — contracts (OpenAPI/AsyncAPI) are written
   **before** implementation, not reverse-engineered from it.
3. **The map comes last** — `docs/REFERENCE.md` is written last, because it
   describes everything above it. Writing it last forces a full verification.

## Phases

**Phase 1 — Product foundation**
- `docs/VISION.md` — 1 paragraph: what it is, who it's for, problem solved,
  out-of-scope. If you can't write this, **stop**: clarify the idea first.
- `docs/PRD.md` (draft) — goals/non-goals, top stories, success metrics.
- `docs/BACKLOG.md` (L2+) — ideas, deferred features, priorities.

**Phase 2 — Plan & architecture (drafts)**
- `docs/ROADMAP.md` — milestones by value (not effort), each with a proof.
- `docs/ARCHITECTURE.md` (draft) — components, communication, data ownership.
- ADR process starts: `docs/ADR/ADR-001.md` (L2+) or `docs/DECISIONS.md` (L1).

**Phase 3 — Contracts FIRST (API-first / L3)**
- `contracts/openapi/*.yaml`, `contracts/asyncapi/events.yaml` **before any route
  is written**. Prevents «the agent invented a route nobody planned».

**Phase 4 — Feature catalog**
- `docs/FEATURES.md` (L2+): ✅/📋 per feature/module.
- L3·microservices: scaffold services; types mirror the contracts.

**Phase 5 — Cross-module behavior (if >1 module)**
- `docs/SAGA.md`: trigger, steps, compensation, retries, DLQ.

**Phase 6 — Tests**
- `docs/TEST_CASES.md` (L2+) + contract-conformance tests.
- L1: a `TEST_PLAN.md` is allowed; grows to L2 TEST_CASES later.

**Phase 7 — Dev guide**
- `docs/DEV_GUIDE.md` (L2+): prerequisites, run, env, migrations, add-a-module.
- README «Quick start» must list real commands.

**Phase 8 — What running taught you**
- `docs/TROUBLESHOOTING.md` (L2+): errors E1…En + startup checklist.
- `docs/IMPROVEMENTS.md` (L2+): known issues, doc-vs-fact drift, fix plan.
- `AGENT.md`, `DELIVERY.md` (L2+): agent runbook + delivery gate.

**Phase 9 — Entry point + community (public repos)**
- `ENTRY.md` (L2+): navigation «topic → file» + onboarding checklist.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.

**Phase 10 — The map (LAST)**
- `docs/REFERENCE.md` — written **last**: card for every doc, hierarchy of truth,
  drift table. Then run `references/completeness.md` until it passes.

## Rules that hold throughout

- **Update, don't recreate.** Each phase updates earlier docs.
- **One authoritative home per fact.** On conflict — the hierarchy of truth decides.
- **Touch a doc → touch its card.** Any edit implies `REFERENCE.md` maintenance in
  the drift table.
- **Smallest adequate level.** L1 that can grow is better than a premature full
  catalog. Growth rules live in `references/levels.md`.