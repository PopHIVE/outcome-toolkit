import { expect, test } from "@playwright/test";

test("About > About", async ({ page }) => {
  await page.goto("/about", { waitUntil: "networkidle" });
  // Expect the About the Outcome Toolkit heading to be visible
  await expect(page.getByRole("heading", { name: "The Outcome Toolkit Program" })).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "The Outcome Toolkit", exact: true })
  ).toBeVisible();
});
