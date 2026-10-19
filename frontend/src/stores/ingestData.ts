/**
 * Adapter that replaces the Flask backend with the PopHIVE Ingest "bundle_health_outcomes" parquet files
 * (https://github.com/PopHIVE/Ingest/tree/main/data/bundle_health_outcomes) plus static geography
 * built by scripts/build-geography.mjs into public/local-data/.
 *
 * Each loader returns data in the same shape the old API routes did, so the rest of the app is unchanged.
 */
import { OUTCOME_DATA } from "@/stores/OUTCOME_DATA";
import type { SpatialGranularity } from "@/stores/SPATIAL_GRANULARITY_DATA";
import type {
  APITree,
  APIV2BinsType,
  APIV2DataDetails,
  APIV2DemographicsType,
  APIV2Details,
  AreaFeatureCollection,
  MetricBin,
  MID,
  OutcomeKeyType,
  RawTimeBin,
} from "@/types";
import { COUNTRY_USA } from "@/util/Consts";
import { asyncBufferFromUrl, parquetReadObjects } from "hyparquet";
import _ from "lodash";
import { DateTime } from "luxon";

const INGEST_BASE_URL: string =
  import.meta.env.VITE_INGEST_BASE_URL ??
  "https://raw.githubusercontent.com/PopHIVE/Ingest/main/data/bundle_health_outcomes/dist";
const LOCAL_DATA_URL = `${import.meta.env.BASE_URL}local-data`;

/** Same rank -> label scale the backend used (BinLabels in backend/app/configs/consts.py). */
const BIN_LABELS = [
  "Low Outlier",
  "Significantly Lower Than National Average",
  "Much Lower than National Average",
  "Lower than National Average",
  "Slightly Lower than National Average",
  "Slightly Higher than National Average",
  "Higher than National Average",
  "Much Higher than National Average",
  "Significantly Higher than National Average",
  "High Outlier",
];
const labelToRank = (label: string | null): number | null => {
  const i = BIN_LABELS.findIndex((l) => l.toLowerCase() === label?.toLowerCase());
  return i === -1 ? null : i;
};

type IngestRow = Record<string, unknown> & {
  geography: string;
  geography_type: string;
  time: Date;
};

/** How each outcome maps onto its Ingest parquet file. */
const SOURCES: Record<
  OutcomeKeyType,
  { file: string; geoType: string; prefix: string; low?: string; high?: string; label?: string }
> = {
  alcohol: {
    file: "alcohol.parquet",
    geoType: "county",
    prefix: "COUNTY",
    low: "alcohol_ems_rate_low",
    high: "alcohol_ems_rate_high",
    label: "alcohol_ems_rate_label",
  },
  opioid: {
    file: "opioid.parquet",
    geoType: "county",
    prefix: "COUNTY",
    low: "opioid_ems_rate_low",
    high: "opioid_ems_rate_high",
    label: "opioid_ems_rate_label",
  },
  soc: {
    file: "maternal.parquet",
    geoType: "zcta3",
    prefix: "ZCTA3",
    low: "maternal_soc_rate_low",
    high: "maternal_soc_rate_high",
    label: "maternal_soc_rate_label",
  },
  // ASCVD has continuous values (no bins), so bins are computed below.
  cardio: { file: "ascvd.parquet", geoType: "zcta3", prefix: "ZCTA3" },
};

async function readParquet(file: string): Promise<IngestRow[]> {
  const buffer = await asyncBufferFromUrl({ url: `${INGEST_BASE_URL}/${file}` });
  return (await parquetReadObjects({ file: buffer })) as IngestRow[];
}

/** The data is a single snapshot per source; represent it as the calendar month ending on `time`. */
function monthTimeBin(time: Date): RawTimeBin {
  const end = DateTime.fromJSDate(time, { zone: "utc" }).startOf("day");
  return [end.startOf("month").toISO(), end.toISO()].join("|");
}

function rowMid(row: IngestRow, prefix: string): MID | undefined {
  if (row.geography_type === "national") return COUNTRY_USA;
  return `${prefix} ${row.geography}`;
}

const num = (v: unknown): number | null => (v === null || v === undefined ? null : Number(v));

export type IngestOutcome = {
  details: APIV2Details;
  bins: APIV2BinsType[OutcomeKeyType];
  latestDate: Date;
};

/** Load one outcome from Ingest and convert it to the /api/v2/details + /api/v2/bins response shapes. */
export async function loadIngestOutcome(outcomeKey: OutcomeKeyType): Promise<IngestOutcome> {
  const src = SOURCES[outcomeKey];
  const { key: metricKey, keyT6mo } = OUTCOME_DATA[outcomeKey].metric;

  let rows = (await readParquet(src.file)).filter(
    (r) => r.geography_type === src.geoType || r.geography_type === "national"
  );
  if (outcomeKey === "cardio") {
    rows = rows.filter((r) => r.age === "Overall" && r.race_ethnicity === "Overall" && r.sex === "Overall");
  }

  const latestDate = _.maxBy(rows, (r) => r.time.valueOf())!.time;
  const binsByTime: Record<RawTimeBin, MetricBin[]> = {};
  const details: APIV2Details = {};

  for (const [, timeRows] of Object.entries(_.groupBy(rows, (r) => r.time.valueOf()))) {
    const timeBin = monthTimeBin(timeRows[0].time);
    let ranked: { mid: MID; value: number | null; bin_rank: number | null }[];

    if (outcomeKey === "cardio") {
      // ascvd_risk is a percentage (e.g. 5.1); the app's percent formatter expects a fraction.
      const withValues = timeRows.map((r) => ({ mid: rowMid(r, src.prefix)!, value: num(r.ascvd_risk) }));
      const local = withValues.filter((r) => r.mid !== COUNTRY_USA && r.value !== null);
      // Deciles across areas, as the backend did with pd.qcut(..., 10).
      const sorted = local.map((r) => r.value! / 100).sort((a, b) => a - b);
      const q = (p: number) => sorted[Math.min(sorted.length - 1, Math.floor(p * sorted.length))];
      const edges = _.range(11).map((i) => (i === 10 ? sorted[sorted.length - 1] : q(i / 10)));
      binsByTime[timeBin] = _.range(10).map((rank) => {
        const inBin = sorted.filter((v) => v >= edges[rank] && (rank === 9 ? v <= edges[10] : v < edges[rank + 1]));
        return {
          rank,
          rank_value: BIN_LABELS[rank],
          min: edges[rank],
          max: edges[rank + 1],
          mean: _.mean(inBin),
          median: inBin[Math.floor(inBin.length / 2)] ?? (edges[rank] + edges[rank + 1]) / 2,
          midpoint: (edges[rank] + edges[rank + 1]) / 2,
          representative: (edges[rank] + edges[rank + 1]) / 2,
        };
      });
      const rankOf = (v: number) => _.findLastIndex(edges.slice(0, 10), (e) => v >= e);
      ranked = withValues.map(({ mid, value }) => {
        const v = value === null ? null : value / 100;
        return { mid, value: v, bin_rank: v === null ? null : Math.max(0, rankOf(v)) };
      });
    } else {
      // Binned rates: the source provides each area's bin (low/high/label) but no point value.
      const bins: Record<number, MetricBin> = {};
      ranked = timeRows.map((r) => {
        const rank = labelToRank(r[src.label!] as string | null);
        const low = num(r[src.low!]);
        const high = num(r[src.high!]);
        if (rank !== null && low !== null && high !== null && !bins[rank]) {
          const mid = (low + high) / 2;
          bins[rank] = {
            rank,
            rank_value: BIN_LABELS[rank],
            min: low,
            max: high,
            mean: mid,
            median: mid,
            midpoint: mid,
            representative: mid,
          };
        }
        return { mid: rowMid(r, src.prefix)!, value: null, bin_rank: rank };
      });
      binsByTime[timeBin] = _.sortBy(Object.values(bins), "rank");
    }

    for (const { mid, value, bin_rank } of ranked) {
      const datum = { value, bin_rank };
      // Only one snapshot exists, so the six-month-average series is the same snapshot.
      _.set(details, [mid, metricKey, timeBin], datum);
      _.set(details, [mid, keyT6mo, timeBin], datum);
    }
  }

  return {
    details,
    bins: { [metricKey]: binsByTime, [keyT6mo]: binsByTime },
    latestDate,
  };
}

export function dataDetailsFromIngest(
  latest: Partial<Record<OutcomeKeyType, Date>>
): APIV2DataDetails {
  const one = (d?: Date) => ({
    earliest_date: d?.toUTCString() ?? "",
    latest_date: d?.toUTCString() ?? "",
    data_release: "PopHIVE Ingest bundle_health_outcomes",
  });
  return {
    alcohol: one(latest.alcohol),
    cardio: one(latest.cardio),
    opioid: one(latest.opioid),
    soc: one(latest.soc),
  };
}

async function getLocalJSON<T>(name: string): Promise<T> {
  const res = await fetch(`${LOCAL_DATA_URL}/${name}`);
  if (!res.ok) {
    throw new Error(`${res.status} fetching ${name}. Run "node scripts/build-geography.mjs" in frontend/.`);
  }
  return res.json();
}

export const loadLocalTree = () => getLocalJSON<APITree>("tree.json");

export const loadLocalGeometry = (key: Exclude<SpatialGranularity, "COUNTRY">) =>
  getLocalJSON<AreaFeatureCollection>(`geometries-${key}.json`);

/** Area names, populations, adjacency and intersections in the /api/v2/demographics shape.
 * No ACS demographic breakdowns are included, so demographic_categories is empty. */
export async function loadLocalDemographics(): Promise<APIV2DemographicsType> {
  const data = await getLocalJSON<APIV2DemographicsType["data"]>("areas.json");
  return {
    metadata: {
      source: "Population: PopHIVE Ingest bundle_health_outcomes denominators. Geography: US Census Bureau.",
      demographic_categories: {},
      display_names: {},
    },
    data,
  };
}
