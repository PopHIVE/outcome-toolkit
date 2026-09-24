import { expect, test } from "@playwright/test";

test.use({ storageState: { cookies: [], origins: [] } });

test("Map > Hover over selection on the map", async ({ page }) => {
  // Make page huge to minimize chance of our candidate (below) being obscured by a control.
  page.setViewportSize({ width: 2500, height: 1600 });
  await page.goto("/results", { waitUntil: "networkidle" });

  // Hide whatever we can to make map as big as possible
  await page.getByRole("button", { name: /Collapse Outcome Area/ }).click();
  await page.locator(".legend-collapser").click();

  // Expect the Leaflet map to be visible
  const mapPane = page.locator(".leaflet-container");
  await expect(mapPane).toBeVisible();

  // Hover over a selection on the map
  // Expect some county or zcta3-level data to be in the map
  await expect(
    mapPane.locator("path.leaflet-interactive").count(),
    "Didn't find any leaflet paths (i.e. counties/zcta3s) on the map"
  ).not.toEqual(0);

  // hover over map pane to see area map

  // Selector for the tooltip element
  const tooltipSelector = ".pop-value";
  const singleArea = mapPane.locator("path.leaflet-interactive").nth(600);

  // Hover over the element to trigger the tooltip
  await singleArea.hover();

  // Wait for the tooltip to appear
  await page.waitForSelector(tooltipSelector, { state: "visible" });

  // Get tooltip text to compare later
  const firstTooltipText = await page.textContent(tooltipSelector);

  // Move the mouse away to hide the tooltip
  await page.mouse.move(1, 1);

  // Verify the tooltip is no longer visible
  await page.waitForSelector(tooltipSelector, { state: "hidden" });

  // Do again and compare the two tooltip texts - they should be different
  // Get new area
  const newArea = mapPane.locator("path:nth-child(300)");

  // Hover over the element to trigger the tooltip
  await newArea.hover();

  // Wait for the tooltip to appear
  await page.waitForSelector(tooltipSelector, { state: "visible" });

  // Get second tooltip text to compare to first
  const secondTooltipText = await page.textContent(tooltipSelector);
  // Compare two tooltip values
  expect(firstTooltipText).not.toEqual(secondTooltipText);
});
