import { expect, test } from "@playwright/test";
import { OUTCOME_KEYS } from "../../src/types";
import { key2outcome } from "../../src/util/metricUtils";

test("Map > search map legend is visible and contains value bins for each outcome", async ({
  page,
}) => {
  await page.goto("/search", { waitUntil: "networkidle" });

  const legend = page.locator(".map-legend");

  await expect(legend).toContainText("No Data");
  await expect(legend).toContainText("Selected");

  for (const key of OUTCOME_KEYS) {
    const { label } = key2outcome(key);

    await page.getByRole("button", { name: label }).click();

    await expect(page.locator(".map-legend")).toBeVisible();

    await expect(
      legend.locator(".legend-bin-row"),
      `Didn't find 12 bins (10 data + empty + missing) in Legend for outcome ${label}.`
    ).toHaveCount(12);

    await page.getByTitle("Collapse Map Legend").click();
    await expect(legend.getByText("No Data")).not.toBeVisible();
    await page.getByTitle("Expand Map Legend").click();
    await expect(legend.getByText("No Data")).toBeVisible();
  }
});
