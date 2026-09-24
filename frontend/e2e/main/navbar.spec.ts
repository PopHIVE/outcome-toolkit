import { test, expect } from "@playwright/test";

test("Navbar > All elements visible and enabled", async ({ page }) => {
  await page.goto("/");

  await expect(page.locator("a.logo")).toBeEnabled();
  await expect(page.getByRole("link", { name: "Home", exact: true })).toBeEnabled();
  await expect(page.getByRole("link", { name: "Search", exact: true })).toBeEnabled();
  await expect(page.getByRole("link", { name: "Results", exact: true })).toBeEnabled();

  page.getByRole("button", { name: "About" }).click();
  await expect(page.getByRole("link", { name: "About Outcome Toolkit" })).toBeEnabled();
  await expect(page.getByRole("link", { name: "User Guide" })).toBeEnabled();
  await expect(page.getByRole("link", { name: "FAQ" })).toBeEnabled();
  await expect(page.getByRole("link", { name: "About The Data" })).toBeEnabled();

  await expect(page.getByRole("link", { name: "Health Outcomes", exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "Payment Rates", exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "Results", exact: true })).toBeVisible();

  page.getByRole("button", { name: "Projects" }).click();
  //await expect(page.getByRole("link", { name: "Invite Team Members" })).toBeEnabled();
  await expect(page.getByRole("link", { name: "Log In" })).toBeEnabled();
});
