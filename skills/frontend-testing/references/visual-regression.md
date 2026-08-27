# Visual regression testing (rule 4)

Capture screenshots of components/pages and diff them against approved
baselines so unintended visual changes are caught before production.

## Approach

1. **Pick a tool.** Three common options, cheapest first:
   - **Playwright `toHaveScreenshot()`** — zero extra deps, stores PNG baselines
     in `e2e/**/__screenshots__/`, updates with `--update-snapshots`. Good enough
     for most teams.
   - **jest-image-snapshot** — Jest/Vitest matcher, same idea, no browser needed
     if you render to canvas/SSR.
   - **Percy / Argos / Chromatic** — managed, per-pixel + anti-flake + review UI.
     Best when you need a human approval workflow across PRs.

2. **Stabilize the page before shooting** — fixed viewport, seeded data, disable
   animations (`prefers-reduced-motion`), freeze fonts/timestamps. Flaky visuals
   are the #1 cause of noise.

3. **Scope baselines** to key screens + a few components, not every route.

## Playwright example (no extra deps)

```ts
// e2e/visual.spec.ts
import { test, expect } from '@playwright/test';

test('homepage matches baseline', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveScreenshot('homepage.png', { fullPage: true });
});

test('pricing card matches baseline', async ({ page }) => {
  await page.goto('/pricing');
  await expect(page.getByTestId('pricing-card')).toHaveScreenshot('pricing-card.png');
});
```

Run / update:
```bash
npx playwright test e2e/visual.spec.ts            # fails on diff
npx playwright test e2e/visual.spec.ts --update-snapshots   # approve new baseline
```

## Managed-service example (Percy)

```ts
import { test } from '@playwright/test';
import percySnapshot from '@percy/playwright';

test('homepage', async ({ page }) => {
  await page.goto('/');
  await percySnapshot(page, 'Homepage');
});
```

Commit baselines to VCS (or the service) and treat a diff as a build-blocking
event in CI. Do NOT rely on visual diffing to catch logic bugs — that is what
E2E/unit own.
