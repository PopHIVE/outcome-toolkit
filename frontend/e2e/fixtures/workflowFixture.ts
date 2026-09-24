import { test as base, expect } from "@playwright/test";

type WorkflowFixture = {
  outcome: string;
  workflow: (outcome: string) => void;
};

export const test = base.extend<WorkflowFixture>({
  outcome: "Opioid",
  workflow: [
    async ({ page, outcome }, use) => {
      // Go to the main page.
      await page.goto("/", { waitUntil: "networkidle" });

      // Click the Get Started button to navigate to the Search page.
      await page.getByRole("button", { name: "Get Started" }).click();
      await page.waitForURL(/search$/);
      await page.getByRole("button", { name: outcome }).click();
      // TODO: expect map to show county-level information instead
      await page.getByRole("link", { name: /Proceed/ }).click();
      await page.waitForURL(/results$/);

      const exportAsCSV = page.getByRole("button", { name: /Export as CSV/ });
      const exportAsPDF = page.getByRole("button", { name: /Export as PDF/ });

      await expect(exportAsCSV).toBeDisabled();
      await expect(exportAsPDF).toBeDisabled();
      await page.getByRole("button", { name: /Collapse Outcome Area/ }).click();

      // Expect the AreaList to load in a reasonable amount of time.
      await expect(page.locator(".area-list")).not.toContainText("Loading");

      // Spill open Alabama group.
      await page.getByText("Alabama").click();

      // Counties chosen to match the needed workflow below to test contiguity, population, and outcome values
      const county_low_metric_and_pop = page.getByRole("checkbox", { name: /Jackson County/ });

      // Contiguous counties in a line, Autauga -> Chilton -> Shelby -> Jefferson.
      // In combination, they also meet population and metric criteria.
      // Jefferson by itself satisfies the metric criterion.
      const county1 = page.getByRole("checkbox", { name: /Jefferson County/ });
      const county2 = page.getByRole("checkbox", { name: /Shelby County/ });
      const county3 = page.getByRole("checkbox", { name: /Chilton County/ });
      const county4 = page.getByRole("checkbox", { name: /Autauga County/ });

      // TODO: can we locate these some other way than by locator?
      const contiguityGauge = page.locator(".contiguity-gauge");
      const populationGauge = page.locator(".population-gauge");
      const outcomeGauge = page.locator(".outcome-gauge");

      // Expect initial state to be 'empty'
      await expect(county1).not.toBeChecked();
      await expect(page.getByText(/Hover over an area for details/)).toBeVisible();

      // Select a county with insufficiently bad metric and population
      await county_low_metric_and_pop.click();
      await expect(contiguityGauge).toHaveClass(/valid/);
      await expect(populationGauge).not.toHaveClass(/valid/);
      await expect(outcomeGauge).not.toHaveClass(/valid/);
      await county_low_metric_and_pop.click(); // unselect it

      // Select first county and make sure gauges appear and update
      await county1.click();
      await expect(county1).toBeChecked();
      await expect(contiguityGauge).toHaveClass(/valid/);
      await expect(populationGauge).toHaveClass(/valid/);
      await expect(outcomeGauge).toHaveClass(/valid/);

      // Select non-contiguous county
      await county3.click();
      await expect(contiguityGauge).not.toHaveClass(/valid/);
      // Unselect it again so we can build a contiguous selection piece by piece
      await county3.click();
      await expect(contiguityGauge).toHaveClass(/valid/);

      // Add all the counties
      await county2.click();
      await expect(contiguityGauge).toHaveClass(/valid/);
      await county3.click();
      await expect(contiguityGauge).toHaveClass(/valid/);
      await county4.click();
      await expect(contiguityGauge).toHaveClass(/valid/);
      // Areas should now be acceptable on all fronts
      await expect(contiguityGauge).toHaveClass(/valid/);
      await expect(populationGauge).toHaveClass(/valid/);
      await expect(outcomeGauge).toHaveClass(/valid/);

      // Test the CSV export
      // Start waiting for file chooser before clicking. Note: no await.
      const downloadPromise = page.waitForEvent("download");
      await exportAsCSV.click();
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toMatch(/outcome-toolkit-\d\d\d\d-\d\d-\d\d.csv/);

      // Test the PDF export
      // Start waiting for file chooser before clicking. Note: no await.
      const downloadPromise2 = page.waitForEvent("download");
      await exportAsPDF.click();
      const download2 = await downloadPromise2;
      expect(download2.suggestedFilename()).toMatch(/outcome-toolkit-\d\d\d\d-\d\d-\d\d.pdf/);
      // Provide the fixture value
      await use((outcome: string) => {
        outcome == "Opioid";
      });
    },
    { scope: "test" }, // Fixture will be reused for each test
  ],
});

export { expect };
