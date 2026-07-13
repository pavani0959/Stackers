import { expect, test } from '@playwright/test';

test('loads the application shell', async ({ page }) => {
  const response = await page.goto('/');

  expect(response).not.toBeNull();
  expect(response.ok()).toBeTruthy();

  const root = page.locator('#root');

  await expect(root).toBeVisible();
  await expect(root).not.toBeEmpty();

  await expect(page.locator('body')).not.toContainText(
    'Something went wrong',
  );
});