import { expect, type Locator, test } from "@playwright/test";
import { DEMOGRAPHIC_DATA, DemographicKeys } from "../../src/stores/DEMOGRAPHIC_DATA";

/** Extract e.g. the number `67` from text like 'Alabama (3 of 67)'  */
async function extractNumberFromStateGroup(t: string | null): Promise<number> {
  if (!t) {
    return -1;
  }
  const matches = /of (\d+)\)/.exec(t);
  return matches === null ? -1 : Number(matches[1]);
}
/** Extract the number from text like 'Selected: 482.5k'  */
async function extractNumberFromGauge(gaugeLocator: Locator): Promise<number | null> {
  return gaugeLocator
    .locator(".actual-label")
    .getAttribute("title")
    .then((s) => (s ? Number(s.split(":")[1]) : null));
}

/** Extract the string from text like 'Selected: Above National Average'  */
async function extractStringFromGauge(t: string | null): Promise<string | null> {
  if (!t) {
    return null;
  }
  const matches = /Selected: (.+)/.exec(t);
  return matches === null ? null : matches[1];
}

// ************* TESTS ************* //

// Clear local storage before running test.
test.use({ storageState: { cookies: [], origins: [] } });

test.beforeEach(async ({ page }) => {
  page.setViewportSize({ width: 1600, height: 1600 });
  await page.goto("/results", { timeout: 30_000, waitUntil: "networkidle" });
  await expect(page.getByText("Loading data...")).not.toBeVisible();
});

test("Empty state looks right", async ({ page }) => {
  const csvExportButton = page.getByRole("button", { name: "Export as CSV" });
  const pdfExportButton = page.getByRole("button", { name: "Export as PDF" });
  await expect(csvExportButton).toBeDisabled();
  await expect(pdfExportButton).toBeDisabled();

  // Expect the Selected Outcomes area to be visible and have SOC selected (the default)
  await expect(page.getByRole("button", { name: /Maternal Health/ })).toHaveClass(/selected/);

  // Collapse outcome area
  await page.getByRole("button", { name: /Collapse Outcome Area/i }).click();

  // With no selections, all elements should be in the 'no selections' state
  const areaSelectionDropdown = page.locator(".selection-dropdown");
  await expect(areaSelectionDropdown).toContainText("0 selected");
  await expect(page.locator(".state-group").first()).toBeVisible();
  await expect(page.getByRole("heading", { name: "Evaluate Area Suitability" })).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Select one or more areas to view suitability" })
  ).toBeVisible();
  await expect(page.getByRole("heading", { name: "Contiguity" })).not.toBeVisible();
  await expect(page.getByRole("heading", { name: "Population" })).not.toBeVisible();

  await expect(page.getByRole("heading", { name: /Select \w+ for Intervention/ })).toBeVisible();
  await expect(page.locator(".leaflet-container")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Export Selected Data" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Export as PDF" })).toBeDisabled();

  // Map should be visible and have 'hover' message
  const mapDiv = page.locator(".area-map");
  await expect(mapDiv).toBeInViewport();
  await expect(mapDiv.getByRole("heading", { name: /Hover over/ })).toBeVisible();
});

test("expands/collapse outcome area", async ({ page }) => {
  const expandOutcomeButton = page.getByRole("button", { name: /Outcome/ });
  await page.getByRole("button", { name: /Collapse Outcome Area/ }).click();
  const selectedOutcomeText = page.getByRole("heading", { name: /Select Outcome/ });
  await expect(selectedOutcomeText).not.toBeVisible();

  await expandOutcomeButton.click();
  await expect(selectedOutcomeText).toBeVisible();
});

test("can select via the list of states", async ({ page }) => {
  const selectionDropdown = page.locator(".selection-dropdown");
  const firstStateGroup = page.locator(".state-group").first();

  const areasInFirstState = await firstStateGroup.textContent().then(extractNumberFromStateGroup);
  expect(areasInFirstState, {
    message: "String format for the number of areas in a state didn't match expected pattern",
  }).not.toEqual(-1);

  await selectionDropdown.click(); // Close dropdown again
  await expect(selectionDropdown).toContainText(/No selections/);
  await selectionDropdown.click(); // Close dropdown again

  // Click the Add all button to add all of Alabama's areas
  await firstStateGroup.getByRole("button", { name: /Add All/ }).click();

  // State group should now have every element selected
  await expect(firstStateGroup).toContainText(`${areasInFirstState} of ${areasInFirstState}`);
  await expect(selectionDropdown).toContainText(`${areasInFirstState} selected`);

  await selectionDropdown.click();
  await expect(selectionDropdown.locator("li div")).toHaveCount(areasInFirstState);

  // Test removal using selection dropdown's 'Remove All' button
  await selectionDropdown.getByRole("button", { name: "Remove All" }).click();
  await selectionDropdown.click();
  await expect(selectionDropdown.locator("li")).toHaveCount(1); // "No selections found"

  await firstStateGroup.click({ position: { x: 10, y: 10 } }); // Click on left hand side to dodge the Add All button

  // County/Zip3-level selection should also work
  const checks = firstStateGroup.getByRole("checkbox");
  await checks.nth(0).click();
  await expect(firstStateGroup).toContainText(`1 of ${areasInFirstState}`);
  await selectionDropdown.click(); // Open dropdown
  await expect(selectionDropdown.locator("li div")).toHaveCount(1);
  await selectionDropdown.click(); // Close it again
  await checks.nth(1).click();
  await expect(firstStateGroup).toContainText(`2 of ${areasInFirstState}`);
  await selectionDropdown.click(); // Open dropdown
  await expect(selectionDropdown.locator("li div")).toHaveCount(2);
  await selectionDropdown.click(); // Close it again
});

test("Area List shows counties for ZCTA3s and not for others", async ({ page }) => {
  const firstStateGroup = page.locator(".state-group").first();

  // Ensure we are on SOC outcome, which has ZCTA3-based data.
  await page.getByRole("button", { name: "Maternal Health" }).click();

  await firstStateGroup.click();

  const zcta301Row = page.locator(".area-row", { hasText: "ZCTA3 301xx" }).first();
  await expect(zcta301Row).toBeVisible();
  await zcta301Row.getByText(/Show all/).click();
  await expect(zcta301Row.getByRole("listitem")).toHaveCount(17);
  await zcta301Row.getByText(/Show all/).click();
  await expect(zcta301Row.getByRole("listitem")).toHaveCount(0);

  // Switch to Opioid, which is county-based
  await page.getByRole("button", { name: "Opioid Overdose" }).click();
  await page.waitForLoadState("networkidle");
  await firstStateGroup.click();
  await expect(
    firstStateGroup
      .locator(".area-row")
      .first()
      .getByText(/Show all/)
  ).toBeHidden();
});

test("Gauges update as user makes selections", async ({ page }) => {
  // Make space
  await page.getByRole("button", { name: /Collapse Outcome Area/ }).click();

  const firstStateGroup = page.locator(".state-group").first();

  // TODO: can we locate these some other way than by locator?
  const contiguityGauge = page.locator(".contiguity-gauge");
  const populationGauge = page.locator(".population-gauge");
  const metricGauge = page.locator(".outcome-gauge");

  const selectedMetricValue = metricGauge.textContent().then(extractStringFromGauge);

  await firstStateGroup.getByRole("button", { name: /Add All/ }).click();

  // Expect the gauge headers to be visible
  await expect(page.getByRole("heading", { name: "Contiguity" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Population" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Rate" })).toBeVisible();

  await expect(contiguityGauge).toContainText(/are contiguous/);

  // Save for later comparison
  const wholeStatePop = await extractNumberFromGauge(populationGauge);
  expect(wholeStatePop).toBeGreaterThan(0);

  await expect(selectedMetricValue).not.toContain("No Data"); // FIXME need more tests for metric value

  // Spill open first group
  await firstStateGroup.click({ position: { x: 10, y: 10 } }); // Click on left hand side to dodge the Add All button

  const checks = firstStateGroup.getByRole("checkbox");

  // Select a few and make sure numbers change each time
  await firstStateGroup.getByRole("button", { name: /Remove All/ }).click();
  let oldPop: number | null = null;
  for (const n of [0, 1, 2]) {
    await checks.nth(n).click();
    const newPop = await extractNumberFromGauge(populationGauge);
    expect(newPop).toBeGreaterThan(0);
    expect(newPop).not.toEqual(oldPop);
    oldPop = newPop;
  }
});

test("demographics table updates with selection changes", async ({ page }) => {
  // Make space
  await page.getByRole("button", { name: "Collapse Outcome Area" }).click();

  const firstStateGroup = page.locator(".state-group").first();
  const demographicsArea = page.locator(".demographic-distribution");

  await firstStateGroup.click(); // Spill open first state group
  const checks = firstStateGroup.getByRole("checkbox");

  await checks.first().click();

  // Test the table for each of the demographic types we're splitting the data on
  for (const key of DemographicKeys) {
    const { label } = DEMOGRAPHIC_DATA[key];
    await demographicsArea.locator("label").getByText(label).click(); // HACK: figure out component type of demographics headers. It's not radio...?

    await expect(
      demographicsArea.locator("thead"),
      `For demographic '${key}', did not find '${label}' in the header of the demographics table`
    ).toContainText(label);

    // Find 'selected' value for first row
    const firstSelectedAgeValue = await demographicsArea
      .locator("tbody td:nth-of-type(2)")
      .first()
      .textContent();
    expect(firstSelectedAgeValue, {
      message: "Demographics table value did not look like a number.",
    }).toMatch(/[0-9.]+[mk]?/);

    await checks.nth(1).click();
    const firstSelectedAgeValueAfter = await demographicsArea
      .locator("tbody td:nth-of-type(2)")
      .first()
      .textContent();
    expect(firstSelectedAgeValueAfter, {
      message: "Demographics table value did not update when selection was changed.",
    }).not.toEqual(firstSelectedAgeValue);
  }
});

test("Each whole state/territory should pass the population criterion", async ({
  browserName,
  page,
}) => {
  test.skip(
    browserName !== "chromium",
    "This test only checks data, and so only needs to be run on one browser."
  );

  // Make space
  await page.getByRole("button", { name: "Collapse Outcome Area" }).click();

  // TODO: can we locate these some other way than by locator and icon?
  const populationGauge = page.locator(".population-gauge");
  const stateGroups = page.locator(".state-group");

  for (const stateGroup of await stateGroups.all()) {
    await stateGroup.getByRole("button", { name: "Add All" }).click();
    await expect(
      populationGauge,
      `Did not pass population criterion: ${await stateGroup.innerText()}`
    ).toHaveClass(/valid/);
    // Unselect
    await stateGroup.getByRole("button", { name: "Remove All" }).click();
  }
});
