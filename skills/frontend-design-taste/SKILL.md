---
name: frontend-design-taste
description: "Give a website a distinctive, deliberate visual direction that does not read as templated AI output. Grounds in the subject, proposes a compact token system (palette 4-6 hexes, display/body/utility type roles, layout concept, ONE signature element), runs a uniqueness gate against the three AI-default looks, and rewrites copy from the user's side of the screen. Includes a condensed worked example (ishotgirls). No scripts. Triggers: 'design direction', 'design taste', 'make it look good', 'not templated', 'redesign with taste', 'visual identity', 'aesthetic direction', 'design brief', 'anti-templated design', 'signature element'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.0.1"
compatibility: "No scripts; design judgment. Optionally a browser for visual verification"
when_to_use: "Use when user wants a distinctive visual direction (not templated): 'design direction', 'design taste', 'make it look good', 'not templated', 'redesign with taste', 'visual identity', 'aesthetic direction', 'design brief', 'anti-templated design'. Examples: 'give this landing page a real visual identity', 'redesign my site so it stops looking like AI'."
---

# Frontend Design Taste — distinctive direction, not templated defaults

Approach this as the design lead at a small studio known for giving every client a
visual identity that could not be mistaken for anyone else's. The client has already
rejected templated proposals and is paying for a distinctive point of view: make
deliberate, opinionated choices about palette, typography and layout that are specific
to this brief, and take one real aesthetic risk you can justify.

This skill defines the DIRECTION. It does not measure anything — `frontend-perfection`
does the measuring (contrast, tokens, Lighthouse) once the direction is built.

## When to use

- User asks to "make it look good", "redesign with taste", "not look templated",
  "give it a visual identity", "design direction for this page".
- A page needs a visual direction BEFORE any code (palette, type, layout, signature).
- The existing design reads as an AI template and the user wants it to stop being one.

## Do NOT use

- To audit/fix an existing page (contrast, SEO meta, Lighthouse, raw-hex tokens) — that is `frontend-perfection`.
- For SEO / Core Web Vitals / schema.org — that is `seo-toolkit`.
- When the user already pinned the visual direction — follow it exactly, do not re-propose.

## The three AI defaults to avoid

AI-generated design currently clusters around three looks. All three are legitimate for
SOME briefs, but they are defaults, not choices, and they appear regardless of subject:

1. **Warm cream background** (~#F4F1EA) + high-contrast serif display + terracotta accent.
2. **Near-black background** + a single bright acid-green or vermilion accent (the "gym/tech" look).
3. **Broadsheet layout** — hairline rules, zero border-radius, dense newspaper columns.

Where the brief pins one of these looks, follow it. Where an axis is free, do NOT spend
that freedom on a default.

## Design principles

- **Hero is a thesis.** Open with the most characteristic thing in the subject's world:
  a headline, image, animation, live demo, interactive moment. A big number + small
  label + gradient accent is the template answer — only use it if it's truly the best.
- **Typography carries personality.** Pair display and body deliberately, not the same
  families you reach for on every project. Set a real type scale with intentional
  weights/widths/spacing. Make the type treatment memorable, not a neutral carrier.
- **Structure is information.** Numbering, eyebrows, dividers should encode something
  true about the content. Numbered markers (01/02/03) only when content is a real
  sequence — a process or timeline where order carries meaning.
- **Motion serves the subject.** An orchestrated moment lands harder than scattered
  effects; sometimes less is more — extra animation reads as AI-generated.
- **Complexity matches the vision.** Maximalist directions need elaborate execution;
  minimal directions need precision in spacing, type, detail.
- **Copy is design material.** Words exist to make the page easier to understand and
  use, never decoration.

## Process

1. **Ground it in the subject.** If the brief doesn't pin the subject, pin it yourself:
   one concrete subject, its audience, the page's single job. The subject's world —
   materials, instruments, artifacts, vernacular — is where distinctive choices come from.
2. **Brainstorm a compact token system** (one short plan, not a wall):
   - **Palette**: 4–6 named hex values.
   - **Type**: 2+ roles — a characterful display face used with restraint, a complementary
     body face, a utility/mono face for captions or data.
   - **Layout**: a concept in 1–2 sentences + an ASCII wireframe to compare.
   - **Signature**: the ONE element this page will be remembered by, embodying the brief.
3. **Run the uniqueness gate.** Review the plan against the brief. If any part reads as
   the generic default you'd produce for any similar page — revise it, say what changed
   and why. Only after the plan passes, build.
4. **Build to the plan.** Every color and type decision derives from the tokens. Mind CSS
   specificity (element + class selectors cancelling each other on paddings/margins).
5. **Critique and cut.** Spend boldness in one place; keep everything else quiet. Cut any
   decoration that does not serve the brief. Take one justified risk. "Before leaving the
   house, remove one accessory."

## Copy rules

- Write from the **user's side of the screen**: a person manages notifications, not webhook config.
- **Active voice as default**: "Save changes", not "Submit". Keep the same name through a
  flow — a "Publish" button produces a "Published" toast.
- **Errors don't apologize and are never vague**; empty screens invite action.
- Specific beats clever. Plain verbs, sentence case, no filler, one job per element.

## Quality floor (handoff to frontend-perfection)

- Responsive down to mobile; visible keyboard focus (`:focus-visible`); `prefers-reduced-motion` respected.
- **Long pages need a way back to top**: the logo links to the top and/or a floating
  scroll-to-top button (arrow in a circle, bottom-right, appears after scrolling,
  `aria-label`, focusable). Enforced by `frontend-perfection` as `nav:back-to-top`.
- Then verify measurably (this skill doesn't measure — hand to `frontend-perfection`):
  computed contrast ≥ 4.5:1, fonts actually loaded, theme toggle works, zero raw hex outside tokens.

## Worked example — ishotgirls (condensed)

Subject: "fitness inspiration" platform around Instagram models. Grounding: the world is
Instagram grids, gym-as-stage, streaks, PRs, transformation — not generic fitness.
Default trap: original was Montserrat+Lora sidebar with "Discover / Find Your Idol /
Transform Your Life" — the template answer.

- **Palette**: ink `#161A2E` + bone `#F4F0E4` + signal amber `#FFB347` + deep teal `#0F766E`
  (deliberately NOT the cream+serif+terracotta, NOT near-black+acid).
- **Type**: Archivo Black (condensed athletic display, replaces the Lora serif default) +
  Montserrat body + JetBrains Mono for data (streaks, PRs).
- **Layout**: hero as scoreboard — real numbers (47 models / 214 transformations / 12 480
  workouts) instead of motivational copy.
- **Signature**: an Instagram grid 3×3 as the hero element; hovering a cell reveals the
  model's streak/PR.
- **Copy rewrite**: "Follow your first model" / "See the routine" / "Worn by the roster"
  / "Train · Fuel · Recover" — active, user-side, specific.
- **Uniqueness gate**: a generic "make a fitness landing" prompt yields near-black + acid
  green (default 2). Grid-motif + amber flash + scoreboard are choices for THIS subject. Pass.
- **Verified**: contrast 15:1, three fonts loaded, responsive, theme toggle, reduced-motion.

## Canonical analogue

Method origin: `anthropics/skills` → `frontend-design` —
<https://github.com/anthropics/skills/tree/main/skills/frontend-design>.
Adapted and neutralized for opencode/Sisyphus; the "AI default looks" and uniqueness
gate are kept verbatim in spirit.
