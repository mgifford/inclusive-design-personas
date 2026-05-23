import { test, expect } from '@playwright/test';

test.describe('Print workflows', () => {
  test.beforeEach(async ({ page }) => {
    await page.context().addInitScript(() => {
      (window as any).__printCapture = {
        openCalls: 0,
        html: ''
      };
      const nativeOpen = window.open;
      window.open = function openStub(...args) {
        const capture = (window as any).__printCapture;
        capture.openCalls += 1;
        const opened = nativeOpen.apply(window, args as any);
        if (opened && opened.document && typeof opened.document.write === 'function') {
          const originalWrite = opened.document.write.bind(opened.document);
          opened.document.write = function captureWrite(html: string) {
            capture.html = html;
            return originalWrite(html);
          };
        }
        return opened;
      };

      window.print = function printStub() {
        (window as any).__printCalls = ((window as any).__printCalls || 0) + 1;
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

    await printSelectedButton.click();

    const printCapture = await page.evaluate(() => (window as any).__printCapture);
    const printGroupCount = (printCapture.html.match(/class="print-card-wrapper"/g) || []).length;
    expect(printCapture.openCalls).toBe(1);
    expect(printGroupCount).toBe(visibleCardCount);
    expect(printCapture.html).toContain('css/style.css');
    expect(printCapture.html).toContain('window.print()');
  });

  test('homepage "Print all" includes every currently loaded card', async ({ page }) => {
    await page.goto('/index.html');
    await page.waitForSelector('.category-section');

    const printAllButton = page.locator('#print-all-btn');
    await expect(printAllButton).toBeEnabled();

    const allCardCount = await page.locator('.card-preview').count();
    expect(allCardCount).toBeGreaterThan(0);

    await printAllButton.click();

    const printCapture = await page.evaluate(() => (window as any).__printCapture);
    const printGroupCount = (printCapture.html.match(/class="print-card-wrapper"/g) || []).length;

    expect(printCapture.openCalls).toBe(1);
    expect(printGroupCount).toBe(allCardCount);
    expect(printCapture.html).toContain('print-card-front');
    expect(printCapture.html).toContain('Print all persona cards');
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
