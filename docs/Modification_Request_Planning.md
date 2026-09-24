# Modification Request Planning

---

## The Mod-Request Warden

We are creating a new role called the Mod-Request Warden&trade;. They will work alongside the Release Warden&trade; to get major and minor versions of the application approved for release.

Responsibilities include:
1. [Tracking new features](#tracking-new-features)
2. [Tracking release deadlines](#tracking-release-deadlines)
3. [Coordinating prioritization of issues](#coordinating-prioritization-of-issues)
4. [Creating modification requests](#creating-modification-requests)
5. [Managing the review process](#managing-the-review-process)

The above information shall be tracked in an issue. When a new [major or minor version](https://semver.org/) is planned by the team, create an issue to track its corresponding modification request. Call the issue something like "vX.Y.Z Modification Request and Review". It is possible that a minor version does not require a modification request but plan one just in case.

## Important concepts & acronyms

- **MRI** - Modification request issue, the GitLab issue being used to track all details and progress of a given modification request
- **MTV** - Minimum testable version, the version of a feature which is ready for review in a modification request. Some features require additional work to be ready for deployment to production, but that additional work is essentially content and won't impact security. At that point the feature's development can be split into two issues, with one (The MTV) describing the functional aspect and the second describing the polish. 

## Details of responsibilities

### Tracking new features
1. Be aware of sponsor requirements for requests and deadlines for new features.
2. Be aware of major feature work being done by the team not specified by the above.
3. Continuously update the above features in the **MRI** list.
   - As issues are created for features, add them.
   - If a feature's issue needs to be split to get a **MTV** faster, update the issue # accordingly.
   - When a feature's issue gets a merge request, add that to the list as well.

### Tracking release deadlines
1. Be aware of contractual requirements to deliver specific products or capabilities.
2. Be aware of informal promises and communication about expected timeline for features.
3. Be sure to confirm that your understanding of the above is correct (May require coordination with PL, TL or other team members).
4. Finalize the target date for release and add it to the **MRI**.

### Coordinating prioritization of issues
1. Determine the date by which the modification request should be submitted in order to comfortably meet deployment deadlines.
   - At minimum a month before the deployment deadline, more comfortably 6-8 weeks.
   - **IMPORTANT - Submit a request to the Secure Code Review team for a review in advance (Email . The planned date for the review will be a week or two after the modification request deadline.**
2. Encourage the team to perform triaging in order to identify features that will take longer to develop, and features that are blockers for others.
3. Work with the team to prioritize the development of features in order to submit the modification request on time.

### Creating modification requests
1. As features are added to a version's **MRI**, begin collecting information from the feature's developer(s) that describes the changes to the application they made.
2. Combine that information into a text document which describes the entire scope of technical changes and additions we want approval to include in a deployed version of the application.
   - Graphics may also be included.
   - Append the text "_please substitute Alice Isenberg for VP Stephen Ondra as DM & TD_" to the end of the paragraph.
3. Submit the text and graphics in a modification request to your organization's InfoSec intake process.

### Managing the review process
1. Coordinate with InfoSec as they review the modification request.
2. Ensure all **MTV** merge requests are complete and code for the release is in the `main` branch.
3. All tests must pass.
4. In git, tag `main` branch with a tag like `merge-request-x.y.z-candidate`.
5. Deploy the tagged commit to an internal cluster for penetration testing.
6. Deliver the tagged version of the codebase to the Secure Code Review team.
   - Also send the tag of the last merge request version so that they can diff the new code.
7. Inform the development team of any findings from the above testing and coordinate responses.
8. Once all reviews complete, tag the final commit of the code with a tag like `merge-request-x.y.z`.

---

## FAQ

#### Q. What to do when features planned to be in a modification request are moved to a different version?
If it's a version deploying sooner, discuss it with the person who prompted the change. If the features are likely to require review, make sure that enough time is planned for that version to get its own modification request.

---
#### Q. What features should be included in a modification request?
Basically anything that changes the scope of what an application can do, or how it does it. We err on the side of including unless we are sure it is a change that doesn't require review.

---
#### Q. What features require review?
- Any new functionality or features
  - This can include internal development tools on a case-by-case basis
- Changes to the codebase, architecture or tech stack of the application

---
#### Q. What features definitely DON'T require review?
- New API endpoints (Use discretion if the endpoint uses a new format)
- Changes to site content
- Bug fixes and patches

---
## What is a modification request?
### Background
When the Outcome Toolkit application was initially approved for public release, it went through a review process helmed by an InfoSec intake form. That form described most aspects of the Outcome Toolkit web application, including data sensitivity, user account handling, technical stack cloud architecture and more. Following submitting the form it was reviewed by InfoSec for completeness, and then put through a round of penetration testing and static analysis which both generated reports. 

We addressed concerns found in the two reports and then the entire suite of findings generated by the process were sent to our InfoSec A&E (architecture and engineering) risk assessor. They asked some questions and ultimately gave us their stamp of approval for public release, with some requirements and guidelines for hardening security. 

### Present
When the OUTCOME_TOOLKIT application is changed to the point where the information in the II form becomes out of date, they should be synchronized. This is done through the modification request process. In COMPASS you can add paragraphs describing new features, or changes to the application architecture and tech stack. Those changes will be reviewed by InfoSec, and one of two outcomes can occur:
1. The changes are acknowledged, but considered unnecessary to review
2. The changed are acknowledged, and determined to require further examination in case
