import { expect, test } from "@playwright/test";
import { OUTCOME_KEYS } from "../../src/types";
import { key2outcome } from "../../src/util/metricUtils";

// Clear local storage before running test.
test.use({ storageState: { cookies: [], origins: [] } });

test("Test the search page", async ({ page }) => {
  test.setTimeout(80_000);

  await page.goto("/search", { waitUntil: "networkidle" });

  // Expect the Select headings to be visible
  await expect(
    page.getByRole("heading", { name: "Select a health outcome to explore" })
  ).toBeVisible();
  await expect(page.getByRole("heading", { name: "Select a region to explore" })).toBeVisible();

  // Go through every outcome and check if things look okay
  // We are using for...of because we want this to happen serially; a forEach would not work.
  for (const key of OUTCOME_KEYS) {
    const { label, selectDescription } = key2outcome(key);
    const btn = page.locator(".select-outcome").getByRole("button", { name: label });

    // Select outcome and make sure selection and text changes
    await btn.click();
    await expect(btn).toHaveClass(/selected/);
    await expect(
      page.locator(".select-outcome").getByText(selectDescription.substring(0, 20))
    ).toBeVisible();

    // Expect the Leaflet map to be visible
    const mapPane = page.locator(".leaflet-container");
    await expect(mapPane).toBeVisible();

    // Close legend
    const legendCollapseBtn = page.locator(".legend-collapser");
    await legendCollapseBtn.click();

    // Expect some county or zcta3-level data to be in the map
    await expect(
      mapPane.locator("path.leaflet-interactive").count(),
      "Didn't find any leaflet paths (i.e. counties/zcta3s) on the map"
    ).not.toEqual(0);

    // Click the Learn More link to go to the Health Outcomes Maternal health details page
    await page.getByRole("button", { name: /Learn More/ }).click();
    expect(page.url()).toContain(key);

    await page.goBack();
  }
});
