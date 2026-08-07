# Fill Order — from idea to complete documentation set

The order in which documents are created matters. It is the difference between a
folder of files and a coherent, drivable system. Follow these phases **in order**.
Later phases often reveal gaps in earlier ones — that's normal and healthy.

> Principle: **machine truth before code, the map last.** Contracts/OpenAPI come
> before implementation; `REFERENCE.md` is written last because it describes
> everything above it.
>
> Each phase lists: what to create/update · why · which level applies.

---

## Phase 1 — Vision & container

**Goal:** title the thing, capture the idea so nothing is lost.

- `README.md` — 1 paragraph: what it is, who it's for, 3 bullets of core value.
  (Expand in Phase 10.)
- `BACKLOG.md` (L2+) — first entry: the idea itself, priority, open questions.
- `LICENSE` — pick it early if the repo is public.

> If the idea is not yet clear enough to write a paragraph — do **not** start code.
> Clarify first.

## Phase 2 — Decisions & architecture draft

**Goal:** capture the *shape* before implementation: what components, how they talk,
who is authoritative.

- `docs/ADR/ADR-001.md` (L2+) or `docs/DECISIONS.md` (L1) — the first architecture
  decision (repo layout, mono/multi, tech stack, module boundaries). Every
  significant decision from now on gets its own ADR.
- `docs/ARCHITECTURE.md` — draft: components, communication principles (sync/async),
  data ownership. It will be revised as decisions land.
- `docs/ENTRY.md` (L2+) — draft the initial "start here" map: topic → file.

> ADR discipline: a decision is authoritative the moment it's written. Later ADRs can
> supersede earlier ones (like ADR-007 superseding 002–006 in pmOS) — mark this
> explicitly in the ADR.

## Phase 3 — Machine truth (before code)

**Goal:** define the *interface* as the source of truth. Code will implement it, not
invent it.

- **L3·microservices**: `contracts/openapi/*.yaml` per service + `contracts/asyncapi/
  events.yaml`. Every endpoint/event exists here **before** any route is written.
- **API-first monolith/library** (L3): same idea — the public API contract file.
- This phase is what prevents "agent invented a route no one planned".

> Golden rule: code reproduces contract with conformance tests; contract is *never*
> derived from code after the fact.

## Phase 4 — Features & modules

**Goal:** enumerate what exists / is planned, and give each a status.

- `docs/FEATURES.md` (L2+): catalog every feature/module, ✅ (done) / 📋 (planned).
- For L3·microservices: scaffold each service (`scripts/scaffold-*.mjs`), lay in the
  typed routes (mirroring the contract) + db schema + migrations.

## Phase 5 — Cross-module behavior

**Goal:** capture how modules cooperate — events, sagas, compensation, idempotency.

- `docs/SAGA.md` (L3·microservices, or L2 with >1 module): each cross-module scenario —
  trigger event, steps, compensation, retry, DLQ.

## Phase 6 — Verification design

**Goal:** decide how correctness is proven — before you say "it works".

- `docs/TEST_CASES.md` (L2+): Gherkin-style cases per module + coverage matrix.
- Contract-conformance tests (L3·microservices): wire `contracts/test/` helpers.
- Per-module tests: health, contract, integration.

## Phase 7 — How to run it

**Goal:** an outsider (or a fresh agent) can bring the thing up.

- `docs/DEV_GUIDE.md` (L2+): prerequisites, quick start, env vars, migrations,
  debugging, "add a module in N steps". (L1: keep this inside README's quick-start.)
- Update README "Quick start" to the real working commands.

## Phase 8 — Operating reality

**Goal:** capture what running it actually taught you. This is where drift starts to
appear — get it on paper.

- `docs/TROUBLESHOOTING.md` (L2+): runtime error diagnostics (E1…En) + startup checklist.
- `docs/IMPROVEMENTS.md` (L2+): known issues, doc-vs-fact drift, prioritized fix plan.
- `AGENT.md`, `DELIVERY.md` (L2+): runbook + delivery gate (build/verify/definition of done).

## Phase 9 — The entry point & community

**Goal:** make the docs navigable and the repo publishable.

- `ENTRY.md` (L2+): finish the navigation table ("topic → file") + onboarding checklist.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` (public repos).
- Update README further as a final overview (but keep the truth matrix in REFERENCE).

## Phase 10 — The map & completeness (LAST)

**Goal:** prove nothing is forgotten and kill inconsistencies.

- `docs/REFERENCE.md` (L2+): **written last.** The map of every doc (purpose →
  structure → key facts → links), the hierarchy of truth, the drift table.
- `docs/REVIEW.md` (L2+) / `docs/STATUS.md` (L1): what's done, what's not, remaining
  risks, per-module status.
- Run `references/completeness.md` — every item must pass. Any failure → create/fix
  the missing doc, then update REFERENCE with its card.

---

## Companion rules

- **Update, don't recreate.** Every phase also updates the docs of previous phases if
  new facts change them.
- **One authoritative home per fact.** If a fact exists in two docs, one is the
  source and the other links to it (see hierarchy of truth in `REFERENCE.md`).
- **Keep the map current.** Touch any `.md` → touch its card in `REFERENCE.md`.
- **Small, growing pieces.** A doc that is "fine at L1 and grows to L2" is better
  than a premature full catalog. Grow levels when the project outgrows them.