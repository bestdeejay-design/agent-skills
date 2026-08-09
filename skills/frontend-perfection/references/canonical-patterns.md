# frontend-perfection — Canonical Patterns

Deep dive behind `scripts/audit.js` + `scripts/meta_audit.py`. Grounded in
canonical sources (August 2026); every URL is a live, real-world reference:

- **Lighthouse (Google)** — <https://github.com/GoogleChrome/lighthouse>
  — the audit engine this skill wraps on the Node API
- **chrome-launcher (Google)** — <https://github.com/GoogleChrome/chrome-launcher>
  — the stable CDP launch mechanism this skill uses instead of Playwright internals
- **Anthropic official skills (frontend-design)** — <https://github.com/anthropics/skills>
  — reference for agent-side frontend workflow skills
- **obra/superpowers (perfection)** — <https://github.com/obra/superpowers>
  — reference for "perfection"-style high-bar agent skills
- **Open Graph protocol** — <https://ogp.me/>
  — the social share spec the OG-block implements
- **WCAG 2.2 (W3C)** — <https://www.w3.org/TR/WCAG22/>
  — the contrast (1.4.3) and other rules the audit computes, not eyeballs

---

## 1. Why a stable runner (not Playwright/CDP internals)

Legacy implementations grabbed the CDP port from private Playwright fields
(e.g. `browser._impl_obj._connection._transport._ws_url`). These are
**unsupported internals** and break silently when the transport changes
(WebSocket → PipeTransport). The canonical engineering answer, used by
Lighthouse's own tooling, is `chrome-launcher`: it launches the real Chrome,
returns `{ port, pid }` via its public API, and requires no private fields.
This skill builds on that contract and therefore survives upstream refactors.

**Lighthouse ≥ 13**: the package no longer exports the function directly as
the module (`require("lighthouse")` is a namespace). Canonical call is
`require("lighthouse").default(...)`. The skill does both: feature-detect the
shape, then call whatever is a function. This is the same fallback pattern
Google uses in its own docs for dual ESM/CJS exports.

## 2. Dependency isolation — canonical layout

Global `npm install -g` historically did not resolve from `require()` on
Node ≥ 20/22 (global prefix lives outside `NODE_PATH`). The canonical
patterns the skill implements (all three, in order):

- local `node_modules` next to the script (self-contained, `npm i -g` not needed)
- `NODE_PATH` (the documented npm/Node escape hatch for global resolution)
- `npm root -g` auto-discovery

This mirrors how Lighthouse's CLI bundles its deps and how
`PROJECT_ROOT/node_modules` hoisting works in npm workspaces — no module is
ever assumed "just available".

## 3. Techniques the analogues have that this implementation lacks

- **Lighthouse CI server/cluster mode** (Google `lighthouse-ci`,
  <https://github.com/GoogleChrome/lighthouse-ci>): persistent server,
  regression budgets, GitHub action integration. This skill is a local,
  single-run runner — there is no `assert` budget deck or PR blamer.
- **Screenshot diffing on layout changes** (visual regression tooling like
  `backstopjs`): pixel-level before/after on the same page. This skill
  verifies metrics and checks, not pixels.
- **Cumulative browser profile budgets** (`bundle-buddy`/`size-limit`-style JS
  size gates): the Lighthouse JS-bundle audit (`unused-javascript`) is
  surfaced as a failed audit id, but there is no bytes regression suite.
- **Full WCAG 2.2 scope** (color-contrast-enhanced AA/AAA, non-text
  contrast 1.4.11, target-size 2.5.5): the skill implements the 4.5:1 text
  branch (1.4.3) via computed luminance; 3:1 UI/component and AAA are
  explicitly out of scope.
- **Real social-cache verification harness**: ogp.me documents the tags, but
  nothing canonical automates "is my preview right in WhatsApp *today*";
  the skill bakes the *known constraints* (crop-safe zone ~640px, URL change
  to bust caches, forced reflow before capture) into the workflow instead.

## 4. Determinism contract

- `meta_audit.py`: offline, no network, no wall-clock dependence; same
  files → same report. Report field order is stable (checks in fixed id
  order, summary block last).
- `audit.js`: Lighthouse itself is non-deterministic across runs (CPU, cache,
  Chrome version), so the *scores* are best-effort; the *failed audit ids*
  (what to fix) are the stable contract. `--threshold` gates exit code
  machine-checkably.

## 5. Exit-code contract

- `audit.js`: `0` = all measured categories ≥ threshold; `1` = below; `2` =
  runner error (missing module / URL unreachable / crash).
- `meta_audit.py`: `0` = no violations; `1` = violations found; `2` = usage /
  I/O error (missing file args). Downstream tooling may therefore `&&`-chain
  audit passes.

## Sources

- GoogleChrome/lighthouse: <https://github.com/GoogleChrome/lighthouse>
- GoogleChrome/chrome-launcher: <https://github.com/GoogleChrome/chrome-launcher>
- GoogleChrome/lighthouse-ci: <https://github.com/GoogleChrome/lighthouse-ci>
- anthropics/skills (frontend-design): <https://github.com/anthropics/skills>
- obra/superpowers: <https://github.com/obra/superpowers>
- Open Graph protocol: <https://ogp.me/>
- WCAG 2.2: <https://www.w3.org/TR/WCAG22/>