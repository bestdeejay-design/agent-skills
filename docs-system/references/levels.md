# Levels & Profiles — right-sizing the documentation

The skill is one process (the fill order) applied at the right **level** of
completeness. Pick the **smallest level that fits**; grow it as the project outgrows
it. All levels share the same engine (order.md) — the difference is *how many
documents* exist and *how detailed* templates are.

---

## L1 — Minimal core (any project, from day one)

**Rule:** every project, no matter how small, gets a working documentation spine, so
the agent and humans are never lost.

Docs:
| File | Why |
|------|-----|
| `README.md` | What it is, how to run, status (1 page) |
| `docs/ARCHITECTURE.md` | Components + how data flows (1 page) |
| `docs/DECISIONS.md` | Ongoing decisions log (the L1 form of ADR; one bullet-list per decision) |
| `docs/STATUS.md` | Done / in progress / known limitations |
| `docs/TEST_PLAN.md` | How correctness is proven (manual or automated) |
| `ENTRY.md` (optional at L1) | If >1 "where does X live" navigation |

For a script/small tool, several of these collapse into README. Keep the **spirit**
(everything is documented, one entry points) even if the files merge.

**Grow out of L1** when a second contributor arrives, the API becomes stable and
public, or docs start contradicting each other.

---

## L2 — Canonical (mature project)

**Rule:** the full catalog (see `catalog.md`). The reference model is pmOS
(`examples/pmos/`). Every document exists, has a purpose, and gets a card in
`docs/REFERENCE.md`.

Catalog (from `catalog.md`) — all the root + `docs/` documents: `README`, `ENTRY`,
`AGENT`, `DELIVERY`, community files, `docs/{ARCHITECTURE, FEATURES, SAGA, TEST_CASES,
DEV_GUIDE, IMPROVEMENTS, TROUBLESHOOTING, BACKLOG, REVIEW, REFERENCE}`, `docs/ADR/*`.
Plus generators (`scripts/`) if the project uses codegen.

**Hallmarks of a good L2 set:**
- One entry point (`ENTRY.md`), one map (`REFERENCE.md`).
- Explicit hierarchy of truth (which doc wins on conflict).
- A drift table (doc-vs-fact) kept current.
- A delivery gate (`DELIVERY.md`) + agent runbook (`AGENT.md`).

**Grow into L3** when the project is one of the profile shapes below and benefits
from hard, rigged-out per-module contracts.

---

## L3 — Profiles (L2 + hard layout per project type)

Principles: profiles multiply L2 **contract-first discipline** and frame
**the canonical layout** for a project shape. Code and docs are organized to match
**the pattern** exactly.

### Profile 1 · microservices

Shape: many independently-scoped services around an event bus / shared storage.

- **Layout:** `services/<name>/` + `contracts/openapi/*.yaml` +
  `contracts/asyncapi/events.yaml`.
- **Fill order extras:** Phase 3 is **mandatory before any code**: every endpoint in
  the OpenAPI spec — conformance-tested. Events are the glue.
- **Needs:** `docs/SAGA.md` (cross-service scenarios), per-service
  `test/contract.test.ts` (OpenAPI-conformance), a returnable `scaffold-script`
  (in `scripts/`).
- **Drives consistency:** every service shares one template (routes, db, events,
  tests) — see the per-module layout in `catalog.md`.

### Profile 2 · monolith

Shape: single app, optional internal module dirs.

- **Layout:** `src/modules/<name>/` + one public `contracts/openapi.yaml`.
- **Needs:** `docs/SAGA.md` only if modules talk asynchronously (event bus inside);
  otherwise `docs/*` module interactions stay in `ARCHITECTURE.md`.
- **First-class:** contract-first, but all in one file; tests are module-scoped.

### Profile 3 · frontend-app

Shape: `src/` + routing/pages/components, one API contract.

- **Needs:** API contract it consumes from `contracts/openapi`; a visual-design doc
  or reference (design tokens, palettes, component inventory); `docs/TEST_CASES.md`
  covering Components + E2E (Playwright); `DEV_GUIDE.md` with token-based workflow.
- **Drives:** theming, a11y, and "design system" are part of the docs — not inline
  only.

### Profile 4 · library-tool / SDK / CLI

Shape: `src/` + exported public API via one `index` + one contract.

- **Needs:** a **public API profile** doc (what exports/canals/commands are
  stable vs experimental), changelog discipline (ADR `CHANGELOG.md` or keep each
  breaking change in ADR), semver versioning doc, test matrix (node versions).
- **First-class:** docs face the *consumer* — README is a usage guide first, not an
  architecture essay.

### Profile 5 · data-pipeline / ETL

Shape: `src/` (sources/transforms/sinks) + `dags/` + one schema/contract per stage.

- **Needs:** data contracts (`contracts/schema/*` — schemas of input/output frames),
  a lineage map (doc in ARCHITECTURE-style), idempotency/replay rules, quality
  checks (`TEST_CASES.md`), and a `DEV_GUIDE.md` for re-runs.
- **Drives:** schema-first; the "truth" is the data contract, not the pipeline code.

---

## Decision table (from SKILL.md)

| Project state | Level |
|---|---|
| Idea / first 2 weeks | **L1** |
| Small tool / script / library | **L1** |
| Real product, >1 contributor | **L2** |
| Microservices / API-first / long-lived | **L3·microservices** |
| Monolith with modules | **L3·monolith** |
| Frontend application | **L3·frontend-app** |
| Reusable SDK / CLI / package | **L3·library-tool** |
| Data pipeline / ETL | **L3·data-pipeline** |

> If unsure between L1 and L2, start L1 and grow. Over-documenting a toy is
> worse than under-documenting a growing project (the map catches drift).