import type { APIV2DataDetails, MID } from "@/types";

export const LOADING_STRING = "Loading...";

export const EMPTY_DATA_DETAILS: APIV2DataDetails = {
  alcohol: {
    earliest_date: "",
    latest_date: "",
    data_release: "",
  },
  cardio: {
    earliest_date: "",
    latest_date: "",
    data_release: "",
  },
  opioid: {
    earliest_date: "",
    latest_date: "",
    data_release: "",
  },
  soc: {
    earliest_date: "",
    latest_date: "",
    data_release: "",
  },
};

// Keys for use in local storage. Also used in tests.
export const LOCAL_STORAGE_MAP_CENTER = "outcome-toolkit-map-center";
export const LOCAL_STORAGE_MAP_ZOOM = "outcome-toolkit-map-zoom";
export const LOCAL_STORAGE_METRIC_HISTORY_GRAPH_SIZE = "outcome-toolkit-metric-history-graph-size";
export const LOCAL_STORAGE_MID_SELECTIONS = "outcome-toolkit-mid-selections";
export const LOCAL_STORAGE_OUTCOME_SHOWN = "outcome-toolkit-outcome-shown";
export const LOCAL_STORAGE_SELECTED_OUTCOME = "outcome-toolkit-selected-outcome";
export const LOCAL_STORAGE_SELECTED_ROLE = "outcome-toolkit-selected-role";
export const LOCAL_STORAGE_SELECTED_DATA_STREAM = "outcome-toolkit-selected-data-stream";
export const LOCAL_STORAGE_PROJECT_INFO = "outcome-toolkit-project-info";
export const LOCAL_STORAGE_PROJECT_FILTER = "outcome-toolkit-project-filter";
export const LOCAL_STORAGE_STEPS_SHOWN = "outcome-toolkit-steps-shown";

export const COUNTRY_USA: MID = "COUNTRY 840";
export const MONTHS_OF_UNCERTAINTY = 5; // Number of months of uncertainty in the data

// HACK: Have to conditionalize this particular way so Playwright also works.
const maybeHost =
  "env" in import.meta ? import.meta.env?.VITE_API_HOST : process?.env?.VITE_API_HOST;
export const API_HOST = maybeHost ? maybeHost : "";

// API Routes
export const API_GEOMETRIES = (geo_type: string) => `${API_HOST}/api/${geo_type}/geometries`;
export const API_TARGET_PAYOUTS_URL = `${API_HOST}/api/v2/targets`;
export const API_TREE_URL = `${API_HOST}/api/state/tree`;
export const API_V2_BINS = `${API_HOST}/api/v2/bins`;
export const API_V2_DEMOGRAPHICS = `${API_HOST}/api/v2/demographics`;
export const API_V2_DETAILS = `${API_HOST}/api/v2/details`;
export const API_V2_OVERVIEW = `${API_HOST}/api/v2/overview`;
export const API_DATA_DETAILS = `${API_HOST}/api/v2/data-details`;

// Project information
export const API_PROJECT_INFO_URL = `${API_HOST}/protected/api/v2/project`;
