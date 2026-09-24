import { type UserID } from "../../src/types";

const TEST_AUTH_PATH = "playwright/.auth/userProfiles/";

/**
 * *Login Setup*
 *
 * NOTE: This is setup, and does NOT run with each run of the tests.
 * It should be manually re-run via `npm run test:setup-fixtures` when
 * the list of users, or the mechanism for logging in, changes. This will
 * regenerate the files on disk containing login state.
 *
 * It is, however, a playwright test, and therefore uses the same
 * syntax. We import 'test' as 'setup' to emphasize the difference.
 *
 * TO USE:
 * ```typescript
 *    test("admin test", async ({ page }) => {
 *      test.use({ storageState: storageStateForUserID(TEST_USER_ID_ADMIN) });
 *      ... Page now behaves as if TEST_USERS[TEST_USER_ID_ADMIN] was logged in.
 *    });
 * ```
 * See <https://playwright.dev/docs/auth> for inspiration
 */
export function storageStateForUserID(id: UserID) {
  return TEST_AUTH_PATH + id;
}
