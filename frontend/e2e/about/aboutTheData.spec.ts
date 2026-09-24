import { expect, test } from "@playwright/test";

test("About > About the data", async ({ page }) => {
  await page.goto("/aboutdata", { waitUntil: "networkidle" });
  // Expect the About the Data heading to be visible
  await expect(page.getByRole("heading", { name: "About the Data" })).toBeVisible();

  // Find Data Release Notes in side navigation and click it
  await expect(page.getByLabel("Data Release Notes navigation")).toBeVisible();
  // expect Data Release Notes to be at bottom of page and not in view
  await expect(
    page.getByRole("heading", { name: "Data Release Notes" }).getByRole("strong")
  ).not.toBeInViewport();

  await page.getByLabel("Data Release Notes navigation").click();

  // expect screen to have scrolled down
  await expect(
    page.getByRole("heading", { name: "Data Release Notes" }).getByRole("strong")
  ).toBeInViewport();

  // check that the first header matches regex for pattern ex: v3.2.3 (23 Jan 2025) or v.3.2 (1 Oct 2024)
  expect(page.locator("h3").first()).toHaveText(
    /^v\.?\d+\.\d+(\.\d+)? \(\d{1,2} [A-Za-z]+ \d{4}\)$/
  );

  // TODO check if first header text matches the version number in top right screen
  //const latestVersion = (await page.locator("div.app-version").innerHTML()).trim();
  //expect(page.locator("h3").first()).toContainText(latestVersion);
});
