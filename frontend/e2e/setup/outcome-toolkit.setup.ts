import { expect, test as setup } from "@playwright/test";

setup("Wait for first (cold) load of the Outcome Toolkit", async ({ page }) => {
  // Go to the main page.
  await page.goto("/", { waitUntil: "networkidle", timeout: 120_000 });

  // Go to the Search page to verify that data is available
  await page.goto("/search", { waitUntil: "networkidle" });

  // Expect the map legend to be visible when the data is available
  await expect(page.locator(".map-legend")).toBeVisible();
});
