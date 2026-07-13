import { expect, test } from '@playwright/test';

test('loads the application splash screen', async ({ page }) => {
  await page.goto('/');

  await expect(
    page.getByRole('heading', {
      name: /Myntra Identity/i,
    }),
  ).toBeVisible();

  await expect(
    page.getByText('Fashion that knows who you are.'),
  ).toBeVisible();

  await expect(
    page.getByRole('button', {
      name: /Begin Your Journey/i,
    }),
  ).toBeVisible();

  await expect(
    page.getByText('Something went wrong'),
  ).toHaveCount(0);
});