import { expect, test } from "@playwright/test";
import { key2outcome } from "../../src/util/metricUtils";
import { OUTCOME_KEYS } from "../../src/types";

test("About > Health Outcomes", async ({ page }) => {
  await page.goto("/healthoutcomes", { waitUntil: "networkidle" });

  // Expect the Health Outcomes heading to be visible
  await expect(page.getByRole("heading", { name: "Health Outcomes" })).toBeVisible();

  for (const key of OUTCOME_KEYS) {
    const { label } = key2outcome(key);

    // Click to that tab
    await page.getByRole("tab", { name: label }).click();
    await expect(page.getByRole("heading", { name: "Overview" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "The Problem" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Performance Monitoring" })).toBeVisible();
  }
});
