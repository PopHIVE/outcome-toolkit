import { expect, test } from "@playwright/test";
import { OUTCOME_DATA } from "../../src/stores/OUTCOME_DATA";
import { OUTCOME_KEYS } from "../../src/types";

test("About > Payment Rates", async ({ page }) => {
  await page.goto("/paymentrates", { waitUntil: "networkidle" });

  // Expect the Payment Rates heading to be visible
  await expect(page.getByRole("heading", { name: "Payment Rates" })).toBeVisible();

  for (const key of OUTCOME_KEYS) {
    const { label } = OUTCOME_DATA[key];

    // Click to that tab
    await page.getByRole("tab", { name: label }).click();
    await expect(page.getByRole("heading", { name: "Rate Card" })).toBeVisible();
    await expect(page.getByRole("rowheader", { name: "Target Performance" })).toBeVisible();
  }
});
