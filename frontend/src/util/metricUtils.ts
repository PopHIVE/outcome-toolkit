import { useDataStore, type DatumProps } from "@/stores/data";
import { OUTCOME_DATA, type OutcomeType } from "@/stores/OUTCOME_DATA";
import { type MetricData, type MetricKeyType, type MID, type OutcomeKeyType } from "@/types";
import _ from "lodash";

export function key2outcome(m: OutcomeKeyType): OutcomeType {
  return OUTCOME_DATA[m];
}

export function outcome2metric(m: OutcomeKeyType): MetricKeyType {
  return key2outcome(m).metric.key;
}

const complainAboutMetricAverageData = _.once(() => {
  console.error("Data was not ready during averaging.");
});
/**
 * Compute the metric data as population-weighted mean of all selected area metrics, or undefined if the data was weird.
 * For metrics without specific values, the `value` is the pop-weighted average of bin representatives.
 *
 * NOTE: This is a composable, and should only be called at the outer level of a setup script, or inside another composable.
 */
export function areaMetricAverage(props: { mids: Set<MID> } & DatumProps): MetricData {
  const { dataFilterKey, mids, outcomeKey, timeBin } = props;
  const result: MetricData = { bin_rank: null, value: null };

  const dataStore = useDataStore();
  if (!dataStore.dataIsReady(outcomeKey)) {
    complainAboutMetricAverageData();
    return result;
  }

  const datumProps: DatumProps = { dataFilterKey, outcomeKey, timeBin };
  const metricBins = dataStore.metricBins(datumProps);

  const metric = key2outcome(outcomeKey).metric;

  // Use null to capture the sense of "we have no metric data for this area"
  let metricTimesPopTotal: number | null = null;
  let rankRepTotal: number | null = null;
  let populationTotal = 0;

  const dataNotFound: string[] = [];

  for (const mid of mids) {
    const datum = dataStore.overviewDatum({
      ...datumProps,
      mid,
    });

    // TODO: What to do about missing values? They're skipped here, but might need to be exposed to user.
    if (!datum) {
      dataNotFound.push(mid);
      continue;
    }

    const pop = dataStore.population(mid);
    if (!pop) {
      // Skip zero-population areas
      continue;
    }

    if (metric.hasMetricValues) {
      // Only sum metric over areas which have metric values reported.
      // Null means "we have no metric data for this area"
      if (datum.value !== null) {
        metricTimesPopTotal = (metricTimesPopTotal ?? 0) + datum.value * pop;
        populationTotal += pop;
      }
    } else if (datum.bin_rank !== null && !!metricBins[datum.bin_rank]) {
      // Only sum metric over areas which have rank values reported.
      // Null means "we have no rank data for this area"
      rankRepTotal = (rankRepTotal ?? 0) + metricBins[datum.bin_rank].representative * pop;
      populationTotal += pop;
    }
  }

  if (dataNotFound.length) {
    console.error("When averaging, no overview data found for some points:", {
      dataFilterKey,
      outcomeKey,
      timeBin: timeBin?.asString,
      dataNotFound,
    });
  }

  if (populationTotal === 0) {
    return result;
  }

  // Compute and return averages (or nulls)
  if (metric.hasMetricValues) {
    if (metricTimesPopTotal === null) {
      return result;
    }
    result.value = metricTimesPopTotal / populationTotal;
    result.bin_rank =
      dataStore.metricBin({
        metricValue: result.value,
        dataFilterKey,
        outcomeKey,
        timeBin,
      })?.rank ?? null;
  } else {
    if (rankRepTotal === null) {
      return result;
    }
    result.value = rankRepTotal / populationTotal;
    const avgBin = dataStore.metricBin({
      metricValue: result.value,
      dataFilterKey,
      outcomeKey,
      timeBin,
    });
    result.bin_rank = avgBin?.rank ?? null;
  }
  return result;
}

/** Take a DiD measurement (which can be in the range -Inf to +Inf, but is "usually" in the range [-50%, 50%]) and
 * translate it to a reasonable scale number in [0, 1].
 */
export function normalizeDiD(d: number | undefined | null): number | null {
  if (_.isNil(d) || _.isNaN(d)) {
    return null;
  } else if (!_.isFinite(d)) {
    return d > 0 ? 1 : 0;
  } else {
    const k = 0.25; // k chosen so a 30% increase/decrease, our total target, is at about 5% or 95%.
    const norm = 0.5 + Math.atan(d * k) / Math.PI;
    return norm;
  }
}
