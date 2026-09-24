import { isSpatialGranularity } from "@/stores/SPATIAL_GRANULARITY_DATA";
import { timeBinToTimes } from "@/util/dateUtils";
import _ from "lodash";
import { DateTime, Duration } from "luxon";
import * as RT from "runtypes";
import { makeEmptyPayouts } from "./stores/data";

export type ColorRamp = Record<number, string>;

export const MIDSpec = RT.String.withConstraint(
  (s) =>
    /(?:zcta3|zcta5|county|state|country|project|user)\s+\d+/i.test(s) ||
    `Invalid MID format "${s}"`
);
/**
 * Marker type for M(orpheus) IDs. MIDs are a string like `ZCTA3 010` or `County 12345`, derived from the Census data.
 */
export type MID = RT.Static<typeof MIDSpec>;
export const isMID = MIDSpec.guard;

export const RawTimeBinSpec = RT.String.withConstraint((u) => {
  const [s, e] = timeBinToTimes(u);
  return !isNaN(s) && !isNaN(e);
});
/**
 * This is a string like "Start Time|End Time" where times are in ISO format, e.g.:
 * '2022-01-01T00:00:00+00:00|2022-12-31T00:00:00+00:00'
 */
export type RawTimeBin = RT.Static<typeof RawTimeBinSpec>;
export const isRawTimeBin = RawTimeBinSpec.guard;

export const DateTimeStringSpec = RT.String.withConstraint((s) => DateTime.isDateTime(s));
export const DateTimeSpec = RT.Unknown.withConstraint<DateTime>(DateTime.isDateTime);

export const DurationSpec = RT.Unknown.withConstraint<Duration>(Duration.isDuration);

/**
 * This is a string for a datetime in ISO format, e.g.: '2022-01-01T00:00:00+00:00'
 */
export type DateTimeStringType = RT.Static<typeof DateTimeStringSpec>;
export const isDateTimeString = DateTimeStringSpec.guard;

// TODO: Source from a database table.

export const OutcomeKeySpec = RT.Union(
  RT.Literal("soc"),
  RT.Literal("opioid"),
  RT.Literal("cardio"),
  RT.Literal("alcohol")
);
export const OutcomeKeyTypes = OutcomeKeySpec.alternatives;

export type OutcomeKeyType = RT.Static<typeof OutcomeKeySpec>;
export const OUTCOME_KEYS = OutcomeKeySpec.alternatives.map((k) => k.value);
export const isOutcomeKeyType = OutcomeKeySpec.guard;

/** The database name for a metric, like "any_soc_rate". */
export const MetricKeySpec = RT.String.withConstraint((s) => s.length > 0);
export type MetricKeyType = RT.Static<typeof MetricKeySpec>;
export const isMetricKeyType = MetricKeySpec.guard;

export type MetricHistoryGraphSize = "collapsed" | "normal" | "expanded";

/** An individual bin for a metric */
export const MetricBinSpec = RT.Object({
  max: RT.Number,
  mean: RT.Number,
  median: RT.Number,
  midpoint: RT.Number,
  min: RT.Number,
  rank: RT.Number,
  rank_value: RT.String, // e.g. "Significantly Lower Than National Average"
  representative: RT.Number,
});
export type MetricBin = RT.Static<typeof MetricBinSpec>;
export const isMetricBin = MetricBinSpec.guard;

/**
 * Store additional data about each time bin to make them easier to address/compute over.
 * TODO: Figure out if any of this should get promoted back to the DB.
 */
export const TimeBinSpec = RT.Object({
  /** Raw time string, two ISOs joined with a pipe. May end up deprecated. */
  raw: RawTimeBinSpec,
  /** User-friendly format like "Jan 2022 to Mar 2022" */
  asString: RT.String,
  startDate: DateTimeSpec,
  endDate: DateTimeSpec,
  /** Duration between start and end dates */
  duration: DurationSpec,
});
export type TimeBin = RT.Static<typeof TimeBinSpec>;
export const isTimeBin = TimeBinSpec.guard;

/**
 * User role, currently admin (can see all projects) vs. proposal author (can see their projects) vs. general public (can see sample projects)
 * May eventually be replaced by role-based authentication.
 */
const RoleKeySpec = RT.Union(RT.Literal("admin"), RT.Literal("proposer"), RT.Literal("public"));
export type RoleKeyType = RT.Static<typeof RoleKeySpec>;
export const isRoleKeyType = RoleKeySpec.guard;

const RoleSpec = RT.Object({
  key: RoleKeySpec,
  icon: RT.String,
  label: RT.String,
  description: RT.String,
});
export type RoleType = RT.Static<typeof RoleSpec>;
export const isRoleType = RoleSpec.guard;

export const OverviewDataSpec = RT.Record(MIDSpec, RT.Number);
export type OverviewData = RT.Static<typeof OverviewDataSpec>;
export const isOverviewData = OverviewDataSpec.guard;

/* NOTE: We don't use RT to validate the GeoJSON because it would impose a tremendous load on the front end at load time. */
/** Custom properties found on each of our GeoJSON shapes. Other things are passed, but this is all we use. */
export type AreaShapeProps = { mid: MID };
/** GeoJSON feature with custom props (in our case, MID). */
export type AreaFeature = GeoJSON.Feature<GeoJSON.Geometry, AreaShapeProps>;
/** GeoJSON feature collection containing Features with AreaShapeProps as their properties. */
export type AreaFeatureCollection = GeoJSON.FeatureCollection<GeoJSON.Geometry, AreaShapeProps>;

/** Represents a state and all its intersected areas, with nice labels, for AreaList. */
export const AreaListStateSpec = RT.Object({
  mid: MIDSpec /* State */,
  areas: RT.Record(MIDSpec, RT.String /* label */),
});
export type AreaListState = RT.Static<typeof AreaListStateSpec>;
export const isAreaListState = AreaListStateSpec.guard;

export const MetricDataSpec = RT.Object({
  bin_rank: RT.Union(RT.Number, RT.Null),
  value: RT.Union(RT.Number, RT.Null),
});
export type MetricData = RT.Static<typeof MetricDataSpec>;
export const isMetricData = MetricDataSpec.guard;

export const AreaDemographicsSpec = RT.Intersect(
  RT.Object({
    adjacency: RT.Optional(RT.Array(MIDSpec)),
    intersections: RT.Record(RT.String.withConstraint(isSpatialGranularity), RT.Array(MIDSpec)),
  }),
  RT.Record(
    RT.String /* "acs.between_60k_75k", i.e. keys from demographic_categories. */,
    RT.Union(
      RT.Null,
      RT.Number,
      RT.String,
      RT.Array(MIDSpec),
      RT.Record(RT.String, RT.Array(MIDSpec))
    )
  )
);

export type AreaDemographicsType = RT.Static<typeof AreaDemographicsSpec>;

/* ****** PROJECT INFO ****** */
// FIXME Tighten constraint when back end inserts project data correctly
export const ProjectIDSpec = RT.String.withConstraint((s) => /^(PROJECT\s+)?\d+$/.test(s));
export type ProjectID = RT.Static<typeof ProjectIDSpec>;

export const UserIDSpec = RT.String.withConstraint((s) => /^USER \d+$/.test(s));
export type UserID = RT.Static<typeof UserIDSpec>;

export const ProjectRoleSpec = RT.Union(
  RT.Literal("Health Accelerator"),
  RT.Literal("Outcome Buyer")
);
/** What role this user plays on this project (HA or OB). Does not impact permissions currently. */
export type ProjectRole = RT.Static<typeof ProjectRoleSpec>;

export const PayoutIntervalSpec = RT.Union(
  RT.Literal("6"),
  RT.Literal("12"),
  RT.Literal("18"),
  RT.Literal("24"),
  RT.Literal("30"),
  RT.Literal("36"),
  RT.Literal("baseline"),
  RT.Literal("total")
);
export const PAYOUT_INTERVALS = PayoutIntervalSpec.alternatives.map((m) => m.value);
export type PayoutInterval = RT.Static<typeof PayoutIntervalSpec>;

/** The payout rate record type for the payout rate type used for the static rate card */
export const PayoutRateLineTypeSpec = RT.Object({
  payout: RT.Number,
  target: RT.Number,
});
export type PayoutRateLineType = RT.Static<typeof PayoutRateLineTypeSpec>;
export const isPayoutLineRateType = PayoutRateLineTypeSpec.guard;

/** The payout rate type for the static rate card */
export const PayoutRateTypeSpec = RT.Object({
  payouts: RT.Record(PayoutIntervalSpec, PayoutRateLineTypeSpec),
  payoutStartDate: DateTimeStringSpec,
  payoutPercentImprovement: RT.String,
  payoutPartialStatement: RT.String,
});
export type PayoutRateType = RT.Static<typeof PayoutRateTypeSpec>;
export const isPayoutRateType = PayoutRateTypeSpec.guard;

/** TARGET PAYOUT INFO */
export const APITargetPayoutDetailSpec = RT.Object({
  outcome: OutcomeKeySpec,
  period: PayoutIntervalSpec,
  minimum_payout: RT.Number,
  maximum_payout: RT.Number,
  target_rate: RT.Number,
});
export type APITargetPayoutDetail = RT.Static<typeof APITargetPayoutDetailSpec>;
/* API returns this as a flat list. We reorganize it in fetching.ts for quicker access. */
export const APITargetPayoutsSpec = RT.Object({
  targets: RT.Array(APITargetPayoutDetailSpec),
});
export type APITargetPayoutsType = RT.Static<typeof APITargetPayoutsSpec>;

export type PayoutTarget = {
  outcomeKey: OutcomeKeyType;
  period: PayoutInterval;
  minimumPayout: number;
  maximumPayout: number;
  targetRate: number;
};

/** Project page filter options */
export type DataFilterKeyType = "t6mo" | "monthly" | "did";
export type DataFilterType = {
  // Unique key
  key: DataFilterKeyType;

  // The key to use to index into a MetricType to get the right value for this filter.
  apiMetricKey: "keyT6mo" | "key";
  // Long description
  description: string;
  // Short human-readable name
  label: string;
};

/** The list of valid keys into MetricType for metric values.
 * Currently, the raw data ("monthly") and the trailing 6 month average ("t6mo") are available for all uses;
 * within a specific project, the Difference in Differences ("did") can also be selected, which is computed
 * from the project area's t6mo and the national average's t6mo.
 */
export const DATA_FILTERS: Record<DataFilterKeyType, DataFilterType> = {
  monthly: {
    key: "monthly",

    apiMetricKey: "key",
    description:
      "Data as measured month by month. Monthly data is not used for total calculations, but may be useful as a reference.",
    label: "Monthly data",
  },
  t6mo: {
    key: "t6mo",

    apiMetricKey: "keyT6mo",
    description:
      "The average of performance for the past six months. For example, the data point for June 2025 is for data from January 2025 through June 2025.",
    label: "Six-month rolling average",
  },
  did: {
    key: "did",

    apiMetricKey: "keyT6mo", // DiD is computed on the six month averages.
    description: "How the region compares to the national and regional baselines",
    label: "Project Performance",
  },
};

export function key2dataFilter(key: DataFilterKeyType): DataFilterType {
  return DATA_FILTERS[key];
}
export function isDataFilterKeyType(s: unknown): s is DataFilterKeyType {
  return _.isString(s) && s in DATA_FILTERS;
}

/*** Data from APIs. ***/

export const APIV2DemographicsSpec = RT.Object({
  metadata: RT.Object({
    source: RT.String,
    demographic_categories: RT.Record(RT.String, RT.Object({ bands: RT.Array(RT.String) })),
    display_names: RT.Record(RT.String, RT.String),
  }),
  data: RT.Record(MIDSpec, AreaDemographicsSpec),
});
export type APIV2DemographicsType = RT.Static<typeof APIV2DemographicsSpec>;

export const APIAreaListSpec = RT.Record(MIDSpec, RT.Record(MIDSpec, RT.String));
/** Dictionary by state MID. Inner dictionaries are "mid: label", e.g.,
 * ```json
 * {
 *   "STATE 01": {
 *     "COUNTY 01021": "Smith County, AL (Pop: 45.01K)",
 *     "ZCTA3 894": "ZCTA3 894xx: Churchill County, Douglas County, Elk County, Humboldt County, and 6 more (NV); Major County (OR); Sierra County (CA) (Pop: 323.32K)",
 *   }
 * }
 * ```
 */
export type APIAreaList = RT.Static<typeof APIAreaListSpec>;
export const isAPIAreaList = APIAreaListSpec.guard;

export const APIV2DetailsSpec = RT.Record(
  MIDSpec,
  RT.Record(MetricKeySpec, RT.Record(RawTimeBinSpec, MetricDataSpec))
);
export type APIV2Details = RT.Static<typeof APIV2DetailsSpec>;
export const isAPIV2Details = APIV2DetailsSpec.guard;

const OutcomeDataDetails = RT.Object({
  earliest_date: RT.String,
  latest_date: RT.String,
  data_release: RT.String,
});

// Define the overall API response structure
export const APIV2DataDetailsSpec = RT.Object({
  alcohol: OutcomeDataDetails,
  cardio: OutcomeDataDetails,
  opioid: OutcomeDataDetails,
  soc: OutcomeDataDetails,
});

export type APIV2DataDetails = RT.Static<typeof APIV2DataDetailsSpec>;
export const isAPIV2DataDetails = APIV2DataDetailsSpec.guard;

export const APITreeSpec = RT.Record(MIDSpec, RT.Record(MIDSpec, RT.String));
export type APITree = RT.Static<typeof APITreeSpec>;
export const isAPITree = APITreeSpec.guard;

export const APIUserSpec = RT.Object({
  id: UserIDSpec,
  email: RT.String,
  first_name: RT.String,
  last_name: RT.String,
  organization: RT.String,
  role: RT.String, // TODO: Re-add check for Health Accel vs. Outcome Buyer
  // FUTURE: Ignore list of projects associated with user as we don't want to parse it right now
});
export type UserType = RT.Static<typeof APIUserSpec>;

export const APIProjectMeasurementSpec = RT.Object({
  period: PayoutIntervalSpec,
  date_of_payout: RT.String,
  national_metric: RT.Union(RT.Null, RT.Number),
  project_metric: RT.Union(RT.Null, RT.Number),
  mid_metrics: RT.Array(RT.Object({ mid: MIDSpec, metric: RT.Number })),
  actual_payout: RT.Union(RT.Null, RT.Number),
});
export type APIProjectMeasurement = RT.Static<typeof APIProjectMeasurementSpec>;
export type ProjectMeasurement = {
  period: PayoutInterval;
  date: DateTime;
  nationalMetric: number;
  projectMetric: number;
  payout: number;
  midMetrics: Record<MID, number>; // As of the time when the payout occurred
};
export function api2ProjectMeasurement(s: APIProjectMeasurement): ProjectMeasurement {
  return {
    period: s.period,
    date: DateTime.fromHTTP(s.date_of_payout),
    nationalMetric: s.national_metric ?? 0,
    projectMetric: s.project_metric ?? 0,
    payout: s.actual_payout ?? 0,
    midMetrics: _.fromPairs(s.mid_metrics.map(({ mid, metric }) => [mid, metric])),
  };
}
//TODO delete unused function below?
export function makeProjectMeasurement(
  project: ProjectType,
  p: Pick<ProjectMeasurement, "period" | "nationalMetric" | "projectMetric" | "payout">
): ProjectMeasurement {
  return {
    ...p,
    date: project.performancePeriodFrom.plus({ months: _.isNumber(p.period) ? p.period : 0 }),
    midMetrics: {},
  };
}

export const PROJECT_PERFORMERS = [
  {
    performerType: "AHA",
    description: "Health Accelerator",
    details:
      "Health accelerators have been awarded program contracts and are tracked in the Outcome Toolkit program.",
  },
  {
    performerType: "PHA",
    description: "Participating Health Accelerator",
    details:
      "Participating health accelerators are tracked in the Outcome Toolkit program, but are not paid out as a part of the program.",
  },
];

export const APIProjectSpec = RT.Object({
  id: ProjectIDSpec,
  outcome: OutcomeKeySpec,
  project_name: RT.String,
  performer_type: RT.Union(RT.Literal("AHA"), RT.Literal("PHA")),
  performance_period_from: RT.String.withConstraint((s) => DateTime.fromHTTP(s).isValid),
  performance_period_to: RT.String.withConstraint((s) => DateTime.fromHTTP(s).isValid),
  project_measurements: RT.Array(APIProjectMeasurementSpec),
  users: RT.Array(APIUserSpec),
  areas: RT.Array(RT.Object({ mid: MIDSpec, type: RT.String })),
});
/** Non-API type for projects, with JS-style names and tighter constraints on values. Doesn't go over the wire so doesn't need RT. */
export type ProjectMeasurementsType = Record<PayoutInterval, ProjectMeasurement | null>;
export type ProjectType = {
  id: ProjectID;
  outcomeKey: OutcomeKeyType;
  projectName: string;
  performerType: "PHA" | "AHA";
  performancePeriodFrom: DateTime;
  performancePeriodTo: DateTime;
  projectMeasurements: ProjectMeasurementsType;
  users: UserType[];
  areas: MID[];
};
export type APIProjectType = RT.Static<typeof APIProjectSpec>;
export function api2Project(p: APIProjectType): ProjectType {
  return {
    id: p.id,
    outcomeKey: p.outcome,
    projectName: p.project_name,
    performerType: p.performer_type,
    performancePeriodFrom: DateTime.fromHTTP(p.performance_period_from),
    performancePeriodTo: DateTime.fromHTTP(p.performance_period_to),
    projectMeasurements: _.keyBy(
      p.project_measurements.map(api2ProjectMeasurement),
      "period"
    ) as Record<PayoutInterval, ProjectMeasurement>, // NOTE: keyBy doesn't emit the right type, so we have to cast it here
    users: p.users,
    areas: p.areas.map((m) => m.mid),
  };
}

export function api2TargetPayoutDetail(s: APITargetPayoutDetail): PayoutTarget {
  return {
    outcomeKey: s.outcome,
    period: s.period,
    minimumPayout: s.minimum_payout,
    maximumPayout: s.maximum_payout,
    targetRate: s.target_rate,
  };
}
export type TargetPayoutsType = Record<OutcomeKeyType, Record<PayoutInterval, PayoutTarget>>;

/** Convert the flat list from the API into a nested data object for speed of retrieval and usage. */
export function api2TargetPayout({ targets }: APITargetPayoutsType): TargetPayoutsType {
  const out: TargetPayoutsType = makeEmptyPayouts();
  for (const t of targets) {
    out[t.outcome][t.period] = api2TargetPayoutDetail(t);
  }
  return out;
}

export const APIProjectsRouteSpec = RT.Object({ projects: RT.Array(APIProjectSpec) });

export const APIV2VersionSpec = RT.Object({
  version: RT.String,
  dataVersion: RT.String,
  tag: RT.String,
});
export type APIV2VersionType = RT.Static<typeof APIV2VersionSpec>;

export const APIV2BinsTypeSpec = RT.Record(
  RT.String.withConstraint(isOutcomeKeyType),
  RT.Record(MetricKeySpec, RT.Record(RawTimeBinSpec, RT.Array(MetricBinSpec)))
);

export type APIV2BinsType = RT.Static<typeof APIV2BinsTypeSpec>;
export const isAPIV2BinsType = APIV2BinsTypeSpec.guard;

export const APIV2PopulationSpec = RT.Record(MIDSpec, RT.Number);
