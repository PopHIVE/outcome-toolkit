import { expect, test } from "@playwright/test";

test.use({ storageState: { cookies: [], origins: [] } });

test("Map > Selection via the map", async ({ page }) => {
  // Make page huge to minimize chance of our candidate (below) being obscured by a control.
  page.setViewportSize({ width: 2500, height: 1600 });
  await page.goto("/results", { waitUntil: "networkidle" });

  // Hide whatever we can to make map as big as possible
  await page.getByRole("button", { name: /Collapse Outcome Area/ }).click();
  await page.locator(".legend-collapser").click();

  const selectionDropdown = page.locator(".selection-dropdown");
  await expect(selectionDropdown).toContainText(/0 selected/);

  // TODO: Make map-selection test less fragile.
  // Click right in the center. This should be on a valid area, but there's no guarantee.
  const mapDiv = page.locator(".area-map");
  const bb = await mapDiv.boundingBox();

  await mapDiv.click({ position: { x: bb.width / 2, y: bb.height / 2 } });
  await expect(selectionDropdown).toContainText(/1 selected/);

  await mapDiv.click({ position: { x: bb.width / 2, y: bb.height / 2 } });
  await expect(selectionDropdown).toContainText(/0 selected/);
});
