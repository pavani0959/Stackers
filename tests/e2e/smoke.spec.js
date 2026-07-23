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

test('add to cart flow works end-to-end', async ({ page }) => {
  // Navigate directly to a product page
  await page.goto('/product/1');
  
  // Wait for the decision engine to load the product
  const addToCartBtn = page.getByRole('button', { name: /Add to Cart/i });
  await expect(addToCartBtn).toBeVisible({ timeout: 15000 });
  
  // Add to cart
  await addToCartBtn.click();
  
  // Handle potential regret warning modal
  const stillWantBtn = page.getByRole('button', { name: /I still want it/i });
  try {
    await stillWantBtn.waitFor({ state: 'visible', timeout: 2000 });
    await stillWantBtn.click();
  } catch (e) {
    // Modal did not appear, proceed normally
  }
  
  // Click the new Cart icon in the header
  const cartIcon = page.getByRole('button', { name: /View Cart/i });
  await expect(cartIcon).toBeVisible();
  await cartIcon.click();
  
  // Verify we are on the cart page and item is visible
  await expect(page).toHaveURL(/\/cart/);
  await expect(page.getByRole('button', { name: '+' })).toBeVisible();
  
  // Verify we can checkout
  const checkoutBtn = page.getByRole('button', { name: /Complete purchase/i });
  await expect(checkoutBtn).toBeVisible();
  await checkoutBtn.click();
  
  // Verify it redirects to memory (purchase successful)
  await expect(page).toHaveURL(/\/memory/, { timeout: 10000 });
});