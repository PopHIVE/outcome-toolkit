import { expect, test } from "@playwright/test";

test("Home Page > Main body elements should be visible and enabled", async ({ page }) => {
  await page.goto("/");

  // Spot check that the nav bar is visible
  await expect(page.locator("a.logo")).toBeVisible();

  // Body contents too
  await expect(page.getByRole("heading", { name: "Welcome to the Outcome Toolkit" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Get Started" })).toBeEnabled();
});
