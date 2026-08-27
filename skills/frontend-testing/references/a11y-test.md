# Accessibility testing in CI (rule 5)

Automate WCAG checks with axe-core. Two drop-in patterns: axe inside Playwright
(best for E2E + a11y in one run) and jest-axe (best for component unit tests).

## Pattern A — @axe-core/playwright (rides on your E2E run)

```ts
// e2e/a11y.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('accessibility', () => {
  test('homepage has no axe violations', async ({ page }) => {
    await page.goto('/');
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();
    expect(results.violations).toEqual([]);
  });

  test('login form has no axe violations', async ({ page }) => {
    await page.goto('/login');
    const results = await new AxeBuilder({ page })
      .include('main')
      .analyze();
    expect(results.violations).toEqual([]);
  });
});
```

Run: `npx playwright test e2e/a11y.spec.ts` → exit 0 when clean; on violation it
prints the axe rule id + the offending nodes.

## Pattern B — jest-axe (component-level, no browser)

```ts
// src/Button.a11y.test.tsx
import { render } from '@testing-library/react';
import { axe } from 'jest-axe';
import { Button } from './Button';

test('Button has no a11y violations', async () => {
  const { container } = render(<Button>Save</Button>);
  expect(await axe(container)).toHaveNoViolations();
});
```

Install: `npm i -D jest-axe @types/jest-axe`.

## Notes

- Keep the tag set tight (`wcag2a`, `wcag2aa`) to avoid noise; widen per the
  project's compliance target.
- axe is an *automated subset* of WCAG — pair with the `frontend-a11y` expert
  pass (screen readers, focus order) for full coverage. This file is the CI gate.
- `toEqual([])` fails the build on any violation; that is the point.
