// TODO: Source these from DB

export const DemographicKeys = ["age", "re", "income"] as const;
export type DemographicKeyType = (typeof DemographicKeys)[number];

type DemographicBlock = {
  // CSS-safe key
  key: DemographicKeyType;
  // TODO: get rid of need for db_group by fixing the API. Ticket OUTCOME_TOOLKIT-484
  // Which object the API returns this info in.
  db_group: "acs_estimates" | "demographics";
  // Key into the object found by db_group
  db_key: string;
  // Human-readable label
  label: string;
  // TODO: Bins for each demographic? Ticket OUTCOME_TOOLKIT-484
};
export const DEMOGRAPHIC_DATA: Record<DemographicKeyType, DemographicBlock> = {
  age: { key: "age", db_group: "demographics", db_key: "age", label: "Age" },
  income: { key: "income", db_group: "acs_estimates", db_key: "income", label: "Income" },
  re: { key: "re", db_group: "demographics", db_key: "race/ethnicity", label: "Race/Ethnicity" },
};
