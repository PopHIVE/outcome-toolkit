import { mergeTests } from "@playwright/test";
import { test as navigationTest } from "../fixtures/navigationFixture";
import { test as workflowTest } from "../fixtures/workflowFixture";

export const test = mergeTests(navigationTest, workflowTest);

// Clear local storage before running test.
test.use({ storageState: { cookies: [], origins: [] } });

// Set the outcome for the tests
test.use({ outcome: "Opioid Overdose" });

// Set the count for the navigation test
navigationTest.use({ count: 10 });

test("Test the navigation to/from the Search page of the Outcome Toolkit application", async ({
  navigationSearchOutcome,
  workflow,
}) => {
  // Run the navigationSearchOutcome test fixture
  navigationSearchOutcome("Opioid Overdose", 5);

  // Run the workflow test fixture
  workflow("Opioid Overdose");
});

test("Test the navigation to/from the Results page of the Outcome Toolkit application", async ({
  navigationSearchResults,
  workflow,
}) => {
  // Run the navigationSearchResults test fixture
  navigationSearchResults("Opioid Overdose", 5);

  // Run the workflow test fixture
  workflow("Opioid Overdose");
});
