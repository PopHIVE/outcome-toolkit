import { test as base, expect } from "@playwright/test";

type NavigationFixture = {
  outcome: string;
  count: number;
  navigationSearchOutcome: (outcome: string, count: number) => void;
  navigationSearchResults: (outcome: string, count: number) => void;
};

export const test = base.extend<NavigationFixture>({
  outcome: "Opioid",
  count: 5,
  navigationSearchOutcome: [
    async ({ page, outcome, count }, use) => {
      // Navigate to the Search page
      await page.goto("/search", { waitUntil: "networkidle" });

      // Click the outcome button
      await page.getByRole("button", { name: outcome }).click();

      // Navigate to the Health Outcomes page and back to the Search page a few times
      for (let index = 0; index < count; index++) {
        // Resize the viewport on the third time through the loop
        if (index === 2) {
          await page.setViewportSize({ width: 1200, height: 900 });
        }

        // Click another outcome button
        if (index === 6) {
          await page.getByRole("button", { name: /Alcohol/ }).click();
        }

        // Click the Learn More link to go to the Health Outcomes details page
        await page.getByRole("button", { name: /Learn More/ }).click();

        // Expect the Health Outcomes heading to be visible
        await expect(page.getByRole("heading", { name: "Health Outcomes" })).toBeVisible();

        // Navigate back to the Search page
        await page.goBack();

        // Expect the Select headings to be visible
        await expect(
          page.getByRole("heading", { name: "Select a health outcome to explore" })
        ).toBeVisible();
        await expect(
          page.getByRole("heading", { name: "Select a region to explore" })
        ).toBeVisible();
      }
      // Provide the fixture value
      await use((outcome: string, count: number) => {
        outcome == "Opioid";
        count == 5;
      });
    },
    { scope: "test" }, // Fixture will be reused for each test
  ],

  navigationSearchResults: [
    async ({ page, outcome, count }, use) => {
      // Navigate to the Search page
      await page.goto("/search", { waitUntil: "networkidle" });

      // Click the Opioid Overdose button
      await page.getByRole("button", { name: outcome }).click();

      // Wait for the map to load on the Search page
      await expect(page.getByText("loading map ...")).not.toBeVisible();

      // Expect the Select headings to be visible
      await expect(
        page.getByRole("heading", { name: "Select a health outcome to explore" })
      ).toBeVisible();
      await expect(page.getByRole("heading", { name: "Select a region to explore" })).toBeVisible();

      // Navigate to the Results page
      await page.goto("/results", { timeout: 20_000, waitUntil: "networkidle" });

      // Wait for the map to load on the Results page
      await expect(page.getByText("loading map ...")).not.toBeVisible();

      // Expect the Selected Outcomes heading to be visible
      await expect(page.getByRole("heading", { name: /Select Outcome/ })).toBeVisible();

      // Navigate back to the Search page and forward to the Results page a few times
      for (let index = 0; index < count; index++) {
        // Resize the viewport on the second time through the loop
        if (index === 1) {
          await page.setViewportSize({ width: 1200, height: 900 });
        }

        // Navigate back to the Search page
        await page.goBack();

        // Wait for the map to load on the Search page
        await expect(page.getByText("loading map ...")).not.toBeVisible();

        // Click another outcome button
        if (index === 6) {
          await page.getByRole("button", { name: /Alcohol/ }).click();
        }

        // Expect the Select headings to be visible
        await expect(
          page.getByRole("heading", { name: "Select a health outcome to explore" })
        ).toBeVisible();
        await expect(
          page.getByRole("heading", { name: "Select a region to explore" })
        ).toBeVisible();

        // Navigate forward to the Results page
        await page.goForward();

        // Wait for the map to load on the Results page
        await expect(page.getByText("loading map ...")).not.toBeVisible();

        // Expect the Selected Outcomes heading to be visible
        await expect(page.getByRole("heading", { name: /Select Outcome/ })).toBeVisible();
      }
      // Provide the fixture value
      await use((outcome: string, count: number) => {
        outcome == "Opioid";
        count == 5;
      });
    },
    { scope: "test" }, // Fixture will be reused for each test
  ],
});

export { expect };
