---
name: docs-product
description: "Product documentation branch — the 'why' and 'what' of a project: VISION.md, PRD.md, ROADMAP.md, FEATURES.md. Written from an idea forward, before engineering docs. Order: VISION -> PRD -> ROADMAP -> FEATURES. Full catalog + checklist in references/product-docs.md, templates in templates/. Triggers: 'продуктовая документация', 'vision', 'prd', 'роадмап', 'roadmap', 'фичи документация', 'product docs', 'требования к продукту', 'документация продукта'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.0.0"
compatibility: "No scripts — template-driven authoring"
when_to_use: "Use when user needs product docs: 'продуктовая документация', 'vision', 'prd', 'роадмап', 'roadmap', 'product docs', 'требования к продукту', 'документация продукта'. Examples: 'write a PRD for my app', 'создай VISION и ROADMAP для проекта'."
---

# Docs Product — product documentation («why» & «what»)

Use this skill to write the **product-facing** documents: vision, requirements,
roadmap, feature catalog. Written from an idea forward — **before** (or in
parallel with) engineering docs.

## When to use

- A project needs its product docs: VISION, PRD, ROADMAP, FEATURES.
- User asks for "продуктовая документация", "vision", "prd", "роадмап",
  "требования к продукту", "product requirements".
- Requirements must become the input for engineering docs.

## Do NOT use

- For engineering docs (architecture, ADR, tests, dev guide, map) — that is `docs-project`.
- For the meta-guide (phases, levels L1/L2/L3, completeness checklist) — `docs-system`.

## Which docs belong here

| File | Purpose | When | Template |
|------|---------|:----:|----------|
| `docs/VISION.md` | Why the product exists: audience, problem, value, principles, scope, long-term success | Phase 1 — first, stays stable | `templates/VISION.tmpl` |
| `docs/PRD.md` | What we build: functional + non-functional requirements, priorities, acceptance criteria, success metrics, user stories | After VISION, before architecture | `templates/PRD.tmpl` |
| `docs/ROADMAP.md` | What ships when: milestones, value per milestone, proof (metrics) | Phase 2+, updated each milestone | `templates/ROADMAP.tmpl` |
| `docs/FEATURES.md` | Feature catalog + status (✅/📋) — the bridge to engineering | From requirements, kept current | `templates/FEATURES.tmpl` |

The golden chain: **VISION → PRD → ROADMAP → FEATURES**. Vision spawns
requirements, requirements spawn the plan and the feature catalog. Nothing is
written "from the end".

## Order of writing

1. **VISION** — can you state the product in 1–2 sentences? If not, stop and
   clarify before writing anything else.
2. **PRD** — goals/non-goals, stories with priorities, functional +
   non-functional requirements, acceptance criteria, **success metrics**
   (a milestone without a metric is a wishlist).
3. **ROADMAP** — order the PRD's milestones by value (not effort), each with a
   target date, features, and proof.
4. **FEATURES** — the living status board of every feature, ✅/📋 only against
   reality. This doc hands the product requirements to the engineering side.

## Links across the boundary (with docs-project)

| Engineering doc | Takes from product | Gives back |
|-----------------|--------------------|------------|
| `ARCHITECTURE.md` | PRD non-functional requirements | component decisions → PRD "technical notes" |
| `TEST_CASES.md` | acceptance criteria | proof that a story is done |
| `IMPROVEMENTS.md` | roadmap drift (missed dates, changed scope) | prioritized fix plan → next milestone |
| `REVIEW.md` | any doc-vs-reality mismatch | reconciled product/eng truth |

## Checklist (product side)

- [ ] VISION: 1 paragraph; audience named; explicitly listed **out-of-scope** items.
- [ ] PRD: every story has a priority (MoSCoW/P0–P2) and links to a feature.
- [ ] PRD: success metrics present (baseline → target) — not "quality" in prose.
- [ ] ROADMAP: milestones ordered by value; each has a date/target + a metric.
- [ ] FEATURES: ✅/📋 statuses match reality (no wishlist-only catalog).

> Rule: product docs answer «why» and «what»; engineering docs answer «how».
> If a doc has no reader and no question it answers — it does not belong.
