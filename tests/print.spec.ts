import { test, expect } from '@playwright/test';

test.describe('Print workflows', () => {
  test.beforeEach(async ({ page }) => {
    await page.context().addInitScript(() => {
      const nativePrint = window.print;
      window.print = function printStub() {
        (window as any).__printCalls = ((window as any).__printCalls || 0) + 1;
        return nativePrint.call(window);
      };
    });
  });

  test('homepage "Print selected" assembles print markup for visible cards', async ({ page }) => {
    await page.goto('/index.html');
    await page.waitForSelector('.category-section');

    const filters = page.locator('#category-filters input[type="checkbox"]');
    const filterCount = await filters.count();
    expect(filterCount).toBeGreaterThan(0);

    for (let i = 0; i < filterCount; i++) {
      const filter = filters.nth(i);
      if (await filter.isChecked()) {
        await filter.uncheck();
      }
    }

    const printSelectedButton = page.locator('#print-visible-btn');
    await expect(printSelectedButton).toBeDisabled();

    await filters.first().check();
    await expect(printSelectedButton).toBeEnabled();

    const visibleCardCount = await page.locator('.card-preview').count();
    expect(visibleCardCount).toBeGreaterThan(0);

    const [popup] = await Promise.all([
      page.waitForEvent('popup'),
      printSelectedButton.click()
    ]);
    await popup.waitForLoadState('load');

    await expect(popup.locator('.print-card-group')).toHaveCount(visibleCardCount);
    await expect(popup.locator('link[href$="css/style.css"]')).toHaveCount(1);
    const printCalls = await popup.evaluate(() => (window as any).__printCalls || 0);
    expect(printCalls).toBeGreaterThan(0);
  });

  test('homepage "Print all" includes every currently loaded card', async ({ page }) => {
    await page.goto('/index.html');
    await page.waitForSelector('.category-section');

    const printAllButton = page.locator('#print-all-btn');
    await expect(printAllButton).toBeEnabled();

    const allCardCount = await page.locator('.card-preview').count();
    expect(allCardCount).toBeGreaterThan(0);

    const [popup] = await Promise.all([
      page.waitForEvent('popup'),
      printAllButton.click()
    ]);
    await popup.waitForLoadState('load');

    await expect(popup.locator('.print-card-group')).toHaveCount(allCardCount);
    await expect(popup.locator('main .print-card-front h1').first()).toBeVisible();
  });

  test('persona page print button triggers print and has print-only layout for print media', async ({ page }) => {
    await page.goto('/persona.html?id=11');
    await page.waitForSelector('.card-detail');

    await page.click('#header-print-btn');
    const printCalls = await page.evaluate(() => (window as any).__printCalls || 0);
    expect(printCalls).toBeGreaterThan(0);

    await page.emulateMedia({ media: 'print' });
    const printOnlyDisplay = await page.locator('.print-only').evaluate((el) => getComputedStyle(el).display);
    const detailDisplay = await page.locator('.card-detail').evaluate((el) => getComputedStyle(el).display);

    expect(printOnlyDisplay).not.toBe('none');
    expect(detailDisplay).toBe('none');
  });
});
