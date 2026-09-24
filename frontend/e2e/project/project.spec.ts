import { expect, test } from "@playwright/test";
//import _ from "lodash";
import { SAMPLE_PROJECT_1 } from "../../src/stores/SAMPLE_PROJECTS";
import { PROJECT_IGNORED_COLOR } from "../../src/util/colorUtils";

// FIXME: Enable test.use() of storage state when we have auth built
//test.use({ storageState: storageStateForUserID(SAMPLE_PROJECT_1.users[0].id) });

// FIXME: Enable login testing once auth is in place
test.fixme("Project > Project page login elements present and populated", async ({ page }) => {
  await page.goto("/protected/projects");
  const user = SAMPLE_PROJECT_1.users[0].id;

  await expect(page.getByLabel(/project name/i)).toContainText(SAMPLE_PROJECT_1.projectName);
  await expect(page.getByRole("button", { name: user.first_name })).toBeEnabled();
});

test.skip("Project > Project Info > Info is present and visible, filters and time bin work", async ({
  page,
}) => {
  await page.goto("/protected/projects", { waitUntil: "networkidle" });

  const project = SAMPLE_PROJECT_1;
  const users = project.users;
  // const users = _.keys(project.users).map((mid) => SAMPLE_USERS.find(({ id }) => id === mid));
  const projectAreaNumber = project.areas.length;

  await expect(page.getByTitle(/project name/i)).toContainText(project.projectName);
  await expect(page.getByTitle(/project geograph(y|ies)/i)).toHaveText(
    new RegExp(`${projectAreaNumber} project `)
  );
  await expect(page.getByTitle(/project members/i)).toHaveText(
    new RegExp(`${users.length} project members?.*`)
  );

  await page.getByTitle(/project members/i).click();
  for (const u of users) {
    const username = u.first_name + " " + u.last_name;
    await expect(page.locator(".project-member-dropdown")).toContainText(username);
  }
  // Close dropdown again so it doesn't cover the buttons below
  await page.getByTitle(/project members/i).click();

  // Project areas should be visible and should match project data in length at least
  const projectAreas = await page
    .locator(`.leaflet-interactive:not([fill="${PROJECT_IGNORED_COLOR}"])`)
    .all();
  const projectAreasLength = (await projectAreas).length;
  await expect(projectAreasLength).toEqual(projectAreaNumber);

  // Time bin selector should be clickable
  const timeBinSelector = page.locator(".time-bin-picker");
  await timeBinSelector.click();
  await page.locator(".time-bin-item").first().click();

  // Data Filters
  await page.getByRole("button", { name: /six month rolling/i }).click();
  await page.locator(".data-filter-item").last().click();
});

test.skip("Project > Payout Wizard > Reduction explanation component", async ({ page }) => {
  await page.goto("/protected/projects", { waitUntil: "networkidle" });

  const dashboard = page.locator(".payout-dashboard");
  const wizard = dashboard.locator(".payout-wizard");

  // Wizard area starts closed; check that collapsing works.
  await expect(wizard.getByText(/Baseline/)).not.toBeVisible();
  await wizard.getByRole("button", { name: /Calculation Steps/ }).click();
  await expect(wizard.getByText(/Baseline/)).toBeVisible();

  const pageButtons = wizard.locator("li.page-item");

  // Start on page one
  await expect(pageButtons.filter({ hasText: "1" })).toHaveClass(/active/);

  // Can move forward/back through cards
  await pageButtons.filter({ hasText: "Back" }).click();
  await expect(pageButtons.filter({ hasText: "1" })).toHaveClass(/active/);

  await expect(pageButtons.filter({ hasText: "2" })).not.toHaveClass(/active/);
  await pageButtons.filter({ hasText: "2" }).click();
  await expect(pageButtons.filter({ hasText: "1" })).not.toHaveClass(/active/);
  await expect(pageButtons.filter({ hasText: "2" })).toHaveClass(/active/);
  await pageButtons.filter({ hasText: "3" }).click();
  await expect(pageButtons.filter({ hasText: "1" })).not.toHaveClass(/active/);
  await expect(pageButtons.filter({ hasText: "2" })).not.toHaveClass(/active/);
  await pageButtons.filter({ hasText: "Back" }).click();
  await expect(pageButtons.filter({ hasText: "2" })).toHaveClass(/active/);
  await pageButtons.filter({ hasText: "Next" }).click();
  await expect(pageButtons.filter({ hasText: "3" })).toHaveClass(/active/);
  await pageButtons.filter({ hasText: "Next" }).click();
  await expect(pageButtons.filter({ hasText: "4" })).toHaveClass(/active/);
  await pageButtons.filter({ hasText: "Next" }).click();
  await expect(pageButtons.filter({ hasText: "5" })).toHaveClass(/active/);

  await pageButtons.filter({ hasText: "Next" }).click();
  await expect(pageButtons.filter({ hasText: "5" })).toHaveClass(/active/);

  // TODO: Tests to make sure numbers match the project, once we have project data
});
