# OUTCOME_TOOLKIT Release Checklist

These are the steps to follow to successfully release a new version of the OUTCOME_TOOLKIT application and data.

> NOTE: These steps are for a 'routine' release. Emergency releases (critical bugfixes) should at least tag the release,
> produce updated release notes, increment the version number, and follow the deployment steps.

## Table of Contents

1. [Prepare candidate](#prepare-candidate)
   1. [Wiki page for release](#wiki-page-for-release)
   2. [Bash party](#bash-party)
   3. [Tag candidate](#tag-candidate)
2. [Create Merge Request](#create-merge-request)
   1. [Create Branch](#create-branch)
   2. [Increment version number](#increment-version-number)
   3. [Update release notes](#update-release-notes)
   4. [Update user guide](#update-user-guide)
   5. [Ensure tests still pass](#ensure-tests-still-pass)
   6. [Review merge request with next Release Warden](#review-merge-request-with-next-release-warden)
3. [Deployment](#deployment)
   1. [Schedule the deployment](#schedule-the-deployment)
   2. [Inform the program office (If needed)](#inform-the-program-office-if-needed)
   3. [Deploy](#deploy)
   4. [Report success](#report-success)
   5. [Actually merge](#actually-merge)

## Prepare candidate

### Wiki page for release

A wiki page exists for versions associated with major and minor releases. Update the page with progress as release steps are completed. Other project roles may contribute to other sections of the page, for example the Modification Request Warden.

### Bash party

1. In git, tag the current `main` branch with a tag like `release-x.y.z-bash-party`.
   - Tagging can be done from the gitlab ui by selecting the `Code` option in the left-hand menu, selecting `Tags`, and then selecting `New Tag`.
   - Write the tag name as above, create it from `main`, and leave the `Message` empty.
2. Plan a bash party soon after the version is ready, ideally at least a week before the production release date.
3. Ticket any new issues discovered and triage them into either "Complete before release", or "Can wait until after this version".
   - Urgent fixes that can't be applied in time may be included in a follow-up patch version.
4. Assign the prioritized fixes to developers and coordinate completing and merging them quickly.

### Tag candidate

1. Ensure all work for the release is in the branch `main`.
2. All tests must pass.
   - Tests that do not pass must be disabled—create a ticket for each test disabled in this fashion.
   - When enabled, pipeline must complete successfully.
3. In git, tag the release for commit with a tag like `release-x.y.z-candidate`.

**No new code changes** may be to the release candidate made after this point; the candidate is so the team can prepare all the non-code details.

If additional work is started after the candidate is tagged, it should be branched off the candidate commit, and then merged up with `main` once the release is accepted.

## Create Merge Request

### Create branch

- Create a ticket for the release.
- Create a branch and merge request from `main` where you will update release-specific files.
- Perform the following work in that branch.

### Increment version number

Update the version number.

- Version number is stored in `version.txt`.
- We use [Semantic Versioning](https://semver.org/) as a guideline for how to select the next version number.
- Determine if this release needs a Modification request
  - Refer to your organization's InfoSec/ESR guidance on Modifications. If unclear, email your InfoSec team and discuss with the team.
  - The main things that warrant a modification request when changed are:
    - Cloud architecture
    - Software stack (new libraries and services)
    - User roles/permissions
    - Site functionality
  - The main things that warrant a modification request when changed are:

### Update release notes

Write and commit new [Release Notes](../RELEASE-NOTES.md) for this version.

- Release notes are at the top level, in `RELEASE-NOTES.md`.
- One bullet per new feature, significant bug fix, or major change to the data bundle.
  - Written to illustrate user benefit, not from a code perspective.
    - E.g., "Improve accessibility by adding labels to map buttons."
  - If addressing feedback from the program office, include a reference to the row of the spreadsheet.
- For major versions, sub-bullets to explain its details.
- Merge requests should include suggested bullets for the release notes that can be combined here.
- It may be helpful to look at all chances since the last release. Git can provide this via `git log`, e.g. `git log release-3.0.1...release-3.0.2-candidate`.

### Update user guide

Update and commit the in-application User Guide:

- Take screenshots from the candidate version of the code using the automated user guide test
  - Build the application locally
    - `./start.sh -d yes`
  - Load the application in a browser and navigate to a page that requires maps to load to ensure that geographic information is cached.
  - From the frontend directory in a separate terminal:
    - `npm install`
    - `npx playwright install --with-deps chromium firefox webkit`
    - `npm run test:userguide`
  - Verify that the user guide screenshots are generated and that the tests pass
    - Note: Some of the tests may fail around the versioning number
      - Delete the `frontend/e2e/userguide/userguide.spec.ts-snapshots` directory and run the `npm run test:userguide` twice to fix the error
    - The screenshots should be found under `frontend/public` and will be labeled as `userguide#.png`, where the `#` corresponds with the screenshot number order, there should be 6 in total
      - ie. `userguide1.png`
- Ensure the steps still represent the full workflow.
  - If not, make a ticket to add new steps to the User Guide
- Copy generated screenshots into the corresponding slide in the user guide powerpoint
  - Note: `userguide4.png` corresponds to both slides 4 and 5 of the powerpoint slide
    - Therefore `userguide5.png` corresponds to slide 6 and `userguide6.png` corresponds to slide 7 respectively
  - Generate User Guide Images with tooltips:
    - Align the new screenshot image with the existing old screenshot image
    - Send the new screenshot image to the back
      - Right click image and hit `Send to Back`
    - Delete existing old screenshot image
    - Align the new screenshot image with the corresponding tooltips
- Screenshot each slide of the update userguide with tooltips and rename as `outcome_toolkit_ug#.png`, where the `#` corresponds with the powerpoint slide number of the screenshot, there should be 7 in total
  - ie. `outcome_toolkit_ug1.png`
- Copy newly generated user guide screenshots with tooltips into the `frontend/public` folder to replace the existing outdated user guide images

### Run the navigation tests

Run the navigation tests to verify that the forward and backward navigation between pages is working. The navigation tests are run separately from the other e2e tests, this is intentional as the navigation tests can run very long and should not be included in the CI pipeline tests.

- Build the application locally
  - `./start.sh -d yes`
- Load the application in a browser and navigate to a page that requires maps to load to ensure that geographic information is cached.
- From the frontend directory in a separate terminal:
  - `npm install`
  - `npx playwright install --with-deps chromium firefox webkit`
  - `npm run test:nav`
Note: You can skip the build and install steps above if they have been completed in the user guide generation steps and the application is currently running.

The navigation tests utilizes the playwright test fixtures parameterization capability with a `count` parameter to set the number of times to navigate forward and backward. The `count` parameter has a default value set to 5. The value can be changed within the file `frontend/e2e/navigation/navigation.spec.ts`. Increasing the `count` value to greater than 5 will cause the navigation tests to receive a timeout failure unless the maximum timeout value is increased significantly within the playwright configuration file `frontend/playwright.config.ts`, i.e. >180 seconds.

### Ensure tests still pass

Build the branch locally and run the following command to run the test suite:

`docker exec backend_container python3 -m pytest tests/ -vv`

If there is a test pipeline ensure that runs as well.

### Review merge request with next Release Warden

1. Nominate another developer to be the Release Warden for the next release.
2. Assign that developer as a reviewer for the current release's merge request.
3. Have them ensure that the changes look good and that tests run for them as well.
4. Tag the final commit to this branch as `release-x.y.z`.

## Deployment

### Schedule the deployment

Post intention to release in the Teams channel.

We traditionally deploy on Wednesdays.

### Inform the program office (If needed)

If the release is MAJOR (Refer to Semantic Versioning above) or if the fix is something the program office is especially interested in then we notify them of the release. The person who is designated to communicate with the program office sends an email to their team:

- anticipated date of deployment
- newest release notes (including new version)

### Deploy

Follow the instructions in docs/AWS_Deployment_Notes.md to deploy the system.

### Report success

Drop a note in the Teams channel to let everyone know that the release is live.

### Actually merge

Click `merge` on your approved merge request (Triple check that you are not squashing commits)

You're done!
