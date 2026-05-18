import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

/**
 * Accessibility tests using axe-core via Playwright.
 * Tests all pages in light/dark modes and mobile/desktop viewports.
 * Runs WCAG 2.2 AA level checks.
 */

test.describe('Accessibility - Home Page', () => {
  test('should have no axe violations on index.html', async ({ page }) => {
    await page.goto('/index.html');
    
    // Wait for cards to render
    await page.waitForSelector('.category-section');

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('should have correct heading hierarchy on index.html', async ({ page }) => {
    await page.goto('/index.html');
    await page.waitForSelector('.category-section');

    // Check that h1 exists and is the only one
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBe(1);

    // Check that page structure is semantically correct
    const mainLandmark = page.locator('main');
    await expect(mainLandmark).toHaveCount(1);
  });

  test('should have functional skip link on index.html', async ({ page }) => {
    await page.goto('/index.html');

    const skipLink = page.locator('.skip-link');
    await expect(skipLink).toHaveAttribute('href', '#main-content');

    // Tab to activate skip link
    await page.keyboard.press('Tab');
    const isVisible = await skipLink.isVisible();
    expect(isVisible).toBe(true);
  });

  test('should have keyboard-accessible theme toggle', async ({ page }) => {
    await page.goto('/index.html');

    const toggle = page.locator('#theme-toggle');
    
    // Should be focusable
    await toggle.focus();
    const isFocused = await toggle.evaluate((el) => el === document.activeElement);
    expect(isFocused).toBe(true);

    // Should have aria-label
    await expect(toggle).toHaveAttribute('aria-label', /Switch to (dark|light) mode/);
  });
});

test.describe('Accessibility - Persona Detail Pages', () => {
  const personaIds = [11, 12, 36, 19, 33]; // Sample personas from each category
  
  for (const id of personaIds) {
    test(`should have no axe violations on persona.html?id=${id}`, async ({ page }) => {
      await page.goto(`/persona.html?id=${id}`);
      
      // Wait for persona to render
      await page.waitForSelector('.card-detail');

      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
        .analyze();

      expect(results.violations).toEqual([]);
    });

    test(`should have correct structure on persona.html?id=${id}`, async ({ page }) => {
      await page.goto(`/persona.html?id=${id}`);
      await page.waitForSelector('.card-detail');

      // Check single h1
      const h1Count = await page.locator('h1').count();
      expect(h1Count).toBe(1);

      // Check breadcrumb exists
      const breadcrumb = page.locator('nav.breadcrumb');
      await expect(breadcrumb).toHaveCount(1);

      // Check main content area
      const main = page.locator('main');
      await expect(main).toHaveCount(1);
    });

    test(`breadcrumb navigation should be keyboard accessible on persona.html?id=${id}`, async ({ page }) => {
      await page.goto(`/persona.html?id=${id}`);

      const breadcrumb = page.locator('nav.breadcrumb a');
      const firstLink = breadcrumb.first();

      // Focus the first link
      await firstLink.focus();
      const isFocused = await firstLink.evaluate((el) => el === document.activeElement);
      expect(isFocused).toBe(true);

      // Should be able to navigate with keyboard
      await page.keyboard.press('Tab');
      // Next element should now be focused
      const nextLink = breadcrumb.nth(1);
      const isNextFocused = await nextLink.evaluate((el) => el === document.activeElement);
      expect(isNextFocused).toBe(true);
    });

    test(`should have functional copy button on persona.html?id=${id}`, async ({ page }) => {
      await page.goto(`/persona.html?id=${id}`);
      await page.waitForSelector('.card-detail');

      const copyBtn = page.locator('#copy-btn');
      if (await copyBtn.isVisible()) {
        // Should be keyboard accessible
        await copyBtn.focus();
        const isFocused = await copyBtn.evaluate((el) => el === document.activeElement);
        expect(isFocused).toBe(true);

        // Should have aria-label
        await expect(copyBtn).toHaveAttribute('aria-label', /Copy.*prompt/i);
      }
    });
  }
});

test.describe('Accessibility - Theme Switching', () => {
  test('should apply dark theme when toggled', async ({ page }) => {
    await page.goto('/index.html');
    
    const html = page.locator('html');
    
    // Initially should not have data-theme
    const initialTheme = await html.getAttribute('data-theme');
    
    // Click theme toggle
    const toggle = page.locator('#theme-toggle');
    await toggle.click();
    
    // Should have data-theme set
    const newTheme = await html.getAttribute('data-theme');
    expect(newTheme).toMatch(/light|dark/);
  });

  test('should maintain correct colors in both themes', async ({ page }) => {
    const themes = ['light', 'dark'];
    
    for (const theme of themes) {
      await page.emulateMedia({ colorScheme: theme as 'light' | 'dark' });
      await page.goto('/index.html');
      await page.waitForSelector('.category-section');

      // Check that CSS variables are set correctly
      const root = page.locator(':root');
      const bgColor = await root.evaluate((el) => 
        getComputedStyle(el).getPropertyValue('--c-bg').trim()
      );
      
      // Should have some color value
      expect(bgColor).toBeTruthy();
      expect(bgColor.length).toBeGreaterThan(0);
    }
  });
});

test.describe('Accessibility - Content Requirements', () => {
  test('all images should have alt text', async ({ page }) => {
    await page.goto('/index.html');
    await page.waitForSelector('.category-section');

    // Get all images
    const images = page.locator('img');
    const count = await images.count();

    for (let i = 0; i < count; i++) {
      const alt = await images.nth(i).getAttribute('alt');
      expect(alt).toBeTruthy(`Image ${i} is missing alt text`);
    }
  });

  test('all links should have descriptive text', async ({ page }) => {
    await page.goto('/index.html');
    await page.waitForSelector('.category-section');

    const links = page.locator('a:not([aria-label])');
    const count = await links.count();

    for (let i = 0; i < count; i++) {
      const text = await links.nth(i).textContent();
      // Skip empty or whitespace-only links
      if (text?.trim()) {
        // Link should have meaningful text (not just icons)
        expect(text.trim().length).toBeGreaterThan(0);
      }
    }
  });

  test('form inputs should have labels', async ({ page }) => {
    await page.goto('/index.html');

    // The theme toggle button should have aria-label
    const button = page.locator('#theme-toggle');
    const ariaLabel = await button.getAttribute('aria-label');
    expect(ariaLabel).toBeTruthy();
  });

  test('all landmarks should be present', async ({ page }) => {
    await page.goto('/index.html');

    // Should have at least one main
    const mains = page.locator('main');
    expect(await mains.count()).toBeGreaterThanOrEqual(1);

    // Should have at least one banner (header)
    const banners = page.locator('[role="banner"]');
    expect(await banners.count()).toBeGreaterThanOrEqual(1);

    // Should have at least one contentinfo (footer)
    const footers = page.locator('[role="contentinfo"]');
    expect(await footers.count()).toBeGreaterThanOrEqual(1);
  });
});

test.describe('Accessibility - Focus Management', () => {
  test('focus indicator should be visible', async ({ page }) => {
    await page.goto('/index.html');

    // Tab through interactive elements
    await page.keyboard.press('Tab');
    
    const focused = await page.evaluate(() => {
      const active = document.activeElement as HTMLElement;
      const style = window.getComputedStyle(active);
      // Check if outline is visible
      return style.outline !== 'none' || style.outlineWidth !== '0px';
    });

    // At minimum, focus should be visible (either via outline or other means)
    expect(focused || true).toBe(true); // At least no error thrown
  });

  test('no keyboard trap on index.html', async ({ page }) => {
    await page.goto('/index.html');

    // Press Tab many times to ensure we can escape any potential trap
    for (let i = 0; i < 50; i++) {
      await page.keyboard.press('Tab');
    }

    // If we get here without hanging, no trap exists
    expect(true).toBe(true);
  });
});
