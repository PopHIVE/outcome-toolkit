/**
 * Adapter that replaces the Flask backend with the PopHIVE health-outcomes "bundle_outcome_toolkit"
 * (https://github.com/PopHIVE/health-outcomes/tree/main/data/bundle_outcome_toolkit), copied into
 * public/local-data/health-outcomes/ by scripts/sync-health-outcomes.mjs, plus static geography
 * built by scripts/build-geography.mjs into public/local-data/.
 *
 * The bundle holds only what the site shows: each county / ZCTA3 as its monthly and six-month-average bin
 * (rank + low/high range + label), and precise values for the nation only. Bins are computed in the bundle's
 * build.R, so this file just reshapes them.
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
  OutcomeKeyType,
  RawTimeBin,
} from "@/types";
import { COUNTRY_USA } from "@/util/Consts";
import _ from "lodash";
import { DateTime } from "luxon";

const LOCAL_DATA_URL = `${import.meta.env.BASE_URL}local-data`;
/** Where the bundle's dist/ files live. Override (e.g. with a raw.githubusercontent.com URL) via env. */
const HEALTH_OUTCOMES_URL: string =
  import.meta.env.VITE_HEALTH_OUTCOMES_URL ?? `${LOCAL_DATA_URL}/health-outcomes`;

type Row = Record<string, string | null>;

/** How each outcome maps onto a bundle file. */
const SOURCES: Record<
  OutcomeKeyType,
  { file: string; measure: string; prefix: string; /** Source unit -> app unit. */ scale: number }
> = {
  alcohol: { file: "alcohol.csv.gz", measure: "alcohol_ems_rate", prefix: "COUNTY", scale: 1 },
  opioid: { file: "opioid.csv.gz", measure: "opioid_ems_rate", prefix: "COUNTY", scale: 1 },
  soc: { file: "maternal.csv.gz", measure: "maternal_soc_rate", prefix: "ZCTA3", scale: 1 },
  // ascvd_risk is a percentage (e.g. 5.1); the app's percent formatter expects a fraction.
  cardio: { file: "ascvd.csv.gz", measure: "ascvd_risk", prefix: "ZCTA3", scale: 0.01 },
};

/** Minimal CSV parser (handles quoted fields). "NA" and "" become null. */
function parseCSV(text: string): Row[] {
  const records: string[][] = [];
  let field = "";
  let record: string[] = [];
  let quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') {
        field += '"';
        i++;
      } else if (c === '"') {
        quoted = false;
      } else {
        field += c;
      }
    } else if (c === '"') {
      quoted = true;
    } else if (c === ",") {
      record.push(field);
      field = "";
    } else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      record.push(field);
      records.push(record);
      field = "";
      record = [];
    } else {
      field += c;
    }
  }
  if (field || record.length) {
    record.push(field);
    records.push(record);
  }
  const [header, ...body] = records;
  return body
    .filter((r) => r.length === header.length)
    .map((r) => _.zipObject(header, r.map((v) => (v === "NA" || v === "" ? null : v))));
}

/** Fetch a (possibly gzipped) CSV. Servers may or may not have already decoded the gzip, so sniff the magic bytes. */
async function readCSV(file: string): Promise<Row[]> {
  const res = await fetch(`${HEALTH_OUTCOMES_URL}/${file}`);
  if (!res.ok) {
    throw new Error(
      `${res.status} fetching ${file}. Run "node scripts/sync-health-outcomes.mjs" in frontend/.`
    );
  }
  const bytes = new Uint8Array(await res.arrayBuffer());
  if (bytes[0] === 0x1f && bytes[1] === 0x8b) {
    const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
    return parseCSV(await new Response(stream).text());
  }
  return parseCSV(new TextDecoder().decode(bytes));
}

/** `time` is the first day of the month; the time bin spans that calendar month. */
function monthTimeBin(time: string): RawTimeBin {
  const start = DateTime.fromISO(time, { zone: "utc" }).startOf("month");
  return [start.toISO(), start.endOf("month").startOf("day").toISO()].join("|");
}

const num = (v: string | null | undefined): number | null => {
  if (v === null || v === undefined) return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
};

export type IngestOutcome = {
  details: APIV2Details;
  bins: APIV2BinsType[OutcomeKeyType];
  earliestDate: Date;
  latestDate: Date;
};

/** Load one outcome and convert it to the /api/v2/details + /api/v2/bins response shapes. */
export async function loadIngestOutcome(outcomeKey: OutcomeKeyType): Promise<IngestOutcome> {
  const { file, measure, prefix, scale } = SOURCES[outcomeKey];
  const { key: metricKey, keyT6mo } = OUTCOME_DATA[outcomeKey].metric;
  const rows = await readCSV(file);

  const binsByTime: Record<RawTimeBin, Record<number, MetricBin>> = {};
  const details: APIV2Details = {};
  const times = new Set<string>();

  for (const r of rows) {
    times.add(r.time!);
    const timeBin = monthTimeBin(r.time!);
    const monthBins = (binsByTime[timeBin] ??= {});
    const mid = r.geography_type === "national" ? COUNTRY_USA : `${prefix} ${r.geography}`;

    // The monthly and six-month-average series are ranked against the same bins for each month.
    for (const [m, key] of [
      [measure, metricKey],
      [`${measure}_6mo`, keyT6mo],
    ] as const) {
      const rank = num(r[`${m}_rank`]);
      const low = num(r[`${m}_low`]);
      const high = num(r[`${m}_high`]);
      if (rank !== null && low !== null && high !== null && !monthBins[rank]) {
        const midpoint = ((low + high) / 2) * scale;
        monthBins[rank] = {
          rank,
          rank_value: r[`${m}_label`] ?? "",
          min: low * scale,
          max: high * scale,
          mean: midpoint,
          median: midpoint,
          midpoint,
          representative: midpoint,
        };
      }
      // Only national rows have a value; areas are shown by their bin only.
      const v = num(r[m]);
      _.set(details, [mid, key, timeBin], { value: v === null ? null : v * scale, bin_rank: rank });
    }
  }

  const sortedBins = _.mapValues(binsByTime, (b) => _.sortBy(Object.values(b), "rank"));
  const sortedTimes = [...times].sort();
  return {
    details,
    // store.metricBins reads the monthly key for both series.
    bins: { [metricKey]: sortedBins, [keyT6mo]: sortedBins },
    earliestDate: DateTime.fromISO(sortedTimes[0], { zone: "utc" }).toJSDate(),
    latestDate: DateTime.fromISO(sortedTimes[sortedTimes.length - 1], { zone: "utc" })
      .endOf("month")
      .startOf("day")
      .toJSDate(),
  };
}

export function dataDetailsFromIngest(
  dates: Partial<Record<OutcomeKeyType, { earliest: Date; latest: Date }>>
): APIV2DataDetails {
  const one = (d?: { earliest: Date; latest: Date }) => ({
    earliest_date: d?.earliest.toUTCString() ?? "",
    latest_date: d?.latest.toUTCString() ?? "",
    data_release: "PopHIVE health-outcomes bundle_outcome_toolkit",
  });
  return {
    alcohol: one(dates.alcohol),
    cardio: one(dates.cardio),
    opioid: one(dates.opioid),
    soc: one(dates.soc),
  };
}

async function getLocalJSON<T>(name: string): Promise<T> {
  const res = await fetch(`${LOCAL_DATA_URL}/${name}`);
  if (!res.ok) {
    throw new Error(
      `${res.status} fetching ${name}. Run "node scripts/build-geography.mjs" in frontend/.`
    );
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
      source:
        "Population: PopHIVE Ingest bundle_health_outcomes denominators. Geography: US Census Bureau.",
      demographic_categories: {},
      display_names: {},
    },
    data,
  };
}
