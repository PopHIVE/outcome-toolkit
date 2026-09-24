import { test, expect } from "@playwright/test";
import { LOCAL_STORAGE_PROJECT_INFO } from "../../src/util/Consts";
import { ProjectType } from "../../src/types";

// TODO: Write negative project access test
test.fixme("Cannot access projects you are not authorized for", () => {});

test.fixme("Cannot access any project when not logged in", () => {});

test.fixme("Can log in and log out", () => {});

/**
 * Slow test which loads the main page, ensures there is no project information
 * stored in local storage, then loads and exits a project page to check the same.
 */
test.fixme("Check project info leakage", async ({ page }) => {
  test.slow();
  await page.goto("/", { waitUntil: "networkidle" });

  expect(
    page.context().storageState({ path: LOCAL_STORAGE_PROJECT_INFO }),
    "No project information should be in local storage"
  ).toBeFalsy();

  // TODO:
  // Login
  // See project appear
  // Logout
  // Ensure project info is not in local storage or visible on screen
  // Go to project page and get error.
});
