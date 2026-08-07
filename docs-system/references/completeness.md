# Completeness Checklist — "nothing forgotten" before delivery

Run this before declaring documentation "done". It is the delivery gate of the
docs-system. Every item must pass at the **chosen level** (see `levels.md`). If you
don't know the level, default to L1 (grow later).

For L2/L3, each failing item is a **blocking** inconsistency — fix the doc, then
update `REFERENCE.md` with its card.

---

## A. Entry & navigation (all levels)

- [ ] A reader/agent can find, in ≤30 seconds, the answer to "what is this project?".
- [ ] There is one **entry point** document that routes "topic → file" (`ENTRY.md`
      at L2+, or README at L1).
- [ ] Every doc referenced in the entry point actually exists (no dead links).
- [ ] Every doc that exists has a link pointing to it from somewhere above it.

## B. Truth hierarchy & consistency (L2+)

- [ ] There is an explicit **hierarchy of truth** (which doc wins on conflict), in
      `REFERENCE.md`.
- [ ] The **drift table** (doc-vs-fact) is populated with current, open items.
- [ ] No fact exists in two places unless one is declared the source and the other a
      duplicate-links-to-it.
- [ ] README's "Status"/counts match the actual number of modules/services/tests
      (or the discrepancy is an open drift-table item, not silent).

## C. Machine truth before code (L3·microservices / API-first)

- [ ] Contracts (`contracts/openapi/*.yaml`, `asyncapi/events.yaml`) exist and are
      written **before** implementation (or, if auditing: match the code exactly).
- [ ] Every real endpoint/event has a contract entry; conformance tests pass.
- [ ] No route/event exists in code that is missing from the contract
      ("agent invented it").

## D. Feature & status (L2+)

- [ ] `FEATURES.md` catalogs every module/feature with ✅/📋 status.
- [ ] `REVIEW.md`/`STATUS.md` reflects reality: done / in progress / limitations
      match the code.
- [ ] Counts in headers match `grep`-able facts (or have a recognized drift note).

## E. Cross-module behavior (L3·microservices, or L2 with >1 module)

- [ ] `SAGA.md` (or equivalent) covers every cross-module scenario: trigger,
      steps, compensation, retry, idempotency.
- [ ] Every event that crosses an internal boundary is defined in the event catalog.

## F. Verification (L2+)

- [ ] `TEST_CASES.md` covers each planned scenario + coverage matrix.
- [ ] Contract-conformance tests exist wherever contracts exist.
- [ ] The delivery gate (`DELIVERY.md`) states how to build/verify, what's in, what's
      NOT in.

## G. Run it (all levels)

- [ ] README "Quick start" / `DEV_GUIDE.md` reproduce a successful local run from a
      clean clone (commands correct, order right, env vars listed).
- [ ] Troubleshooting entry exists for errors found while running (`TROUBLESHOOTING.md`).

## H. Map (L2+)

- [ ] `REFERENCE.md` exists and has a **card for every doc**: purpose, structure,
      key facts, links — including itself.
- [ ] ADR table in `REFERENCE.md` lists every ADR with status (active/superseded).
- [ ] The map's "how to maintain this file" section is up to date (info periodic).

## I. Human/community (public L2+)

- [ ] `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` exist (link from README).
- [ ] `LICENSE` present for public repos.

## J. Agent runbook (L2+ / any with agent-assisted build)

- [ ] `AGENT.md` defines roles, phases, Definition of Done, and a commit gate.
- [ ] An agent following `ENTRY` → `REFERENCE` can find each doc it needs with no
      ambiguity.

---

## How to run

1. Start at the bottom of the checklist (J → A) or top (A → J):
   fix in order of the delete that's blocking the next.
2. For each **No** — either fix the doc or add a serviceable drift row
   (visible, not hidden).
3. Re-run until every item passes at the selected level.
4. When all pass → the documentation set is "complete at this level".