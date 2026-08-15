---
name: skill-forge
description: >-
  Meta-skill and design compass for creating new skills and upgrading existing ones with a deliberate push toward being maximally technological, creative, and aesthetically disciplined. Use when the user wants to create a skill from scratch, reshape an existing skill, make a skill more reliable/technological, more creative/varied, or more visually polished — or when a skill feels templated, generic, or mechanically weak. Trigger on phrases like "создай скил", "новый скил", "улучши скил", "сделай скил креативнее", "эстетичный скил", "технологичный скил", "скилл выглядит шаблонно", "перепиши SKILL.md", even if the user does not say the word "skill" explicitly. Also use when reviewing a skill before release.
license: MIT
metadata:
  version: 1.0.0
---

# skill-forge

A compass, not a dictator. This skill helps you **design** skills that are
maximally **technological** (engineered, reliable, composable), **creative**
(generative, varied, distinctive), and **aesthetically disciplined** (intentional,
not templated). It separates the *obligatory base* — rules you must not break —
from *accents* — amplifiers you choose per task.

> Russian triggers: `создай скил`, `новый скил`, `улучши скил`, `сделай скил
> креативнее`, `эстетичный скил`, `технологичный скил`, `скилл шаблонный`,
> `перепиши SKILL.md`, `мета-скилл`, `проверь скилл перед релизом`.

## Level 0 — Hard rules (the base, never break these)

These come from the official Agent Skills specification (agentskills.io) plus our
own working gates. They are **non-negotiable**.

- **Frontmatter**: `name` (≤64 chars, `a-z 0-9 -`, no double hyphens, MUST match
  the folder name) and `description` (≤1024 chars, MUST state *what* the skill
  does AND *when* to use it). Put all "when to use" info in `description`, never
  in the body. Make triggers a little "pushy" to fight undertriggering — list
  synonyms and casual phrasings.
- **Progressive disclosure**: keep `SKILL.md` under 500 lines. Bundle code in
  `scripts/` (deterministic, repetitive tasks), docs in `references/` (loaded as
  needed; add a TOC if >300 lines), outputs in `assets/`. Reference files one
  level deep only.
- **Voice**: write in the imperative. Explain the *why* instead of heaped MUST/
  ALWAYS/NEVER — all-caps rigidity is a yellow flag. The model is smart; reason
  with it.
- **Principle of Lack of Surprise**: no malware, no deceptive or malicious
  content. A skill's intent must match its description.
- **Single data contract**: one spec file (e.g. `deck.json`) is the source of
  truth; every stage reads/writes it so artifacts are regenerable.
- **Mandatory gates**: nothing is "done" until automated checks PASS. At minimum:
  structural/format validation, content QA, and — for any visual output — a
  real-browser or render gate.
- **Reproducibility**: deterministic seed so the same input yields the same
  output on another day.
- **Anti-template baseline** (our enforcement, mechanical): ≤2 typefaces, ≤4
  accent roles (keep 60-30-10), WCAG contrast (text ≥4.5:1, large/non-text
  ≥3:1), **zero raw hex outside `:root`** (every color is a token), one mood per
  artifact, one idea per slide, assertion headlines (full sentence with a verb),
  words-per-slide budget.

## Level 1 — Accent: Technological

Pick this when the skill must be *engineered*. It is an amplifier, not required.

- **Modular base + pluggable patterns** — never a monolithic template. Each
  artifact assembles from base + only the patterns it uses, so no two outputs
  share a prebuilt shell.
- **Composable pipeline**: small single-purpose scripts, one command per stage,
  everything inspectable and debuggable.
- **Real verification**: for any UI/visual output, a Playwright/Chromium gate is
  mandatory (geometry, overflow, clipping, keyboard nav).
- **Fixed contract constants** (lesson from the official `pptx` skill): pin the
  canvas (e.g. 1600×900), the safe font (e.g. Arial — LibreOffice substitutes
  matter), and exempt decorative elements from bounds checks by naming
  convention (`ghost*`, `decor*`, `chrome-*`).
- **Binary-format safety**: when generating OOXML/PDF, follow the hard rules —
  no `#`/8-digit hex (corrupts files), parse with `defusedxml` (round-tripping
  through `ElementTree` rewrites namespaces and corrupts), run the validator
  *after* generating and fix in the generator, never hand-edit packed XML.

## Level 2 — Accent: Creative

Pick this when the skill must *vary* and *surprise* (in a good way).

- **Generative composition from a seed**: synthesize layout/parameters
  deterministically from a deck seed (title + date + index) so rebuilding on
  another day yields a different but reproducible mix.
- **Variety across artifacts**: different outputs should carry different visual
  "handwriting" — not one shared base. Multiple base styles, each deck picks
  its own.
- **Signature element**: one memorable, brief-true motif per artifact (NOT a
  color bar or accent stripe — those read as AI filler).
- **Avoid the three AI-default looks**: (1) cream `#F4F1EA` + high-contrast serif
  + terracotta; (2) near-black + single acid-green/vermilion accent; (3) broadsheet
  hairline rules, zero radius, newspaper columns. Where the brief leaves an axis
  free, don't spend that freedom on a default.

## Level 3 — Accent: Aesthetic

Pick this when the skill must *look intentional*.

- **Mood system**: `swiss | editorial | flat | glass | dark` drives the regime;
  one mood per artifact, one radius/stroke language.
- **Token system (4 parts)**: palette as 4–6 named hex; type as 2+ roles
  (characterful display used with restraint + complementary body + utility face);
  layout as one-sentence prose + ASCII wireframes; signature as the single
  unique element.
- **Assertion headlines**: full sentences with a verb — a conclusion, not a topic.
- **Typography floor**: body text readable at projection scale (≥17px cards,
  labels ≥17px, metric values 30–48px); re-check overflow after any font change.
- **Restraint**: *spend your boldness in one place* — let the signature be the one
  memorable thing, keep everything else quiet. Chanel's rule: before shipping,
  remove one accessory. Match complexity to the vision; elegance is executing the
  chosen vision well.
- **Structural honesty**: numbering/eyebrows/dividers should encode something true
  about the content, not decorate it (numbered markers only if it's actually a
  sequence).

## Process — the build loop

Adapted from the official `skill-creator` flow, with an accent pass added:

1. **Capture intent** — what should the skill enable? when should it trigger?
   what's the output format? do we need test cases (objective outputs do;
   subjective ones often don't)?
2. **Draft SKILL.md** — follow Level 0; choose accents from Levels 1–3 that fit
   the task.
3. **Test prompts** — 2–3 realistic user phrasings; save to `evals/evals.json`.
4. **Parallel runs** — with-skill vs baseline subagents in the same turn; capture
   `total_tokens` / `duration_ms` to `timing.json` (only chance to get them).
5. **Grade** — objective assertions with `text` / `passed` / `evidence`, no
   partial credit; superficial pass = fail. Subjective quality → human judgment.
6. **Accent pass (added)** — on each iteration ask: did we keep it technological,
   creative, *and* aesthetically disciplined? Did it slip into a default look or a
   monolith?
7. **Improve** — generalize from feedback; keep the prompt lean; explain the why;
   if all test runs wrote the same helper, bundle it into `scripts/`.
8. **Optimize description** — generate ~20 trigger queries (mix should/should-not,
   include near-misses and casual typos), split 60/40 train/test, iterate up to 5×
   to get `best_description` by test score.
9. **Package** — `package_skill` → `.skill` file; preserve the original `name`.

## Release checklist

- [ ] Level 0 hard rules all satisfied (frontmatter, <500 lines, gates green)?
- [ ] Chosen accents actually *amplified*, not just "it works"?
- [ ] Escaped the three AI-default looks (Level 2)?
- [ ] Token system coherent: one mood, ≤2 typefaces, ≤4 accent roles, zero raw hex?
- [ ] Signature element present and brief-true (not a stripe/bar)?
- [ ] Description triggers reliably, including casual/near-miss phrasings?

A skill that passes Level 0 and at least one accent is shippable. A skill that
passes all three accents is exceptional.
