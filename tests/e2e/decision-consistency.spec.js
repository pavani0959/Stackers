import { expect, test } from '@playwright/test';
import { decisionFixture } from '../../src/testDecisionFixture.js';

const profileFixture = {
  user: {
    id: 1,
    name: 'Test User',
    email: 'test@example.com',
    gender: 'women',
    age: 21,
    avatar_url: null,
    onboarding_completed: true,
    created_at: '2026-07-01T00:00:00Z',
  },

  preferences: {
    budget_min: 800,
    budget_max: 3000,
    budget_tier: 'mid_range',
    preferred_occasions: ['campus'],
    preferred_colours: ['white'],
    preferred_brands: [],
    preferred_aesthetics: ['minimalist'],
    fit_preferences: ['relaxed'],
    comfort_priority: 0.5,
    trend_openness: 0.5,
    fashion_goal: 'shop smarter',
    comfort_expression_balance: 0.5,

    occasion_priorities: {
      campus: 1,
    },
  },

  style_profile: {
    profile_id:
      '22222222-2222-4222-8222-222222222222',

    version: 3,

    dna_vector: {
      minimalist: 70,
      streetwear: 30,
    },

    primary_identity: 'minimalist',
    secondary_identity: 'streetwear',
    profile_confidence: 86,

    identity: {
      name: 'Minimalist Explorer',
      description: 'Test identity',
      primary: 'minimalist',
      secondary: 'streetwear',
    },

    confidence_breakdown: {},
    evidence: {},
  },
};

test(
  'product and Decision Intelligence show one immutable score',
  async ({ page }) => {
    let profileRequested = false;
    let feedRequested = false;
    let snapshotRequested = false;

    page.on('console', (message) => {
      console.log(
        `[browser:${message.type()}]`,
        message.text(),
      );
    });

    page.on('pageerror', (error) => {
      console.error(
        '[browser page error]',
        error.message,
      );
    });

    page.on('requestfailed', (request) => {
      console.error(
        '[browser request failed]',
        request.method(),
        request.url(),
        request.failure()?.errorText,
      );
    });

    page.on('response', (response) => {
      if (response.status() >= 400) {
        console.error(
          '[browser response error]',
          response.status(),
          response.url(),
        );
      }
    });

    page.on('request', (request) => {
      const url = new URL(request.url());

      if (
        url.origin === 'http://127.0.0.1:8000'
        && url.pathname.startsWith('/api/')
      ) {
        console.log(
          '[browser API request]',
          request.method(),
          request.url(),
        );
      }
    });

    await page.addInitScript(() => {
      localStorage.clear();
      sessionStorage.clear();
    });

    const corsHeaders = {
      'Access-Control-Allow-Origin':
        'http://127.0.0.1:5173',

      'Access-Control-Allow-Methods':
        'GET, POST, PUT, PATCH, DELETE, OPTIONS',

      'Access-Control-Allow-Headers':
        'Content-Type, Accept',
    };

    /*
     * Use a broad API matcher so the test works whether the frontend
     * calls localhost, 127.0.0.1, or another configured API host.
     */
    await page.route(
      'http://127.0.0.1:8000/api/**',
      async (route) => {
        const request = route.request();
        const url = new URL(request.url());

        const method = request.method();

        const pathname =
          url.pathname.replace(/\/+$/, '')
          || '/';

        console.log(
          `[mock-api] ${method} ${pathname}`,
        );

        /*
         * Cross-origin POST requests may send an OPTIONS request first.
         */
        if (method === 'OPTIONS') {
          await route.fulfill({
            status: 204,
            headers: corsHeaders,
            body: '',
          });

          return;
        }

        /*
         * The current profile must load before Home requests the
         * persisted recommendation feed.
         */
        if (
          (
            pathname === '/api/profile'
            || pathname === '/api/profile/current'
          )
          && method === 'GET'
        ) {
          profileRequested = true;

          await route.fulfill({
            status: 200,

            headers: {
              ...corsHeaders,
              'Content-Type':
                'application/json',
            },

            body: JSON.stringify(
              profileFixture,
            ),
          });

          return;
        }

        /*
         * Retained for any screen that still requests the product list.
         */
        if (
          pathname === '/api/products'
          && method === 'GET'
        ) {
          await route.fulfill({
            status: 200,

            headers: {
              ...corsHeaders,
              'Content-Type':
                'application/json',
            },

            body: JSON.stringify([
              decisionFixture.product,
            ]),
          });

          return;
        }

        /*
         * Home must request server-owned persisted decisions and must
         * not submit a frontend-owned user profile.
         */
        if (
          pathname === '/api/decisions/feed'
          && method === 'POST'
        ) {
          feedRequested = true;

          const requestBody =
            request.postDataJSON();

          expect(
            requestBody,
          ).not.toHaveProperty(
            'user_profile',
          );

          expect(
            requestBody,
          ).not.toHaveProperty(
            'dna',
          );

          expect(
            requestBody,
          ).not.toHaveProperty(
            'score_breakdown',
          );

          await route.fulfill({
            status: 201,

            headers: {
              ...corsHeaders,
              'Content-Type':
                'application/json',
            },

            body: JSON.stringify({
              session_id:
                decisionFixture.session_id,

              model_version:
                decisionFixture.model_version,

              profile_version:
                decisionFixture.profile_version,

              items: [
                decisionFixture,
              ],
            }),
          });

          return;
        }

        /*
         * Product Detail and Decision Intelligence must both retrieve
         * the same immutable stored snapshot.
         */
        if (
          pathname
          === `/api/decisions/${decisionFixture.snapshot_id}`
          && method === 'GET'
        ) {
          snapshotRequested = true;

          await route.fulfill({
            status: 200,

            headers: {
              ...corsHeaders,
              'Content-Type':
                'application/json',
            },

            body: JSON.stringify(
              decisionFixture,
            ),
          });

          return;
        }

        /*
         * Product Detail may record a view event after loading.
         */
        if (
          (
            pathname === '/api/events'
            || pathname === '/api/user-events'
          )
          && method === 'POST'
        ) {
          await route.fulfill({
            status: 201,

            headers: {
              ...corsHeaders,
              'Content-Type':
                'application/json',
            },

            body: JSON.stringify({
              id: 1,
              user_id: 1,
              event_type: 'product_view',

              product_id:
                decisionFixture.product.id,

              wardrobe_item_id: null,

              recommendation_item_id:
                decisionFixture
                  .recommendation_item_id,

              event_metadata: {},

              occurred_at:
                '2026-07-16T12:00:00Z',

              created_at:
                '2026-07-16T12:00:00Z',
            }),
          });

          return;
        }

        console.error(
          `[unhandled-api] ${method} ${pathname}`,
        );

        await route.fulfill({
          status: 404,

          headers: {
            ...corsHeaders,
            'Content-Type':
              'application/json',
          },

          body: JSON.stringify({
            detail: [
              'Unhandled Playwright API request',
              method,
              pathname,
            ].join(': '),
          }),
        });
      },
    );

    await page.goto('/home');

    await expect.poll(
      () => profileRequested,
      {
        message:
          'The application should request the server profile',

        timeout: 10000,
      },
    ).toBe(true);

    await expect.poll(
      () => feedRequested,
      {
        message:
          'Home should request the persisted decision feed',

        timeout: 10000,
      },
    ).toBe(true);

    const productName = page
      .getByText(
        decisionFixture.product.name,
        {
          exact: true,
        },
      )
      .first();

    await expect(
      productName,
    ).toBeVisible({
      timeout: 10000,
    });

    await productName.click();

    await expect(page).toHaveURL(
      new RegExp(
        `/product/${decisionFixture.product.id}`
        + `\\?decision=${decisionFixture.snapshot_id}`,
      ),
    );

    const productScore = page.locator(
      '.det-score',
    );

    await expect(
      productScore,
    ).toHaveText(
      String(
        decisionFixture.overall_score,
      ),
      {
        timeout: 10000,
      },
    );

    const displayedProductScore =
      (
        await productScore.textContent()
      )?.trim();

    await page.getByRole(
      'button',
      {
        name: /why is this recommended/i,
      },
    ).click();

    await expect(page).toHaveURL(
      new RegExp(
        `/decision/${decisionFixture.snapshot_id}`,
      ),
    );

    await expect.poll(
      () => snapshotRequested,
      {
        message:
          'Decision Intelligence should load the stored snapshot',

        timeout: 10000,
      },
    ).toBe(true);

    const decisionScore = page.locator(
      '.di-hero-score',
    );

    await expect(
      decisionScore,
    ).toContainText(
      String(
        decisionFixture.overall_score,
      ),
      {
        timeout: 10000,
      },
    );

    const displayedDecisionScore =
      (
        await decisionScore.textContent()
      )?.trim();

    expect(
      displayedDecisionScore,
    ).toContain(
      displayedProductScore,
    );

    await page.reload();

    await expect(
      decisionScore,
    ).toContainText(
      String(
        decisionFixture.overall_score,
      ),
      {
        timeout: 10000,
      },
    );
  },
);