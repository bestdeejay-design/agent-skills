# ROADMAP — docs-system development plan

> Where the skill is now and where it's going. Short-term items unblock the biggest
> gaps; long-term make the skill a general tool for any docs problem. Prioritized,
> each item has a "done when" so progress is verifiable.

---

## Now (current state)

Shipped: SKILL.md (guide: product + project branches) + product-docs.md/project-docs.md
catalogs + order/levels/completeness + 14 project templates + 3 product templates +
example-monorepo reference. Reorganized: templates now live in `templates/{product,project}/`,
product docs have their own branch and templates (VISION/PRD/ROADMAP).

Verified: templates are clean of generation artifacts; fill order is explicit;
completeness gate exists; level decision lives in SKILL.md + levels.md reference.

## Short-term — make it immediately usable (P1)

Status of subsequent phases in the gaps that matter for first real use:

| # | Item | Why | Done when |
|---|------|-----|-----------|
| 1 | **Usage example** `examples/apply.md` | An agent/intern handles an idea → full doc set following the skill, step by step. Proves the skill works end-to-end, not just on paper. | `examples/apply.md` shows a concrete idea → completed L1 → grown L2 set with real decisions. |
| 2 | **Per-template "fill me" placeholders doc** | Templates are skeletons; a note describing how to fill each section consistently (single consistent voice). | New doc or section in `references/product-docs.md` / `references/project-docs.md` lists, per template, which sections are facts vs judgement. |
| 3 | **L1 → L2 growth recipe** | A concrete "when and how to grow" — trigger list + steps to promote a doc from L1 to L2 without rewrite. | `references/levels.md` gains a "growing a level" subsection with a checklist. |
| 4 | **mnemonic / tag** | Give the skill a memorable short name + a `tags:` frontmatter so an agent/prompt can "route" to it. | SKILL.md frontmatter includes a clear `name`, `tags`, and one-line «does». |

## Mid-term — broaden coverage (P2)

| # | Item | Goal | Done when |
|---|------|-----|-----------|
| 5 | **Fourth profile: `templates/monolith` gap** | Monolith profile is the thinnest — concrete module dir layout + "one contract file" guidance is weak. | profile section has a layout diagram and a contracts/0 example for monolith. |
| 6 | **data-pipeline profile details** | Lineage, replay, schema-per-stage are mentioned but not sketched. | `levels.md` data-pipeline profile has a real `dag/` example and a schema-contract example. |
| 7 | **A "doc lifecycle" appendix** | Each doc's life: created → reviewed → deprecated → superseded. | `references/` gains `lifecycle.md` (state machine). |
| 8 | **CI-style completeness check** | Turn `completeness.md` into a runnable check (e.g. a script) that flags missing docs/drift | a `scripts/check-docs` validates links + counts + drift rows automatically. |

## Long-term — a general docs-tool (P3)

| # | Item | Goal | Done when |
|---|------|-----|-----------|
| 9 | **Language stability** | SKILL.md EN, templates EN, but allow RU mirror / localization hook. | A `localization.md` doc describing the EN/RU mirror (like the example monorepo README/ru). |
| 10 | **Framework integration** | Works with the agent's own "project-spirit" system (entry/map/gate) beyond opencode. | Reference in SKILL.md demonstrates integration with the user's existing agent skills. |
| 11 | **Multi-{open- close} catalog** | Support simple projects with only L1 without the noise of the full catalog. | `project-docs.md` has explicit L1-only view: which docs, which sections of each, which to skip. |
| 12 | **Sibling skills repo-wide** | `agent-skills/` grows a mechanism to discover/install skills (README inventory + `skills.json`). | root README lists every skill with a one-liner + install path. |

---

## Principles that shape the plan

1. **Smallest working level grows** — prefer improving L1 and the growth path to
   flooding L3 with edge cases.
2. **Verifiable before claimable** — each item has a "done when" that is
   checkable (a file exists, a section is added, a link resolves).
3. **Truth before code** — the catalog's machine-truth rule applies to the skill
   itself: document before automating.
4. **Reuse, don't invent** — extending example-monorepo patterns is cheaper than inventing a
   schema; the skill's own docs follow its own catalog.

---

## Backlog (nice-to-have, no priority yet)

- [ ] Screenshot / mini-case: how the skill transforms a toy repo's chaotic docs into an order
- [ ] ADR-template example for a "one-file ADR log" (L1 DECISIONS.md) to reduce ADR overhead
- [ ] A quick "self-test" the skill can run on its own templates (does this repo contradict its own rules)