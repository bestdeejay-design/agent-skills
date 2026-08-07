# Levels & Profiles — right-sizing the documentation (reference)

> **Purpose:** reference for **large or growing systems** — how many documents to
> create and how rigid the layout should be. The main guide (SKILL.md) assumes
> L1/L2 out of the box; consult this file when a project outgrows the default.
>
> **RU:** справочник для больших систем: какой объём документации нужен и насколько
> жёсткий лейаут. Основной гайд (SKILL.md) по умолчанию работает на L1/L2 —
> обращайтесь сюда, когда проект перерастает стандартный набор.

All levels share the same engine (`references/order.md`) — the difference is
*how many documents* exist and *how detailed* templates are. Pick the **smallest
level that fits**; grow it as the project outgrows it.

---

## L1 — Minimal core (any project, from day one)

**Rule:** every project, no matter how small, gets a working documentation spine,
so the agent and humans are never lost.

| File | Why |
|------|-----|
| `README.md` | What it is, how to run, status (1 page) |
| `docs/ARCHITECTURE.md` | Components + how data flows (1 page) |
| `docs/DECISIONS.md` | Ongoing decisions log (L1 form of ADR; one bullet per decision) |
| `docs/STATUS.md` | Done / in progress / known limitations |
| `docs/TEST_PLAN.md` | How correctness is proven (manual or automated) |
| `ENTRY.md` (optional) | If >1 "where does X live" navigation |

For a script/small tool, several of these collapse into README. Keep the **spirit**
(everything documented, one entry point) even if the files merge.

**Grow out of L1** when a second contributor arrives, the API becomes stable and
public, or docs start contradicting each other.

> **RU:** минимум для любого проекта — «спина» из 5–6 документов. Для скрипта
> большинство сливается в README. Переходите на L2 при втором контрибьюторе,
> стабильном публичном API или первых противоречиях в доках.

---

## L2 — Canonical (mature project)

**Rule:** the full catalog — see `references/project-docs.md` (all root + `docs/`
documents, `docs/ADR/*`, contracts for API-first). The reference model is pmOS
(`examples/pmos/`). Every document has a purpose and a card in `docs/REFERENCE.md`.

**Hallmarks of a good L2 set:**
- One entry point (`ENTRY.md`), one map (`REFERENCE.md`).
- Explicit hierarchy of truth (which doc wins on conflict).
- A drift table (doc-vs-fact) kept current.
- A delivery gate (`DELIVERY.md`) + agent runbook (`AGENT.md`).
- `FEATURES.md` status board linking product (PRD) and engineering.

**Grow into L3** when the project matches one of the profile shapes below and
benefits from hard, per-module contracts.

---

## L3 — Profiles (L2 + hard layout per project type)

Principles: profiles multiply L2 **contract-first discipline** and frame
**the canonical layout** for a project shape. Code and docs are organized to
match **the pattern** exactly.

### Profile 1 · microservices
- **Layout:** `services/<name>/` + `contracts/openapi/*.yaml` + `contracts/asyncapi/events.yaml`.
- **Fill order extras:** Phase 3 mandatory **before any code**; every endpoint
  conformance-tested. Events are the glue.
- **Needs:** `docs/SAGA.md`, per-service `test/contract.test.ts`, a reusable
  `scaffold-script` (in `scripts/`).

### Profile 2 · monolith
- **Layout:** `src/modules/<name>/` + one public `contracts/openapi.yaml`.
- **Needs:** `docs/SAGA.md` only if modules talk asynchronously; otherwise module
  interactions stay in `ARCHITECTURE.md`.
- **First-class:** contract-first, one file; tests module-scoped.

### Profile 3 · frontend-app
- **Needs:** the API contract it consumes; a visual-design doc (tokens, palettes,
  component inventory); `docs/TEST_CASES.md` covering Components + E2E (Playwright);
  `DEV_GUIDE.md` with token-based workflow.
- **Drives:** theming, a11y, and "design system" are part of the docs — not inline only.

### Profile 4 · library-tool / SDK / CLI
- **Needs:** a **public API profile** doc (stable vs experimental exports),
  changelog discipline, semver versioning doc, test matrix (node versions).
- **First-class:** docs face the *consumer* — README is a usage guide first.

### Profile 5 · data-pipeline / ETL
- **Needs:** data contracts (`contracts/schema/*`), a lineage map, idempotency/replay
  rules, quality checks (`TEST_CASES.md`), `DEV_GUIDE.md` for re-runs.
- **Drives:** schema-first; the "truth" is the data contract, not the pipeline code.

---

> **RU:** решение по уровню — из таблицы в SKILL.md. Если сомневаетесь между L1
> и L2 — берите L1 и растите: пере-документировать игрушку хуже, чем недо-документировать
> растущий проект (карту/дрифт держит REFERENCE).