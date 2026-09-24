import type { PlaywrightTestConfig } from "@playwright/test";
import { devices } from "@playwright/test";

/**
 * Read environment variables from file.
 * https://github.com/motdotla/dotenv
 */
import "dotenv/config";

/**
 * See https://playwright.dev/docs/test-configuration.
 */
const config: PlaywrightTestConfig = {
  testDir: "./e2e",
  /* Maximum time one test can run for, in ms. */
  timeout: 300_000,
  fullyParallel: true,
  expect: {
    /*
     * Maximum time expect() should wait for the condition to be met.
     * For example in `await expect(locator).toHaveText();`
     */
    timeout: 60_000,
  },

  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 1,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: "html",
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Maximum time each action such as `click()` can take. Defaults to 0 (no limit). */
    actionTimeout: 60_000,

    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: "http://localhost",

    /* Only on CI systems run the tests headless */
    headless: true, //!!process.env.CI,

    /* Max time to navigate between pages */
    navigationTimeout: 60_000,

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: "on-first-retry",

    /* Our default screen size is set quite large. */
    viewport: { width: 1800, height: 1200 },
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: "setup",
      testMatch: /.*\.setup\.ts/,
    },
    {
      /* Quick-turnaround tests for local test and code development. Does NOT run setup first. */
      name: "quick",
      retries: 0,
      testIgnore: ["**userguide**", "**navigation**"],
      use: {
        ...devices["Desktop Chrome"],
      },
    },
    {
      name: "chromium",
      testIgnore: ["**userguide**", "**navigation**"],
      use: {
        ...devices["Desktop Chrome"],
      },
      dependencies: ["setup"],
    },
    {
      name: "firefox",
      testIgnore: ["**userguide**", "**navigation**"],
      use: {
        ...devices["Desktop Firefox"],
      },
      dependencies: ["setup"],
    },
    /* Safari. */
    {
      name: "webkit",
      testIgnore: ["**userguide**", "**navigation**"],
      use: {
        ...devices["Desktop Safari"],
      },
      dependencies: ["setup"],
    },
    {
      name: "userguide",
      testMatch: /userguide.spec.ts/,
      use: {
        ...devices["Desktop Chrome"],
      },
      dependencies: ["setup"],
    },
    {
      name: "navigation",
      testMatch: /.navigation.spec.ts/,
      retries: 0,
      use: {
        ...devices["Desktop Chrome"],
      },
      dependencies: ["setup"],
    },

    /* Test against mobile viewports. */
    // {
    //   name: 'Mobile Chrome',
    //   use: {
    //     ...devices['Pixel 5'],
    //   },
    // },
    // {
    //   name: 'Mobile Safari',
    //   use: {
    //     ...devices['iPhone 12'],
    //   },
    // },

    /* Test against branded browsers. */
    // {
    //   name: 'Microsoft Edge',
    //   use: {
    //     channel: 'msedge',
    //   },
    // },
    // {
    //   name: 'Google Chrome',
    //   use: {
    //     channel: 'chrome',
    //   },
    // },
  ],

  /* Folder for test artifacts such as screenshots, videos, traces, etc. */
  // outputDir: 'test-results/',

  /* Run your local dev server before starting the tests */
  // webServer: {
  //   /**
  //    * Use the dev server by default for faster feedback loop.
  //    * Use the preview server on CI for more realistic testing.
  //   Playwright will re-use the local server if there is already a dev-server running.
  //    */
  //   command: process.env.CI ? "vite preview --port 5001" : "vite dev",
  //   port: 5001,
  //   reuseExistingServer: !process.env.CI,
  // },
};

export default config;
