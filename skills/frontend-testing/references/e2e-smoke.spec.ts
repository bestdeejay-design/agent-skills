import { test, expect } from '@playwright/test';

/**
 * Copy to e2e/smoke.spec.ts. Replace journeys with YOUR critical paths.
 * E2E (rule 3): cover only the 3-7 journeys that are sev-1 if broken.
 * Run: npx playwright test e2e/smoke.spec.ts --project=chromium
 */
test.describe('critical user journeys', () => {
  test('homepage loads and primary CTA is reachable', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/.+/);
    const cta = page.getByRole('link', { name: /get started/i });
    await expect(cta).toBeVisible();
    await cta.click();
    await expect(page).toHaveURL(/\/signup|\/start/);
  });

  test('auth: login rejects bad credentials', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('bad@example.com');
    await page.getByLabel(/password/i).fill('wrong');
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page.getByRole('alert')).toContainText(/invalid/i);
  });

  test('checkout: empty cart blocks payment', async ({ page }) => {
    await page.goto('/cart');
    await expect(page.getByText(/your cart is empty/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /pay/i })).toBeDisabled();
  });
});
