# Product documentation — catalog

> **What this is:** the **product-facing** documents — the «why» and «what» of the
> project. Written from an idea forward, before (or in parallel with) engineering docs.
>
> **RU:** продуктовые документы — «зачем» и «что»: видение, требования, дорожная
> карта, метрики. Пишутся до проектной документации.

## Which docs belong here

| File | Purpose | Written when | Template |
|------|---------|:------------:|----------|
| `docs/VISION.md` | **Why this product exists**: audience, problem, value, principles, scope, long-term success | Phase 1 — first, stays stable | `templates/product/VISION.tmpl` |
| `docs/PRD.md` | **What we build**: requirements (functional + non-functional), priorities, acceptance criteria, success metrics, user stories | After VISION, before architecture | `templates/product/PRD.tmpl` |
| `docs/ROADMAP.md` | **What ships when**: milestones, value per milestone, proof (metrics), dependencies || Phase 2+, updated each milestone | `templates/product/ROADMAP.tmpl` |
| `docs/FEATURES.md` | **Feature catalog + status** (✅/📋) — the bridge between product and engineering | From requirements, kept current | `templates/project/FEATURES.tmpl` |

> **RU:** главное правило — **VISION → PRD → ROADMAP → FEATURES**. Видение
> порождает требования, требования порождают план и каталог фич. Ничего не
> пишется «с конца».

## The order of writing

1. **VISION.md** — can you state the product in 1–2 sentences? If not, stop and
   clarify before writing anything else. (RU: не можешь сформулировать видение — стоп.)
2. **PRD.md** — goals/non-goals, stories with priorities, functional +
   non-functional requirements, acceptance criteria, **success metrics** (a
   milestone without a metric is a wishlist).
3. **ROADMAP.md** — order the PRD's milestones by value (not effort), each with a
   target date, features, proof.
4. **FEATURES.md** — the living status board of every feature, ✅/📋 only against
   reality. This doc hands the product requirements to the engineering side.

## Links across the boundary

| Engineering doc | Takes from product | Gives back |
|-----------------|--------------------|------------|
| `docs/ARCHITECTURE.md` | PRD non-functional requirements | component decisions → PRD «technical notes» |
| `docs/TEST_CASES.md` | acceptance criteria | proof that a story is done |
| `docs/IMPROVEMENTS.md` | roadmap drift (missed dates, changed scope) | prioritized fix plan → next milestone |
| `docs/REVIEW.md` | any doc-vs-reality mismatch | reconciled product/eng truth |

## Checklist (product side)

- [ ] VISION: 1 paragraph; audience named; explicitly listed **out-of-scope** items.
- [ ] PRD: every story has a priority (MoSCoW/P0–P2) and links to a feature.
- [ ] PRD: success metrics present (baseline → target) — not "quality" in prose.
- [ ] ROADMAP: milestones ordered by value; each has a date/target + a metric.
- [ ] FEATURES: ✅/📋 statuses match reality (no wishlist-only catalog).

---
> **Rule:** product docs answer «why» and «what»; engineering docs answer «how».
> If a doc has no reader having no question it answers — it does not belong.
> **RU:** продуктовая документация отвечает «зачем» и «что», инженерная — «как».
> Если у документа нет читателя и вопроса, на который он отвечает — его нет.