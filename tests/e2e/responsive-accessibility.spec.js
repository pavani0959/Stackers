import {
  expect,
  test,
} from '@playwright/test';

test.describe.configure({ mode: 'serial' });


const viewports = [
  {
    name: 'mobile-360',
    width: 360,
    height: 800,
  },
  {
    name: 'mobile-390',
    width: 390,
    height: 844,
  },
  {
    name: 'tablet',
    width: 768,
    height: 1024,
  },
  {
    name: 'desktop',
    width: 1440,
    height: 900,
  },
];


for (const viewport of viewports) {
  test(
    (
      'has no horizontal overflow '
      + `at ${viewport.name}`
    ),
    async ({ page }) => {
      await page.setViewportSize({
        width: viewport.width,
        height: viewport.height,
      });

      await page.goto(
        '/',
        {
          waitUntil:
            'domcontentloaded',
        },
      );

      await page.waitForFunction(
        () =>
          document.querySelector('#root')
            ?.childElementCount > 0,
        null,
        {
          timeout: 15000,
        },
      );

      await expect(
        page.locator('#root > *').first(),
      ).toBeVisible();

      const dimensions =
        await page.evaluate(() => ({
          scrollWidth:
            document.documentElement
              .scrollWidth,

          clientWidth:
            document.documentElement
              .clientWidth,
        }));

      expect(
        dimensions.scrollWidth,
      ).toBeLessThanOrEqual(
        dimensions.clientWidth,
      );
    },
  );
}


test(
  'interactive controls are keyboard reachable',
  async ({ page }) => {
    await page.goto(
      '/',
      {
        waitUntil:
          'domcontentloaded',
      },
    );

    let focusedControl = null;

    for (
      let attempt = 0;
      attempt < 12;
      attempt += 1
    ) {
      await page.keyboard.press(
        'Tab',
      );

      focusedControl =
        await page.evaluate(() => {
          const active =
            document.activeElement;

          if (!active) {
            return null;
          }

          return {
            tagName:
              active.tagName,

            focusVisible:
              active.matches(
                ':focus-visible',
              ),
          };
        });

      if (
        focusedControl
        && [
          'BUTTON',
          'A',
          'INPUT',
          'SELECT',
          'TEXTAREA',
        ].includes(
          focusedControl.tagName,
        )
      ) {
        break;
      }
    }

    expect(
      focusedControl,
    ).not.toBeNull();

    expect([
      'BUTTON',
      'A',
      'INPUT',
      'SELECT',
      'TEXTAREA',
    ]).toContain(
      focusedControl.tagName,
    );

    expect(
      focusedControl.focusVisible,
    ).toBe(true);
  },
);


test(
  'reduced motion disables long animations',
  async ({ page }) => {
    await page.emulateMedia({
      reducedMotion: 'reduce',
    });

    await page.goto(
      '/',
      {
        waitUntil:
          'domcontentloaded',
      },
    );

    const motionDurations =
      await page.evaluate(() => {
        const element =
          document.createElement('div');

        element.style.animationName =
          'phase-eight-test';

        element.style.animationDuration =
          '10s';

        element.style.animationIterationCount =
          'infinite';

        element.style.transitionDuration =
          '10s';

        document.body.appendChild(
          element,
        );

        const styles =
          window.getComputedStyle(
            element,
          );

        const result = {
          animationDuration:
            styles.animationDuration,

          animationIterationCount:
            styles.animationIterationCount,

          transitionDuration:
            styles.transitionDuration,
        };

        element.remove();

        return result;
      });

    expect(
      motionDurations
        .animationIterationCount,
    ).toBe('1');

    expect([
      '0s',
      '0.00001s',
      '0.01ms',
      '1e-05s',
    ]).toContain(
      motionDurations
        .animationDuration,
    );

    expect([
      '0s',
      '0.00001s',
      '0.01ms',
      '1e-05s',
    ]).toContain(
      motionDurations
        .transitionDuration,
    );
  },
);
