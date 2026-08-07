# Completeness Checklist — the delivery gate

Run this before declaring documentation "done". Every item must pass at the
**chosen level** (`references/levels.md`); if the set has no explicit level,
default to L1 and grow later. L2/L3 ownership: every unchecked box is a blocking
inconsistency.

> **RU:** прогоняется перед сдачей документации. Каждый пункт должен сходиться
> на выбранном уровне. Для L2/L3 несоблюдение пункта — блокер.

## A. Product side

- [ ] VISION (1 paragraph), audience, problem, out-of-scope, success criteria.
- [ ] PRD: goals + non-goals; every story has a priority; success metrics have
      baseline → target; acceptance criteria are testable.
- [ ] ROADMAP: milestones ordered by value; each has date/target + a metric
      proof (not a wishlist).
- [ ] FEATURES: every feature has a ✅/ / status that matches reality.

## B. Entry & navigation

- [ ] A reader/agent finds "what is this project?" in ≤30 seconds.
- [ ] One entry point routes "topic → file" (`ENTRY.md` at L2+, README at L1).
- [ ] No dead links: every doc referenced in the entry point exists; every doc
      is reached from something above it.

## C. Truth & drift

- [ ] Hierarchy of truth declared (which doc wins on conflict) — in
      `docs/REFERENCE.md` (L2+).
- [ ] Drift table populated: every known doc-vs-fact mismatch is either fixed or
      has an explicit row. **No silent inconsistencies.**
- [ ] No fact duplicated in two docs unless one is the source and the other an
      explicit link to it.

## D. Contracts & tests

- [ ] Contracts were written **before** code (API-first) and match implemented
      endpoints/events — no route "invented" outside the spec.
- [ ] `TEST_CASES.md` (L2+) covers planned scenarios + coverage matrix; contract
      conformance tests exist for each contract.
- [ ] L1: if only `TEST_PLAN.md` exists — its tests actually run and pass.

## E. Delivery & runbook

- [ ] `DEV_GUIDE.md` / README Quick start reproduce a successful run from a clean
      clone (commands, env vars, migrations).
- [ ] Errors found while running have a `TROUBLESHOOTING.md` entry.
- [ ] `AGENT.md` (L2+ / agent-assisted): roles, phases, Definition of Done,
      commit gate — present and referenced.

## F. Map (L2+)

- [ ] `REFERENCE.md` has a card for **every doc** (purpose, structure, facts,
      links) — including a card for REFERENCE itself.
- [ ] ADR table lists every ADR with status (active/superseded); ADR tracking
      works.
- [ ] The "how to maintain this file" section is up to date.

## G. Community & legal (public repos)

- [ ] `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` exist
      and are linked from README.

## How to run

1. Fix in the order that unblocks the next item — product → entry → truth →
   contracts/tests → delivery → map.
2. Every «No» ends either in a fix **or** an explicit drift-table row — never
   silence.
3. Re-run until green. Green = "documentation set complete at this level",
   ready for `docs/REFERENCE.md` sign-off.