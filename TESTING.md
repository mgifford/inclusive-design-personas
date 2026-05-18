# Accessibility Testing

This project includes automated accessibility testing using Playwright + axe-core and Lighthouse CI.

## Quick Start

### Install dependencies
```bash
npm install
```

### Run accessibility tests locally
```bash
npm run test:a11y
```

This runs comprehensive axe-core checks on:
- Home page (`index.html`)
- Sample persona detail pages (`persona.html?id=*`)
- All pages tested in light/dark modes and desktop/mobile viewports

Tests verify:
- WCAG 2.2 AA compliance
- Heading hierarchy
- Keyboard navigation and focus management
- Color contrast (theme-aware)
- Alt text on images
- Semantic structure and landmarks
- No keyboard traps
- Functional skip links and theme toggle

### View test report
After running tests, open the HTML report:
```bash
open playwright-report/index.html
```

### Run Lighthouse audit
```bash
npm run serve  # In one terminal
npm run test:lighthouse  # In another
```

Reports are saved to `.lighthouseci/`.

## CI/CD Pipeline

Automated accessibility checks run on:
- Every pull request
- Every push to `main`
- Daily schedule (0:00 UTC)
- Manual trigger via GitHub Actions

### Workflow: `.github/workflows/accessibility.yml`

Three jobs run in parallel:

1. **Axe Tests** — Playwright + axe-core on multiple viewports and themes
   - Tests all pages with screen reader context
   - Artifacts: `playwright-report/`

2. **Lighthouse Audit** — PageSpeed Insights accessibility, performance, best practices
   - Targets 95% accessibility, 90% performance
   - Artifacts: `.lighthouseci/`

3. **WCAG Compliance** — Basic page load and structure verification
   - Confirms pages render without errors

Results are posted as comments on pull requests.

## Test Coverage

### Pages Tested
- `index.html` — Home page with dynamically rendered cards
- `persona.html?id=11..36` — All persona detail pages (sample of 5)

### Themes
- Light mode (`prefers-color-scheme: light`)
- Dark mode (`prefers-color-scheme: dark`)

### Viewports
- Desktop (1280×1024)
- Mobile (375×667)

### Standards
- WCAG 2.2 Level AA
- WCAG 2.1 Level AA
- WCAG 2.0 Level A

## Accessibility Skills

This project uses the [mgifford/accessibility-skills](https://github.com/mgifford/accessibility-skills) collection.

When reviewing accessibility issues or implementing fixes, load the relevant skill:
- General: `.github/skills/ACCESSIBILITY-general/SKILL.md`
- CI/CD: `.github/skills/ci-cd/SKILL.md`
- (and others as needed)

See `AGENTS.md` for the full list.

## Adding New Pages

When adding new pages to test:

1. Update `.lighthouserc.json` to include the URL
2. Add test cases to `tests/a11y.spec.ts`
3. Run `npm run test:a11y` locally to verify
4. Commit and push — CI will run automatically

## Manual Testing

While automated tests are comprehensive, always complement with:
- Keyboard-only navigation
- Screen reader testing (NVDA, JAWS, VoiceOver)
- Zoom at 200%
- Windows High Contrast Mode
- Manual inspection in both light/dark themes

See `.github/skills/manual-testing/SKILL.md` for detailed checklist.
