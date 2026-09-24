import { DateTime, Duration } from "luxon";
import type { TimeBin, RawTimeBin } from "@/types";
import { timeBinToString } from "@/util/formatters";

/**
 * Given a TimeBin string like `"2022-01-01T00:00:00+00:00|2023-12-31T00:00:00+00:00"`,
 * return a DateTime object for each end point. Returns invalid times if format is invalid.
 */
export function timeBinToDates(rawTimeBin: RawTimeBin): [start: DateTime, end: DateTime] {
  const [s, e] = rawTimeBin.split("|").map((s) => DateTime.fromISO(s));
  if (!s.isValid || !e.isValid) {
    console.error("Could not convert time bin string: ", rawTimeBin);
  }
  return [s, e];
}

/**
 * Given a time bin string like `"2022-01-01T00:00:00+00:00|2023-12-31T00:00:00+00:00"`
 * return the toMillis() result for the start and end dates (`[1640995200000, 1703980800000]`)
 */
export function timeBinToTimes(timeBin: string): [start: number, end: number] {
  return timeBinToDates(timeBin).map((d) => d.valueOf()) as [number, number];
}

/** Given start and end DateTimes, format as a TimeBin string. */
export function datesToTimeBin(start: DateTime, end: DateTime) {
  return [start.toISO(), end.toISO()].join("|");
}

export function makeTimeBin(raw: RawTimeBin): TimeBin {
  const [startDate, endDate] = timeBinToDates(raw);
  return {
    raw,
    startDate,
    endDate,
    duration: Duration.fromMillis(endDate.valueOf() - startDate.valueOf()),
    asString: timeBinToString(raw),
  };
}

export function formattedDate(rawDateString: string) {
  // timezone is utc, keep it as utc to show expected day (ex: April 30 vs April 29)
  const date = DateTime.fromHTTP(rawDateString, { zone: "utc" });
  return date.toFormat("MMMM dd, yyyy");
}
