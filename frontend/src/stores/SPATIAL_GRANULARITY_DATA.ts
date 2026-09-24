// TODO: Source from a database table

import _ from "lodash";

export const GRANULARITIES = ["COUNTRY", "STATE", "ZCTA3", "COUNTY"] as const;
export type SpatialGranularity = "COUNTRY" | "STATE" | "ZCTA3" | "COUNTY";
export function isSpatialGranularity(s: unknown): s is SpatialGranularity {
  // HACK: Shouldn't need to cast 's as SpatialGranularity' but can't figure out how to make TS less picky.
  return _.isString(s) && GRANULARITIES.includes(s as SpatialGranularity);
}

export const SPATIAL_GRANULARITY_DATA: Record<
  SpatialGranularity,
  {
    key: SpatialGranularity;
    label: string;
    plural: string;
    definition: string;
  }
> = {
  COUNTY: {
    key: "COUNTY",
    label: "County",
    plural: "Counties",
    definition:
      "County-level areas (including Boroughs, Parishes, etc.) within a State or Territory.",
  },
  COUNTRY: {
    key: "COUNTRY",
    label: "Country",
    plural: "Countries",
    definition: "National area, i.e. data pertaining to the entire country.",
  },
  STATE: {
    key: "STATE",
    label: "State",
    plural: "States",
    definition:
      "State-level divisions of the USA, including territories such as Puerto Rico and Guam.",
  },
  ZCTA3: {
    key: "ZCTA3",
    label: "ZCTA3",
    plural: "ZCTA3s",
    definition:
      "ZIP Code Tabulation Areas (ZCTAs) are statistical entities developed by the US Census Bureau. ZCTA3s correspond roughly to the first three digits of five-digit ZIP Codes (e.g., 100xx for New York City).",
  },
};
