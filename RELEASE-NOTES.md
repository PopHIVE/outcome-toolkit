# RELEASE NOTES

## v4.0.1 (6 Aug 2025)
- Updated the SOC and ASCVD data definition files for the Download... buttons in the About the Data page

## v4.0.0 (5 Aug 2025)

- Added user authentication system with SSO account integration
    - Note: Auth integration is only properly working in the DEMO test environment and broken in PROD, fix coming soon in next release
- Introduced project pages for authenticated users to view their specific Outcome Toolkit projects
- Added interactive payout wizard to calculate and display project funding details
    - Shows national baseline and project geography information
    - Displays available program funds and payout calculations
    - Updated terminology from "calls" and "activations" to "encounters"
- Improved graph readability and layout across all charts
- Enhanced map and graph tooltips with better font sizes and legibility
- Updated maternal health data language to reflect new data sources
- Updated data as of the June 2025-06 submission (additional data point in trendline)
- Changed SOC rates to display per 10,000 population instead of per 100,000 population
- Fixed cardio target rate display to show 0.5% instead of 50%
- Improved team member invitation system with better form validation
- Enhanced project rate calculations for more accurate reporting
- Introduced data release versioning into the application for different data deployments 
- Project chooser (debug) now shows different text during reload and when there's an error.
- Footer on Search Results page is now always visible, instead of being clipped by the map on some screens.
- Should "never" show the wrong tooltip info when switching projects

## 4.0.0-b3 (10 June 2025)

- Improved payout wizard with consistent number formatting and clearer wording
- Updated data as of the April 2025-04 submission (additional data point in trendline)
- Enhanced user interface with updated terminology from "person" to "women"
- Invite team member page integration with email notifications to the outcome-toolkit-accounts inbox
- Nginx updates for isolated system deployments and shared configurations

## 4.0.0-b2 (12 May 2025)

- Updated Data Release Notes
- Added responsive design improvements for tables on smaller screens

## v4.0.0-b1 (2 May 2025)

- Introduced authentication system allowing users to sign in with SSO accounts on protected routes
- An invite team member form was created to create new SSO accounts
- Added static maintenance page for when F5 infrastructure is down 
- Added project pages for authenticated users to view their specific Outcome Toolkit projects
    - Choose between monthly data or trailing six-month average data
    - Enhanced outcome selection interface
    - Project details display below page header
- Added payout wizard to calculate project funding and view payout dashboard
- Improved PDF export with aggregate summary row and better formatting
- Enhanced map functionality to display difference-in-differences data for all value ranges
- Updated data as of the December 2024-12 submission (additional data point in trendline)
- Extended data coverage:
    - NEMSIS data through March 2025
    - Veradigm data through March 2025
    - SOC data through March 2025


## v3.2.3 (28 Jan 2025)

- Added link to PDF to return back to Outcome Toolkit site
- Updated all PDF Calculations to use the 6-Month Trailing Average values instead of the raw data
    - PDF Now includes the numerical rate for each county/ZIP3 in addition to the comparison text
- Selecting an area with missing data shows as selected on the map
- Improvements to AreaList — can see full list of counties in a ZCTA3 from within the area list, and will see the full list in the PDF export
- Improved map performance to correctly populate data
- Improvements to data formatting for NEMSIS opioid data
- Legend bins display continuous bins (max A = min B)
- Updated to 6 mo. averages and added income stats to CSV
- Data changes:
    - Added December Data Submissions for all outcomes:
        - Increases NEMSIS datas of coverage to November 2024
        - Increases Veradigm dates of coverage to December 2024
        - Increases SOC dates of coverage to October 2024

## v3.2.2 (23 Dec 2024)

- Improvements to layouts on tall or narrow screens
- Added option in Legend for the user to select raw (the default) or trailing six-month data streams (default is turned off).
- Legend says "XXX and up" for top bin
- Updated the SOC Coverage by State file Revision 11/26/2024
- Fixed Legend data to display accurate information
- ETL Pipeline Migration to Dagster for ASCVD Loaders
- Make swagger api docs endpoint hidden from prod deployment 
- Improve map performance and state border unpredictability
- Data changes:
- Added November and October Data Submissions for all outcomes:
    - Increases NEMSIS datas of coverage to October 2024
        - Adds Monthly 2023 Data from backlog
    - Increases Veradigm dates of coverage to November 2024
    - Increases SOC dates of coverage to September 2024

## v3.2.1 (22 Nov 2024)

- Improving map visibility by making the map legend collapsible
- Map, gauges, and legend show Jan 2024 data
- Revised labels on PDF for accurate data representation
- Revised outcome gauge text to improve readability
- Improved '?' icon visibility when hovered over
- Hiding graph lines when data is not available
- Using rank.rep for the value everywhere we can, including in nat'l average and in the gauges.
- Bug fixes and performance improvements

## v3.1.1 (16 Oct 2024)

- Results page Section 3 changes
- PDF content reordered (Section 1, Section 3, Section 2, Legend)
- Added the SOC Coverage by State file download button to the About the Data page
- Area selections are now saved across sessions
- Historical graph and Map use clearer colors to improve visual accessibility
- Historical graph now shows available (but limited) data for outcomes with limited historical data
- Trended Component will now show ASCVD data from January 2022 up through July 2024.
- Updated the css to ensure the map legend is collapsable/expandable at all times
- Updated backend to support the frontend showing the national average in the trendline component.
- Fixed the e2e tests to correct failures
- Fixed the userguide test to generate improved screenshots
- Fixed the legend overlapping with the hover for details

## v3.1 (18 Sep 2024)

- Added site monitoring capabilities to detect disruptions to site availability
- Improved feedback during slow page loads
- Improved data tooltip
- Trailing 6 month average shown when available
- Metric averages are now computed using rates when available, rather than representative rates
- NEMSIS Data has been updated to now cover monthly 2024 Q1, Q2 data.
- The trended chart for Opioid and Alcohol now populates with 2024 Monthly data Q1 and Q2.
- Added a Payment Rates page
- Fixed content typos

## v3.0.1 (29 Aug 2024)

- Added functionality for PDF report downloads

## v3.0.0 (31 Jul 2024)

- View historical data when available (Heart Attack and Stroke Risk; Maternal Health)
- Visualize Health over time for selected area when available (Heart Attack and Stroke Risk; Maternal Health)
- Performance improvements to data and map loading times
- Optimized performance when switching outcomes
- Improved screen size responsiveness for smaller screens
- Updated Maternal Health metric definitions files
- Updated user guide
- Fixed issue with health outcome link
- Bugs squashed

## v2.2.0 (18 Jun 2024)

- Fixed a bug causing zoom of the map to behave unpredictably.
- Improved look and feel of search results view on narrow screens
- Updated the health outcome icons for Maternal Health and Alcohol outcomes on the Search page and the Health Outcomes page
- User will now be seeing updated ASCVD/Veradigm data (2022-2024Q1)
- Improved image and request load time when revisiting
- Added time period of data to the map legend.
- Users using a screen reader, keyboard-only or mouse-only input will notice improved access and navigation of the pages.
- Improved the color contrast for the version number and the 'Hover over an area for details' map tooltip
- Updated SOC csv download outcome metric header

## v2.1.0 (7 May 2024)

- Guide updated with latest screenshots
- Tooltip can now be reached for selection
- Improve layout on narrow screens
- Improved accessibility by providing buttons to pan the map
- Improved accessibility in loading state
- Exchanged hash versioning for numeric versioning

## v2.0.1 (25 Apr 2024)

- Fix missing ASCVD explanatory file
- Fix broken links to other file

## v2.0.0 (19 Apr 2024)

First public release.

- Explanatory content for four outcomes
- Per county and per zip3 data for four outcomes
- Select counties or zip3s to build a cohort for a Outcome Toolkit project
- Contiguity, population, and outcome checks
- CSV export

## v1.0.0 (Jan 2024)

- First deployed version.
- Did not include all data.
