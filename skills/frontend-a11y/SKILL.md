---
name: frontend-a11y
description: "Deep accessibility audit of a webpage or static HTML/CSS, mapped to the Front-End-Checklist 'Accessibility' category (95 rules). Specialist complement to frontend-perfection (which covers only ~12 basic a11y rules). Runs offline static checks (Python stdlib) for structure, ARIA validity, headings, landmarks, tables, forms, media tracks, lists, and CSS signals; documents an optional Playwright+axe-core runtime runner for contrast, focus order, live regions, modal traps, and reflow; and lists manual screen-reader checks. Use for 'accessibility audit', 'a11y check', 'wcag', 'axe', 'screen reader test', 'contrast', 'keyboard navigation', 'focus trap', 'aria', 'accessibility testing', 'проверь доступность', or when the /frontend orchestrator or mobile-frontend needs the deep a11y domain."
license: MIT
metadata:
  author: best
  version: 1.0.0
when_to_use: "Use to audit/polish accessibility deeply: 'accessibility audit', 'a11y check', 'wcag', 'axe', 'screen reader test', 'contrast', 'keyboard navigation', 'focus trap', 'aria', 'accessibility testing', 'проверь доступность'. Examples: 'audit this page for WCAG violations', 'check the modal for keyboard traps', 'run axe on the homepage'."
---

# frontend-a11y

`frontend-perfection` owns measurable *layout/perf/SEO/tokens* polish and only
touches ~12 basic a11y rules (img-alt, button/link-name, form-label, aria-valid,
landmark-unique, plus lang/dir/headings). This skill owns the **deep**
accessibility domain — the full Front-End-Checklist *Accessibility* category
(**95 rules**), split into three checkable tiers so the right tool runs at the
right time.

- **static** — offline Python (`scripts/a11y_audit.py`), no browser, no network.
  Markup structure, ARIA validity, headings, landmarks, tables, forms, media
  tracks, lists, and a few CSS signals.
- **runtime** — Playwright + axe-core (`scripts/a11y_axe.mjs`, optional npm
  deps). Computed contrast, ARIA parent/child relationships, live regions, focus
  order, modal traps, reflow at 400% zoom, touch targets.
- **manual** — screen-reader testing and human-judgement rules (NVDA/JAWS/
  VoiceOver/TalkBack, plain language, seizure flashing). Checklist-only; the
  report records them as `severity: manual` so they are not silently skipped.

## When to use

- User asks to "audit accessibility", "check WCAG", "run axe", "test keyboard
  navigation", "find focus traps", "verify contrast", "проверь доступность".
- The `/frontend` orchestrator routes the a11y domain here; `mobile-frontend`
  calls it for touch-target / orientation / reflow checks.
- After `frontend-perfection` passes its 12 basic rules and you need the other 83.

## Composition

- **vs `frontend-perfection`** — it owns layout/perf/SEO/tokens + 12 a11y rules
  (incl. computed contrast). This skill owns the remaining 83 a11y rules. Do NOT
  re-implement raw-hex token checks or computed-contrast here — those live in
  `frontend-perfection`/`a11y_axe.mjs`. Run `frontend-perfection` first for the
  shared baseline, then `frontend-a11y` for depth.
- **vs `mobile-frontend`** — it calls `frontend-a11y` for the mobile-a11y rules
  (touch target size, orientation, reflow at 400%, reduced motion).
- **vs `/frontend`** — the orchestrator runs `frontend-perfection` + this skill
  + (optionally) `a11y_axe.mjs` for the full a11y picture.

## Workflow

1. **Locate the target** — static `index.html` (+ CSS) or a served URL.
2. **Run the static audit** (always, offline):
   ```bash
   python3 scripts/a11y_audit.py --html index.html --css main.css css/demo.css --out a11y-static.json
   ```
   Exit `0` = no violations, `1` = violations, `2` = runner error.
3. **Run the runtime audit** (optional, needs deps) on a served URL:
   ```bash
   npm i playwright axe-core && npx playwright install chromium
   node scripts/a11y_axe.mjs --url http://localhost:8377/ --out a11y-axe.json
   ```
4. **Fix by audit id** — every fix references the id it closes
   (`a11y:img-alt`, `a11y:landmark-main`, `a11y:axe:color-contrast`, …).
5. **Re-audit until green** on static; resolve runtime `FAIL` rows; record
   `manual` rows as verified-or-pending in the report.
6. **Write the before/after report** (see convention below): input paths, exact
   commands, real output, interpretation, and what was deliberately NOT done.

## audit-id scheme (95 rules)

Each checklist rule maps to a stable id tagged `static` / `runtime` / `manual`.
Severity (critical/high/medium/low) mirrors the checklist priority and is
emitted per check in the JSON report.

### static — offline Python (`a11y_audit.py`)

| id | checklist rule |
|---|---|
| `a11y:img-alt` | Images have alt text |
| `a11y:img-button-alt` | Image buttons (`input[type=image]`) have alt |
| `a11y:img-alt-redundant` | No redundant "image/photo" words in alt |
| `a11y:button-name` | Buttons have accessible names |
| `a11y:link-name` | Links have accessible names |
| `a11y:link-distinct` | Identical link text → identical destination |
| `a11y:link-empty-broken` | Links are not empty/broken |
| `a11y:link-text-descriptive` | Descriptive link text (not "click here") |
| `a11y:form-label` | Form controls have associated labels |
| `a11y:form-label-single` | Exactly one label per field |
| `a11y:input-name` | All inputs have accessible names |
| `a11y:select-name` | Selects have accessible names |
| `a11y:toggle-name` | Toggle fields (checkbox/radio/switch) named |
| `a11y:aria-valid` | ARIA attribute names are valid |
| `a11y:aria-valid-value` | ARIA attribute values are valid tokens |
| `a11y:aria-deprecated-role` | No abstract/deprecated ARIA roles |
| `a11y:aria-role-valid` | ARIA role values are valid |
| `a11y:landmark-unique` | Landmarks are unique |
| `a11y:landmark-main` | Exactly one `<main>` landmark |
| `a11y:landmark-nav` | Multiple `<nav>` have distinct labels |
| `a11y:landmark-regions` | Landmark regions used correctly |
| `headings:single-h1` | Exactly one h1 |
| `headings:order` | Logical heading order (no skipped levels) |
| `headings:non-empty` | Headings contain text |
| `html:lang` | `<html lang>` present (BCP 47) |
| `html:dir-rtl` | RTL languages set `dir="rtl"` |
| `html:lang-xml-match` | `lang` matches `xml:lang` |
| `a11y:skip-link` | Skip-to-content link present |
| `a11y:iframe-title` | iframes/frames have titles |
| `a11y:table-headers` | Data tables have `<th>` headers |
| `a11y:table-header-scope` | Headers scoped to cells |
| `a11y:table-cell-headers` | Cells linked to headers via ids |
| `a11y:table-unique-name` | Tables have unique accessible names |
| `a11y:table-semantic` | Semantic table markup (caption/role) |
| `a11y:video-captions` | `<video>` has `<track kind="captions">` |
| `a11y:video-audio-desc` | `<video>` has `<track kind="descriptions">` |
| `a11y:autofocus-absent` | No `autofocus` on fields |
| `a11y:aria-hidden-body-absent` | No `aria-hidden` on `<body>` |
| `a11y:focusable-in-aria-hidden-absent` | No focusable child in `aria-hidden` |
| `a11y:list-structure` | `<li>` inside ul/ol/menu |
| `a11y:list-correct` | ul/ol contain only `<li>` |
| `a11y:list-semantic` | Semantic list elements used |
| `a11y:dl-structure` | Valid `<dl>` (only dt/dd) |
| `a11y:dl-wrap` | dt/dd wrapped in `<dl>` |
| `a11y:decorative-hidden` | Decorative elements hidden from AT |
| `a11y:object-alt` | `<object>` has alternative content |
| `a11y:meta-refresh-absent` | No meta refresh redirect |
| `a11y:accesskey-unique` | Unique `accesskey` values |
| `a11y:unique-id` | Unique element ids |
| `a11y:aria-ref-unique` | ARIA-referenced ids unique/exist |
| `a11y:tabindex-appropriate` | No positive `tabindex` |
| `a11y:role-text-no-focusable` | `role="text"` has no focusable child |
| `a11y:dialog-name` | Dialogs have accessible names |
| `a11y:meter-name` | Meter elements named |
| `a11y:progress-name` | Progress bars named |
| `a11y:tooltip-name` | Tooltips named |
| `a11y:treeitem-name` | Tree items named |
| `a11y:command-name` | ARIA command elements named |
| `a11y:interactive-name` | Role-based interactive els named |
| `a11y:autoplay-media` | No autoplaying media |
| `a11y:paste-allowed` | Pasting allowed in inputs |
| `a11y:autocomplete-auth` | Auth inputs support autocomplete |
| `a11y:links-in-text-distinguishable` | Links distinct beyond color (CSS) |
| `a11y:reduced-motion` | Respects `prefers-reduced-motion` (CSS) |
| `a11y:instant-anchor-scroll` | Instant anchor-scroll option (CSS) |

### runtime — Playwright + axe-core (`a11y_axe.mjs`)

| id (prefixed `a11y:axe:`) | checklist rule |
|---|---|
| `color-contrast` | Minimum color contrast (WCAG 1.4.3) |
| `aria-required-parent` | ARIA roles contained by required parent |
| `aria-required-children` | ARIA roles contain required children |
| `aria-allowed-attr` | Only allowed ARIA attrs per role |
| `label-content-name-mismatch` | Visible label matches accessible name |
| `focus-order-semantics` / `tablist` | Logical focus order |
| `focus-not-obscured` | Focused el not hidden by sticky chrome |
| `modal-aria` / `focus-trapping` | Modal dialog keyboard accessible |
| `aria-live` / `region` | Dynamic content announced (live regions) |
| `scrollable-region-focusable` | Reflow at 400% zoom |
| `target-size` | Sufficient touch target size |
| `orientation` | Portrait + landscape support |
| `blink` / `css-animation-no-pause` | No seizure-triggering flashing |

### manual — screen reader / human judgement

| id | checklist rule |
|---|---|
| `a11y:screen-reader-test` | Test with NVDA/JAWS/VoiceOver/TalkBack |
| `a11y:content-without-css` | Usable with author CSS disabled |
| `a11y:sensory-only-instructions` | No sensory-only instructions |
| `a11y:images-of-text` | Avoid images of text |
| `a11y:scrolljacking` | No hijacked scroll |
| `a11y:redundant-entry` | No redundant entry in a flow |
| `a11y:help-consistent` | Help in consistent location |
| `a11y:session-timeout` | Warn before session timeout |
| `a11y:seizure-flashing` | No >3 flashes/sec |
| `a11y:parallax-alt` | Alternatives to parallax |
| `a11y:inclusive-language` | Inclusive language |
| `a11y:plain-language` | Plain language |
| `a11y:label-name-match` | Visible label ⊆ accessible name |

## Scripts

### `a11y_audit.py` (static, offline, stdlib)

Reads one or more `--html` files and optional `--css`. Emits a JSON report
(`--out` / `--json`) where every check has `id`, `title`, `severity`, `ok`,
`detail`, `file`. Exit codes: `0` no violations, `1` violations, `2` runner
error. No PyYAML, no `requests`, no network.

```bash
python3 scripts/a11y_audit.py --html index.html --css main.css --out a11y.json
python3 scripts/a11y_audit.py --html a.html b.html --json   # stdout JSON
```

### `a11y_axe.mjs` (runtime, optional deps)

Real Chromium via Playwright; injects `axe-core` and runs the WCAG tag set.
Documents required deps in its header; it does NOT run at build time. Exit codes
mirror the static script (`0`/`1`/`2`). `incomplete` axe results are emitted as
`severity: manual` so they surface for human confirmation instead of being
counted as hard failures.

```bash
npm i playwright axe-core && npx playwright install chromium
node scripts/a11y_axe.mjs --url http://localhost:8377/ --out a11y-axe.json
```

## Before/after report convention

Bind every claim to an audit id. Format:

```
## Accessibility audit — <project>
Inputs: index.html, main.css
Commands:
  python3 scripts/a11y_audit.py --html index.html --css main.css --out a11y.json
  (exit 1, 14 violations)

Before: 14 violations (a11y:img-alt ×3, headings:order, a11y:landmark-main, …)
Fixes:
  - a11y:img-alt: added alt to hero/banner/icons
  - headings:order: h1→h3 gap closed (inserted h2)
  - a11y:landmark-main: removed duplicate <main>
After: 0 violations (exit 0)

Runtime (axe): 2 FAIL (color-contrast on footer), 3 manual pending
Manual: screen-reader pass pending (NVDA) — NOT done this run
Not done: computed-contrast (owned by frontend-perfection), design tokens.
```

## Constraints / non-goals

- `a11y_audit.py` is offline and stdlib-only — no PyYAML, no `requests`, no
  network, no browser. It MUST stay runnable with only `python3`.
- Computed color contrast and design-token hex checks are **out of scope** here
  (owned by `frontend-perfection` and `a11y_axe.mjs`). Do not add them to the
  static script.
- `a11y_axe.mjs` requires `npm i playwright axe-core` + `npx playwright install
  chromium`; it is documented, not executed, at build time.
- Do NOT depend on the external Front-End-Checklist MCP server; the 95-rule
  mapping is embedded above.
- Fix at the root (real semantics), never by hiding audits with `aria-hidden`
  spray or `tabindex=-1` hacks.
- Manual rules are recorded, never silently dropped — they appear as
  `severity: manual` in the report.
