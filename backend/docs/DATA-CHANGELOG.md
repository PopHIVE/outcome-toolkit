# DATA Releases

# CHANGELOG

## Release v0.32.0

- Changes
  - `Added` 2025-07 Data Release for all vendors/outcomes


## Release v0.27.0

- Changes
  - `Added` 2025-06 Data Release for all vendors/outcomes


## Release v0.24.0

- Changes
  - `Added` 2025-05 Data Release for all vendors/outcomes

## Release v0.23.0

- Changes
  - `Added` 2025-04 Data Release for all vendors/outcomes

## Release v0.21.0

- Changes
  - `Added` 2025-02 Data Release for all vendors/outcomes

## Release v0.20.0

- Changes:
 - `Added` 2025-01 Data Release for all vendors/outcomes


## Release v0.18.0

- Changes:
 - `Added` 2024-12 Data Release for all vendors/outcomes

## Release v0.17.0

- Changes:
 - `Added` November and October Data Submissions for all outcomes
   - Increases NEMSIS datas of coverage to October 2024
     - Adds Monthly 2023 Data from backlog
   - Increases Veradigm dates of coverage to November 2024
   - Increases SOC dates of coverage to September 2024


## Release v0.16.0

- Changes:
  - `Added` New SOC Data From Health Verity (September 30th Delivery)

## Release v0.15.0

- Changes:
  - `Added` September NEMSIS Opioid and Alcohol Delivery.
    - Increased dates covered for Opioid and Alcohol to August 2024

## Release v0.14.0

- Changes:
  - `Added` Monthly 2024 Q2 Veradigm ASCVD Data.
    - Increased dates covered from Jan 2022 - Jul 2024

## Release v0.13.0

- Changes:
  - `Added` Monthly NEMSIS Data (2024 Q1 and Q2 Data)
    - Enables Trended line for Opioid and Alcohol Outcomes

## Release v0.12.0

 - Changes:
   - `Added` New Health Verity SOC Data (July 24th 2024 Release).
      - Increased dates covered from Jan 2021 - May 2024
      - Added variables: `mh_suicide_self_harm`, `mh_abuse`, `mh_sud`, `mh_spmi`, `any_soc_mortality`

## Release v0.10.0

- Changes:
 - `Updated` Added the `Veradigm_ASCVD_score_2022_2024Q1.xlsx` to the data bundle.

## Release v0.9.0

- Changes:
 - `Updated` Increased the Adjacency Distance to 5 miles (this means we can increase the threshold cutoff to up to 5 miles without requiring a new bundle).

## Release v0.8.0

- Changes:
 - `Added` 2023 NEMSIS Data (March 18th Delivery)
 - `Added` New SOC Data From Health Verity (March 20th Delivery)
 - `Added` NEMSIS Monthly Total Trendlines

## Release v0.7.0

- Changes:
 - `Added` 2022 NEMSIS Data (March 8th Delivery)
 - `Updated` Bin Statistics which include a -1 bin.

## Release v0.6.0

 - Changes:
   - `Added` New Health Verity SOC Data.
      - Until Future API discussion it is ETL'd in Raw Form but only the Zip3 Aggregated returned by the API.

## Release v0.5.0

 - Changes:
   - `Added` New ASCVD Data `Veradigm_ASCVD_score_2022_2023.xlsx` to the Bundle

## Release v0.4.0

 - Changes:
   - `Added` Adjacencies for all geographies to the data bundle (drastically speeds up `REBUILD_DB` option)

## Release v0.3.1

 - Changes:
   - `Added` New Fixed NEMSIS Opioid and Alcohol Rate Data (COUNTY)
   - `Added` New Fixed NEMSIS Opioid and Alcohol Rate Bins
   - `Deprecated` Old NEMSIS Measures (Avg Naloxone, Time To Patient, etc.)


## Release v0.3.0

 - Changes:
   - `Added` NEMSIS Opioid Data (COUNTY)
   - `Added` NEMSIS Alcohol Data (COUNTY)
     - `Deprecated` Mock Opioid Data

## Release v0.2.0

 - Changes:
   - `Added` ACS Income Estimates by household (ZCTA5, ZCTA3, COUNTY, STATE).
   - `Added` ACS Population Estimates by race/ethnicity, age and gender (ZCTA5, ZCTA3, COUNTY, STATE).
 
---------------------------

 - Changes:
   - `Added` Mock Opioid Data using the same formula as SOC (only difference is the rate used of 300/100,000).


## Release v0.1.1

---------------------------

 - Changes:
   - `Added` Mock Opioid Data using the same formula as SOC (only difference is the rate used of 300/100,000).

## Release v0.1.0

---------------------------

 - Includes:
   - 2020 Cartographic Boundaries (ZCTA5, ZCTA3, County, State)
   - 2020 Census Demographic Data (ZCTA5, ZCTA3, County, State)
   - Mock SOC Data (ZCTA3)
   - Sample ASCVD Data (ZCTA3)


