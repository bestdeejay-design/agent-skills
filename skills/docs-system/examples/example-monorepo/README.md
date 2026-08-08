# Example monorepo — real-world canonical reference

> **What this is:** a condensed picture of an **example monorepo** — the shape this
> skill's L2/L3·microservices canonical layout was derived from. Use it as a concrete
> "this is what the system looks like when fully applied" reference. Not a copy-paste
> of every file — the patterns & rationale. Replace `<owner>/<repo>` and all concrete
> numbers with your own project's.

> **Source repo:** `<owner>/<repo>` — 17 microservices (16 CRUD +
> ops/DLQ panel) + React SPA, TypeScript strict, Fastify, Postgres, NATS JetStream.
> Status at extraction: typecheck green (20 packages), unit+integration green, contract
> 17/17, E2E (Playwright), **~4,100 docs lines + ~11,100 contract lines ≈ 15,200**.

## The two "magic" docs (why it stays consistent)

### `ENTRY.md` — the entry point
> "Start here. This is the routing card: which file answers which question." A table
> of **which file is the truth for what**, plus a first-day onboarding checklist and
> where-to-read-next. A fresh agent/dev lands here and immediately knows where to look.
>
> This is what turns a folder of files into a *system the agent can drive*.

### `docs/REFERENCE.md` — the map
> The permanent map of the whole documentation repo: per-doc **purpose → structure →
> key facts → links**, the hierarchy of truth, and the **drift table** (doc-vs-fact).
> Written **last** (it's the map of everything above), then maintained on every change.
> Its mantra: *touch a doc → update its card*.

## Real directory layout (abridged, ch `##` marks the docs-system files)

```
example-monorepo/
├── README.md  README.ru.md        # EN/RU overview, structure, status, quick start
├── ENTRY.md                       # ★ entry point — "start here", topic→file routing
├── AGENT.md                       # runbook for the auto-build agent (phases, DoD, commit gate)
├── DELIVERY.md                    # delivery gate: build/run/verify, what's IN/NOT
├── CONTRIBUTING.md CODE_OF_CONDUCT.md SECURITY.md LICENSE   # community/legal
│
├── docs/
│   ├── ★ REFERENCE.md             # ★ THE MAP — all docs carded + hierarchy + drift table
│   ├── ARCHITECTURE.md            # components, comms (sync/async), stack, events, safety
│   ├── FEATURES.md                # full module/feature catalog + ✅/📋 counts (87/16)
│   ├── SAGA.md                    # 5 cross-service choreographies + compensation matrix
│   ├── REVIEW.md                  # doc audit + per-service status matrix (status RESOLVED)
│   ├── TEST_CASES.md             # Gherkin cases per service + E2E + coverage matrix
│   ├── DEV_GUIDE.md               # local env, run, migrations, add-a-service (10 steps)
│   ├── IMPROVEMENTS.md            # known runtime issues + prioritized fix plan (§2/§6)
│   ├── TROUBLESHOOTING.md         # E1–E5 launch diagnostics + startup checklist
│   ├── BACKLOG.md                 # ideas / deferred UI (P1) / backend (P2–P3)
│   └── ADR/
│       ├── ADR-001…006.md         # recordings (ADR-002 Fastify, 004 Postgres isolation, 005 OpenAPI, 006 bus)
│       └── ADR-007.md             # ★ CANON — consolidated conventions, supersedes 002–006
│
├── contracts/                     # ★ MACHINE TRUTH (contract-first)
│   ├── openapi/<svc>.yaml         # 17 specs, conformance 17/17
│   ├── asyncapi/events.yaml       # event catalog (+x-implemented-wire-events = actually published)
│   └── test/helper.ts             # contract test helpers
│
├── services/<name>/              # ★ implementation
│   ├── src/app.ts  index.ts       # Fastify app, bootstrap
│   ├── src/db/schema.ts + migrations/   # schema + SQL
│   ├── src/events/publish|subscribe.ts  # emit/sagas
│   ├── src/routes/index.ts        # typed routes mirroring the contract
│   ├── src/lib/  src/plugins/     # business logic, correlationId/health/metrics
│   └── test/ health|contract|integration → sagas
│
├── scripts/                      # ★ reproducibility
│   ├── scaffold-services.mjs     # scaffold a new service from template
│   ├── gen-openapi.mjs  gen-schemas.mjs  gen-routes.mjs
│   ├── gen-contract-tests.mjs  gen-semantics.mjs
│   └── (all regenerate code/contracts from truth)
│
├── platform/
│   ├── docker/{docker-compose.yml, nginx.conf}   # infra (core/all profiles) + gateway
│   ├── shared-types/  @scope/shared
│   └── event-bus/     @scope/event-bus (NATS, DLQ)
│
└── template-service/            # the ask for a NEW service (excluded from build)
```

## What the reference model proves

| docs-system principle | How the example monorepo shows it |
|------------------------|-------------------|
| Single entry point | `ENTRY.md` — a real "start here" router |
| The map exists & is maintained | `docs/REFERENCE.md` — purpose/structure/facts/links for **every** doc + hierarchy + drift |
| Machine truth before code | `contracts/openapi/*.yaml` conformance-tested 17/17 before/constantly against routes |
| Event truth in one place | `contracts/asyncapi/events.yaml` + `x-implemented-wire-events` (only what ships) |
| Canon ADR superseds older | `ADR-007` marks 002–006 `Superseded`; table in REFERENCE §3.3 |
| Drift is visible, not silent | REFERENCE §5 + IMPROVEMENTS — every doc-vs-fact gap tracked |
| Reproducibility | `scripts/*.mjs` generate contracts/schemas/routes/tests |
| Cross-module scenarios | `SAGA.md` + integration tests against real storage+bus |
| Delivery gate | `DELIVERY.md` + `AGENT.md` §5/§7; commit-gate enforces green checks |
| Right-scaled | README.ru is a short mirror; detail lives in docs/ — not a wall of prose |