import { test } from "./fixtures/workflowFixture";

// Clear local storage before running test.
test.use({ storageState: { cookies: [], origins: [] } });

// Set the outcome for the test workflow
// For now only the Opioid Overdose is supported
test.use({ outcome: "Opioid Overdose" });

test("Test the main use case workflow of the Outcome Toolkit application", async ({ workflow }) => {
  test.setTimeout(80_000);
  // Run the workflow test fixture
  workflow("Opioid Overdose");
});
