---
name: docs-system
description: "Systematic documentation for any project. From an idea to a complete documentation set — nothing forgotten. Establishes a documentation catalog (what files, why, when), a fill order (phases), per-project levels (L1 minimal / L2 canonical / L3 profiles), full document skeletons, and a completeness checklist. Use when starting a new repo, creating documentation from scratch, auditing existing docs, or when a project needs a documentation map (ENTRY/REFERENCE). Triggers: 'документация', 'набор документации', 'каталог документов', 'docs catalog', 'documentation structure', 'из идеи в документацию', 'полная документация', 'docs for new project', 'documentation plan', 'системная документация'."
---

# docs-system — Systematic Documentation for Any Project

Turn an idea into a **complete, consistent documentation set** — or bring an existing
project's docs into order — so nothing is forgotten and every document has a clear
purpose, place, and fill order.

## Why this skill exists

Most projects either have no docs (agents and humans get lost) or have *lots* of docs
with no system (contradictions, drift, nobody knows which file is authoritative).
This skill codifies the *system* that makes documentation useful: a **catalog** (what
files, why, when), a **fill order** (from idea to complete set), **levels** (right-sized
for the project), **templates** (copy-paste skeletons), and a **completeness checklist**.

The reference model behind this skill is the pmOS monorepo (`examples/pmos/`): a
microservices project whose docs stayed consistent for hundreds of commits because
every file had a purpose, there was an explicit hierarchy of truth, a single entry
point (`ENTRY.md`), a documentation map (`REFERENCE.md`), and a delivery gate.

## When to use

- Starting a new repository / project — generate the docs skeleton **before** or **in
  parallel with** the first code.
- Turning a raw idea into a full documentation set.
- Auditing an existing project with missing/chaotic documentation.
- Adding a feature or service and needing to know *which docs to update*.

## How it works (TL;DR)

1. **Pick a level** (see `references/levels.md`):
   - **L1 — Minimal core**: any project, from day one. 6 documents.
   - **L2 — Canonical**: mature project. Full catalog (like pmOS).
   - **L3 — Profiles**: L2 + a hard template per project type
     (microservices / monolith / frontend-app / library-tool / data-pipeline).
2. **Read the catalog** (`references/catalog.md`) — every document: purpose, when it
   exists, which level requires it.
3. **Follow the fill order** (`references/order.md`) — phases 1→10 from idea to
   complete set. Order matters: contracts before code, map last.
4. **Use the templates** (`references/templates/`) — copy the skeleton, fill the
   sections.
5. **Finish with the completeness checklist** (`references/completeness.md`) — prove
   nothing was forgotten.

## Two golden rules (from pmOS)

1. **Machine truth before code.** Contracts/OpenAPI/events (anything that *is* the
   interface) are written **before** implementation. Code implements the contract,
   not the other way around.
2. **The map comes last.** `REFERENCE.md` (the documentation map) is written last,
   because it describes everything above it. Writing it forces you to verify the whole
   set is consistent.

## Level selection guide

| Project state | Level |
|---|---|
| Brand-new idea / first 2 weeks | **L1** (minimal) — grow later |
| Small tool, script, library | **L1** |
| Real product, multiple modules, >1 contributor | **L2** (canonical) |
| Microservices, API-first, long-lived | **L3 · microservices** |
| Monolith with modules | **L3 · monolith** |
| Frontend application | **L3 · frontend-app** |
| Reusable library / SDK / CLI | **L3 · library-tool** |
| Data pipeline / ETL / analytics | **L3 · data-pipeline** |

> Rules of thumb: prefer the **smallest level that fits**; grow L1→L2→L3 when the
> project outgrows it. Never force L2/L3 on a toy project — the catalog becomes noise.

## Applying the skill

1. **Ask (or infer) the project shape**: level, project type, team size, expected
   lifespan, is there code already?
2. **Generate the skeleton**: create the doc files from the level's catalog +
   templates. For L3, use the profile's hard layout.
3. **Fill in phase order** (contracts before code, map last).
4. **Run the completeness checklist** before declaring "documentation done".
5. If auditing an existing project: start with `REFERENCE.md`-style map of what
   exists, then fill gaps in catalog order.

## References index

| File | Purpose |
|------|---------|
| `references/catalog.md` | **All documents**: name → purpose → when → level |
| `references/order.md` | **Fill order**: phases from idea to complete set |
| `references/levels.md` | Levels L1/L2/L3 + profile layouts |
| `references/completeness.md` | Checklist: "nothing forgotten" before delivery |
| `references/templates/*` | Copy-paste skeletons for every document |
| `examples/pmos/` | Real-world canonical reference (pmOS monorepo) |
