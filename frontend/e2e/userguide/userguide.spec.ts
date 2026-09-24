import { expect, test } from "@playwright/test";

/**
 * Only run test using chromium browser
 */
test.skip(
  ({ browserName }) => browserName !== "chromium",
  "Generate screenshots in chromium only."
);

// FIXME: See OUTCOME_TOOLKIT-250

/**
 * Test to generate screenshots used to create the user guide graphics
 */
test("Test to generate screenshots for the user guide graphics", async ({ page }) => {
  const screenshotPath = (counter: number) => `public/userguide${counter}.png`;
  let counter = 1;

  // Increase timeout to accommodate longer screenshots and loading times
  test.setTimeout(60_000);

  page.setViewportSize({ width: 1920, height: 1200 });

  await page.goto("/", { waitUntil: "networkidle" });

  // Take a screenshot of the Home page
  await page.screenshot({ path: screenshotPath(counter++), fullPage: true });

  // Click on Get Started button to navigate to Search page
  await page.getByRole("button", { name: "Get Started" }).click();
  await page.waitForURL(/search$/);

  // Click the Opioid Overdose button
  await page.getByRole("button", { name: "Opioid Overdose" }).click();

  // Expect the Map legend to be visible
  await expect(page.locator(".map-legend")).toBeVisible();

  // Take a screenshot of the Search page
  await page.screenshot({ path: screenshotPath(counter++), fullPage: true });

  // Click on Proceed button to navigate to Results page
  await page.getByRole("link", { name: /Proceed/ }).click();
  await page.waitForURL(/results$/);

  // Make sure the Outcome Area is visible
  const collapseButton = page.getByRole("button", { name: /Collapse Outcome Area/ });
  if (!(await collapseButton.isVisible())) {
    await page.getByRole("button", { name: /Outcome:/ }).click();
  }

  // Take a screenshot of the initial Results page
  await page.screenshot({ path: screenshotPath(counter++), fullPage: true });

  // Collapse the Outcome Area for the rest of the steps
  await collapseButton.click();

  // Expect the AreaList to load in a reasonable amount of time.
  await expect(page.locator(".area-list")).not.toContainText("Loading");

  // Collapse the Map legend
  await expect(page.locator(".map-legend")).toBeVisible();
  await page.getByTitle("Collapse Map Legend").click();

  // Spill open Alabama group.
  await page.getByText(/Alabama \(/).click();

  // County chosen to show contiguity, population, and outcome values
  await page.getByRole("checkbox", { name: /Autauga County/ }).click();

  // Take a screenshot of the updated Results page
  await page.screenshot({ path: screenshotPath(counter++), fullPage: true });

  // Select all of Alabama to show better data
  await page
    .getByRole("button", { name: /Add All/ })
    .first()
    .click();

  // Expand the Trended Data visualization and Take a screenshot of the updated Results page
  await page.locator(".expand-model").click({ delay: 500 });
  await page.screenshot({ path: screenshotPath(counter++), fullPage: true });
  await page.locator(".expand-model").click();

  // Collapse the Map legend
  await page.getByTitle("Collapse Map Legend").click();

  // Take a screenshot of the updated Results page
  await page.screenshot({ path: screenshotPath(counter++), fullPage: true });
});
