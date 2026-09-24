import {
  makeProjectMeasurement,
  type ProjectMeasurementsType,
  type ProjectType,
  type UserType,
} from "@/types";
import { DateTime } from "luxon";

export const EMPTY_USER: UserType = {
  id: "USER 00000",
  first_name: "Unknown",
  last_name: "User",
  role: "Health Accelerator",
  email: "email@example.com",
  organization: "Sample Organization",
};

// FIXME: Remove sample projects and users once we have real projects.
const oberon: UserType = {
  id: "USER 00001",
  first_name: "Oberon",
  last_name: "Orlando",
  role: "Outcome Buyer",
  email: "email@example.com",
  organization: "Sample Organization",
};
const nemo: UserType = {
  id: "USER 00002",
  first_name: "Nemo",
  last_name: "Norman",
  role: "Health Accelerator",
  email: "email@example.com",
  organization: "Sample Organization",
};
const priti: UserType = {
  id: "USER 00003",
  first_name: "Priti",
  last_name: "Patel",
  role: "Health Accelerator",
  email: "email@example.com",
  organization: "Sample Organization",
};
export const SAMPLE_USERS: UserType[] = [priti, oberon, nemo];

export const BASE_PROJECT_MEASURES: ProjectMeasurementsType = {
  "baseline": null,
  "total": null,
  "6": null,
  "12": null,
  "18": null,
  "24": null,
  "30": null,
  "36": null,
};

/** Sample project: Some of DC, outcome is SOC, two members. */
const SAMPLE_PROJECT_1_MIDS = [
  "ZCTA3 206",
  "ZCTA3 207",
  "ZCTA3 208",
  "ZCTA3 209",
  "ZCTA3 210",
  "ZCTA3 211",
  "ZCTA3 212",
  "ZCTA3 214",
  "ZCTA3 215",
  "ZCTA3 216",
  "ZCTA3 217",
  "ZCTA3 218",
  "ZCTA3 219",
];
const SAMPLE_PROJECT_2_MIDS = [
  "COUNTY 01001",
  "COUNTY 01003",
  "COUNTY 01005",
  "COUNTY 01007",
  "COUNTY 01009",
  "COUNTY 01011",
  "COUNTY 01013",
  "COUNTY 01015",
  "COUNTY 01017",
  "COUNTY 01019",
  "COUNTY 01021",
  "COUNTY 01023",
  "COUNTY 01025",
  "COUNTY 01027",
  "COUNTY 01029",
  "COUNTY 01031",
  "COUNTY 01033",
  "COUNTY 01035",
  "COUNTY 01037",
  "COUNTY 01039",
  "COUNTY 01041",
  "COUNTY 01043",
  "COUNTY 01045",
  "COUNTY 01047",
  "COUNTY 01049",
  "COUNTY 01051",
  "COUNTY 01053",
  "COUNTY 01055",
  "COUNTY 01057",
  "COUNTY 01059",
  "COUNTY 01061",
  "COUNTY 01063",
  "COUNTY 01065",
  "COUNTY 01067",
  "COUNTY 01069",
  "COUNTY 01071",
  "COUNTY 01073",
  "COUNTY 01075",
  "COUNTY 01077",
  "COUNTY 01079",
  "COUNTY 01081",
  "COUNTY 01083",
  "COUNTY 01085",
  "COUNTY 01087",
  "COUNTY 01089",
  "COUNTY 01091",
  "COUNTY 01093",
  "COUNTY 01095",
  "COUNTY 01097",
  "COUNTY 01099",
  "COUNTY 01101",
  "COUNTY 01103",
  "COUNTY 01105",
  "COUNTY 01107",
  "COUNTY 01109",
  "COUNTY 01111",
  "COUNTY 01113",
  "COUNTY 01115",
  "COUNTY 01117",
  "COUNTY 01119",
  "COUNTY 01121",
  "COUNTY 01123",
  "COUNTY 01125",
  "COUNTY 01127",
  "COUNTY 01129",
  "COUNTY 01131",
  "COUNTY 01133",
];

export const BLANK_PROJECT: ProjectType = {
  id: "PROJECT BLANK",
  projectName: "BLANK",
  performerType: "AHA",
  outcomeKey: "soc",
  users: [],
  performancePeriodFrom: DateTime.fromISO("2026-01-01T00:00:00.000"),
  performancePeriodTo: DateTime.fromISO("2029-01-01T00:00:00.000"),
  areas: [],
  projectMeasurements: BASE_PROJECT_MEASURES,
};
export const SAMPLE_PROJECT_1: ProjectType = {
  id: "PROJECT 1",
  projectName: "Example 1: Maternal Health Project in Maryland",
  performerType: "AHA",
  outcomeKey: "soc",
  users: [priti, oberon],
  performancePeriodFrom: DateTime.fromISO("2024-01-01T00:00:00.000"),
  performancePeriodTo: DateTime.fromISO("2027-01-01T00:00:00.000"),
  areas: SAMPLE_PROJECT_1_MIDS,
  projectMeasurements: BASE_PROJECT_MEASURES,
};
SAMPLE_PROJECT_1.projectMeasurements.baseline = makeProjectMeasurement(SAMPLE_PROJECT_1, {
  period: "baseline",
  payout: 0,
  nationalMetric: 180,
  projectMetric: 192,
});
SAMPLE_PROJECT_1.projectMeasurements["6"] = makeProjectMeasurement(SAMPLE_PROJECT_1, {
  period: "6",
  payout: 3_250_000,
  nationalMetric: 181,
  projectMetric: 174,
});

/** Sample project: All of Delaware, opioid. */
export const SAMPLE_PROJECT_2: ProjectType = {
  id: "PROJECT 2",
  projectName: "Example 2: Opioid Project in Alabama (PHA)",
  performerType: "PHA",
  outcomeKey: "opioid",
  users: [],
  performancePeriodFrom: DateTime.fromISO("2024-01-01T00:00:00.000"),
  performancePeriodTo: DateTime.fromISO("2027-01-01T00:00:00.000"),
  areas: SAMPLE_PROJECT_2_MIDS,
  projectMeasurements: BASE_PROJECT_MEASURES,
};
SAMPLE_PROJECT_2.projectMeasurements.baseline = makeProjectMeasurement(SAMPLE_PROJECT_1, {
  period: "baseline",
  payout: 0,
  nationalMetric: 7.2,
  projectMetric: 12.5,
});

export const SAMPLE_PROJECTS = [SAMPLE_PROJECT_1, SAMPLE_PROJECT_2];
