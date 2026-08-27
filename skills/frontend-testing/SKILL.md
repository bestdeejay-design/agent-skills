---
name: frontend-testing
description: "Scaffold and advise on frontend testing for production readiness, mapped to the Front-End-Checklist Testing category (13 rules). Defines a testing pyramid (unit, integration, E2E, visual, a11y, cross-browser, real-device, perf-budget, mutation, error-monitoring, coverage, mocking, contract) and emits copy-pasteable configs: Playwright config + smoke specs, axe a11y (jest-axe / @axe-core/playwright), Pact contract tests, and a GitHub Actions perf-budget + coverage CI. Use when the user asks for 'frontend testing', 'test strategy', 'e2e', 'visual regression', 'playwright setup', 'playwright test', 'unit test', 'integration test', 'write tests', 'test generation', 'test coverage', 'regression test', 'perf budget CI', 'accessibility testing in CI', 'contract testing', 'mutation testing', 'настрой тесты фронта', or wants tests before a release. Scaffolds & advises only — does not run your full CI; you wire the configs in. Composes with frontend-perfection, frontend-a11y, frontend-performance, /frontend."
license: MIT
metadata:
  author: best
  version: 1.0.0
---

# frontend-testing

Define and scaffold frontend testing for production readiness. Our other
frontend skills (`frontend-perfection`, `frontend-a11y`, `frontend-performance`)
audit a *built* site; they run ZERO tests. This skill closes that gap: it tells
you *what* to test, *which* layer owns each concern, and *hands you the config*
to wire into CI. It is a process/knowledge + scaffolding skill, not a runtime
audit.

## The 13 Testing rules → pyramid layer

Mapped 1:1 from the Front-End-Checklist "Testing" category. Each rule names the
layer it belongs to and the reference file that scaffolds it.

| # | Rule (verbatim priority) | Layer | Scaffold |
|---|---|---|---|
| 1 | Write unit tests [High] | Unit | your unit runner (Vitest/Jest) |
| 2 | Write integration tests for key workflows [High] | Integration | your runner + MSW |
| 3 | Implement end-to-end testing [High] | E2E | `references/playwright.config.ts`, `references/e2e-smoke.spec.ts` |
| 4 | Use visual regression testing [Medium] | Visual | `references/visual-regression.md` |
| 5 | Include accessibility testing [High] | A11y | `references/a11y-test.md` |
| 6 | Test across all major browsers [High] | Cross-browser | `references/playwright.config.ts` (projects) |
| 7 | Test on real mobile devices and viewports [High] | Real-device | `references/playwright.config.ts` (Mobile projects) |
| 8 | Enforce performance budgets in CI [Medium] | Perf-budget | `references/ci-perf-budget.yml` |
| 9 | Use mutation testing to measure how well tests detect bugs [Medium] | Mutation | Stryker config note |
| 10 | Integrate real-time error monitoring in production [High] | Error-monitoring | Sentry note |
| 11 | Maintain test coverage thresholds [Medium] | Coverage | `references/ci-perf-budget.yml` (coverage gate) |
| 12 | Follow mocking best practices [Medium] | Mocking | mocking note |
| 13 | Implement consumer-driven contract testing for API boundaries [Medium] | Contract | `references/contract-test.md` |

## Testing pyramid (shape, not just a list)

```
        /\        E2E (few, critical journeys only)   → Playwright / Cypress
       /  \       Visual regression (key screens)      → snapshot diff
      /----\      Cross-browser + real-device          → Playwright projects
     /      \     A11y (axe in CI)                     → jest-axe / @axe-core/playwright
    /--------\    Integration (key workflows)          → Vitest/Jest + MSW
   /          \   Unit (critical logic, many)          → Vitest/Jest
  /____________\  Contract (API boundaries)            → Pact
```

- **Unit** is the base: fast, many, no browser. Cover *critical functionality*
  only — not every getter.
- **Integration** exercises units wired together (form + validation + state, or
  API route + query). Mock the *network boundary* with MSW, not the unit under test.
- **E2E** covers only the 3–7 journeys that, if broken, are a sev-1 (login,
  checkout, signup, core nav). Everything else is waste.
- **Visual / a11y / cross-browser / real-device** ride on the E2E run — same
  browser, extra assertions. Don't stand them up as separate suites.
- **Contract** guards the frontend↔backend API boundary so a backend change
  can't silently break the UI.

## Decision guide: which test for which job

| Symptom / question | Reach for | Why |
|---|---|---|
| "Is this pure function correct?" | Unit | Fastest feedback, no flake |
| "Do these modules cooperate?" | Integration | Catches wiring bugs units miss |
| "Can a real user complete the flow?" | E2E (Playwright) | Only layer that proves the journey |
| "Did the layout shift unexpectedly?" | Visual regression | Pixel diff beats eyeballs |
| "Is it usable by AT users?" | A11y (axe) | Automated WCAG subset in CI |
| "Does it work in Firefox/Safari/Edge?" | Cross-browser projects | Engine differences are real |
| "Does it break on a phone?" | Real-device / mobile emulation | Touch + viewport bugs |
| "Did a backend change break the UI?" | Contract (Pact) | Fails before prod |
| "Will my tests actually catch bugs?" | Mutation (Stryker) | Coverage % lies; mutations don't |
| "Is it fast enough to ship?" | Perf budget in CI | Fails build on regression |
| "What blew up in prod?" | Error monitoring (Sentry) | Post-deploy truth |

Rule of thumb: **write the cheapest test that can fail for the right reason.**
Don't E2E a pure function; don't unit-test a user journey.

## Composition with sibling skills

- `frontend-perfection` — audits a *built* site (Lighthouse, contrast, tokens,
  a11y subset). This skill adds the *test suite* that prevents regressions the
  audit would otherwise catch late. Scaffold tests here first, then run
  `frontend-perfection` to verify the result stays green.
- `frontend-a11y` — deep accessibility. This skill's `references/a11y-test.md`
  is the *CI gate* (axe in the pipeline); `frontend-a11y` is the *manual/expert*
  pass. They share axe-core; don't duplicate the audit — wire the gate.
- `frontend-performance` — measures field/lab perf. This skill's
  `references/ci-perf-budget.yml` *fails the build* when budgets slip;
  `frontend-performance` tells you *why* and *how to fix*.
- `/frontend` — orchestrator. Routes the testing/QA domain to this skill during
  a build or pre-release handoff.

Do NOT reimplement perf/security/a11y audits here — point to the siblings.

## How to scaffold (workflow)

1. **Decide the layers you need.** Start from the pyramid; for a typical SPA:
   unit (Vitest) + integration (Vitest + MSW) + E2E (Playwright) + a11y gate +
   perf budget in CI. Add visual/contract/mutation when the cost is justified.
2. **Scaffold the configs** into the project with the bundled script — it copies
   the reference files deterministically and prints exactly what it wrote, so the
   run is *evidence* (a config that was never placed is a draft, not a scaffold):
   ```bash
   python3 scripts/scaffold.py --target /path/to/project --layers playwright,e2e,a11y,ci
   # expected: one "copied references/<file> -> <dest>" line per layer;
   #           "Scaffolded N file(s) into <target>"; exit 0
   #           exit 2 if --target does not exist; exit 1 if a source is missing
   ```
   The script maps each layer to its reference file and destination (the reference
   files stay the source of truth if you prefer to place them by hand):
   - `playwright` → `references/playwright.config.ts` → `playwright.config.ts`
   - `e2e` → `references/e2e-smoke.spec.ts` → `e2e/e2e-smoke.spec.ts`
   - `a11y` → `references/a11y-test.md` → `e2e/a11y-test.md`
   - `visual` → `references/visual-regression.md` → `e2e/visual-regression.md`
   - `ci` → `references/ci-perf-budget.yml` → `.github/workflows/perf-budget.yml`
   - `contract` → `references/contract-test.md` → `tests/contract/contract-test.md`

   Copy only the layers you need; pass `--layers` to pick them.
3. **Install only what you use.** Baseline (E2E + a11y + unit):
   ```bash
   npm i -D @playwright/test @axe-core/playwright vitest @vitest/coverage-v8 msw
   npx playwright install --with-deps chromium firefox webkit
   ```
4. **Wire the CI gate** (perf budget + coverage) from `references/ci-perf-budget.yml`.
5. **Run locally to prove the scaffold is green** (evidence gate below) before
   handing configs back.

## Evidence gates (show the command, show the expected shape)

You must be able to demonstrate the scaffold runs, not just that files exist.

**Unit / integration (Vitest):**
```bash
npx vitest run --coverage
# expected: ✓ N passed; coverage summary; exit 0 when ≥ threshold
```

**E2E (Playwright):**
```bash
npx playwright test --project=chromium
# expected: Running 6 tests using 1 worker; N passed; exit 0
# on failure: trace + screenshot retained (see config use:)
```

**A11y gate (axe in Playwright):**
```bash
npx playwright test e2e/a11y.spec.ts
# expected: no violations; exit 0. On violation: list of axe rule ids + nodes
```

**Mutation (Stryker) — critical logic only:**
```bash
npx stryker run
# expected: Mutation score ≥ your threshold (e.g. 80%); report shows killed/survived
```

**Perf budget (CI only, but locally reproducible):**
```bash
npx lhci autorun --collect.url=http://localhost:3000
# expected: all budgets met; exit 0. Breach → non-zero exit fails the build
```

Report the exact command you ran, the real output (or its shape), and the exit
code. A config that has never been executed is not "scaffolded" — it's a draft.

## Engagement / before-after report convention

When you deliver a testing scaffold, write a short report:

- **Input**: repo path, framework detected, which layers were missing.
- **Added**: list of files created (with paths) and the layers they cover.
- **Commands**: the exact commands to run each layer locally.
- **CI**: what the workflow enforces (budgets, coverage threshold, browsers).
- **Expected**: pass/fail shape per layer (from evidence gate).
- **Not done (non-goals)**: we did not run your full CI, did not pick a backend
  provider for Pact, did not tune every threshold — those are the user's calls.
- **Next**: which sibling skill to run next (perf / a11y / perfection).

## Constraints / non-goals

- This skill **scaffolds & advises**. It does NOT run the user's full CI, deploy,
  or stand up their backend provider. It produces configs they wire in.
- Framework-agnostic where possible: the Playwright example is the reference
  implementation; unit/integration snippets adapt to Vitest/Jest/Mocha.
- Do NOT reimplement performance/security/a11y *audits* — delegate to the sibling
  skills. This skill owns the *testing/QA domain* only.
- No external Front-End-Checklist MCP dependency; the 13 rules are inlined above.
- Thresholds (coverage %, mutation score, Lighthouse numbers) are placeholders —
  set them with the user; don't ship arbitrary numbers as policy.

## References index

- `references/playwright.config.ts` — multi-project config (devices, baseURL, trace).
- `references/e2e-smoke.spec.ts` — critical-journey E2E example.
- `references/visual-regression.md` — screenshot-diff approach + tooling.
- `references/a11y-test.md` — jest-axe and @axe-core/playwright snippets.
- `references/ci-perf-budget.yml` — GitHub Actions perf budget + coverage gate.
- `references/contract-test.md` — Pact consumer-driven contract example.
