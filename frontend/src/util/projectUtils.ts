import { useDataStore, type DatumProps } from "@/stores/data";
import { type PayoutInterval, type PayoutTarget, type ProjectType, type TimeBin } from "@/types";
import _ from "lodash";
import { DateTime } from "luxon";
import { areaMetricAverage, outcome2metric } from "./metricUtils";

/** Get which period the project is currently in the midst of, based on the current date or one specified. */
export function projectPeriod(
  project: ProjectType,
  // FIXME DateTime.now() Query date should default to "now", not to a fixed point in the past when we actually had data.
  queryDate: DateTime = DateTime.fromObject({ year: 2024, month: 9 })
): PayoutInterval {
  const months = queryDate.diff(project.performancePeriodFrom, ["months"]).months;
  if (months < 0) {
    console.warn(
      "Warning; attempting to compute project period for a period that hasn't started yet."
    );
    return "baseline";
  }
  if (months < 6) {
    return "6";
  } else if (months < 12) {
    return "12";
  } else if (months < 18) {
    return "18";
  } else if (months < 24) {
    return "24";
  } else if (months < 30) {
    return "30";
  } else if (months < 36) {
    return "36";
  } else {
    return "total";
  }
}

/** Converts "6" to 6, "baseline" to 0, and "total" to 36. */
export function payoutIntervalAsNumber(period: PayoutInterval): number {
  return period === "baseline" ? 0 : period === "total" ? 36 : Number(period);
}

/**
 * Finds the time bin (if any) which contains the date imputed by the project and the period.
 * E.g. period "12" of a project that starts 1-1-2025 will return the bin containing 1-1-2026, if it exists.
 */
export function payoutIntervalToTimeBin(props: {
  timeBins: TimeBin[];
  period: PayoutInterval;
  project: ProjectType;
}): TimeBin | undefined {
  const { timeBins, period, project } = props;
  const queryDate = project.performancePeriodFrom.plus({ months: payoutIntervalAsNumber(period) });
  return timeBins.find((t) => t.startDate <= queryDate && t.endDate >= queryDate);
}

/**
 * Stores payout target and actual, plus a ton of intermediate calculations used in
 * the Payout Dashboard to explain the math to the user.
 */
export type PayoutStatistics = PayoutTarget & {
  /** Project for which the payout was computed. */
  project: ProjectType;

  /** The (computed) time bin used to compute "current" scores. */
  timeBin: TimeBin | undefined;

  /** National baseline for the project. */
  nationalBaseline: number | undefined;
  /** Project baseline for the project. */
  projectBaseline: number | undefined;

  /** Current national metric value, as computed by areaMetricAverage(). */
  nationalCurrent: number | undefined;
  /** Current project metric value, as computed by areaMetricAverage(). */
  projectCurrent: number | undefined;

  /** (nationalBaseline - nationalCurrent) / nationalBaseline */
  nationalRate: number | undefined;
  /** (projectBaseline - projectCurrent) / projectBaseline */
  projectRate: number | undefined;
  /** (projectRate - nationalRate) */
  did: number | undefined;

  /** How DID compares to the target reduction, e.g. `0.5` if did was 10 and target was 20. */
  payoutFraction: number | undefined;
  /** payoutFraction but confined to interval [0...1] */
  saturatedPayoutFraction: number | undefined;
  /** (saturatedPayoutFraction * max payout), but with a min of min payout.value. */
  estimatedPayout: number | undefined;
};

/**
 * Computes payout statistics given the current project and a specified date. NOTE: This is a Vue Composable.
 * Also returns all the intermediate steps in the computation so that they can be used to populate the wizard.
 *
 * FUTURE: Allow user to specify a past or future date.
 */
export function computePayoutStatistics(
  project: ProjectType | null | undefined,
  maybeTimeBin?: TimeBin
): PayoutStatistics | undefined {
  if (!project) {
    return undefined;
  }
  const dataStore = useDataStore();
  if (!dataStore.dataIsReady(project.outcomeKey)) {
    return undefined;
  }

  const period = projectPeriod(project, maybeTimeBin?.endDate);
  if (!period) {
    console.warn("Couldn't compute period for " + project.id);
    return undefined;
  }
  const targetPayout = dataStore.targetPayout(project.outcomeKey, period);
  if (!targetPayout) {
    console.error(`Couldn't find target payout for period ${period} outcome ${project.outcomeKey}`);
    return undefined;
  }
  const timeBin =
    maybeTimeBin ??
    payoutIntervalToTimeBin({
      project,
      period,
      timeBins: dataStore.timeBins({ metricKey: outcome2metric(project.outcomeKey) }),
    });
  if (!timeBin) {
    console.warn(
      `Couldn't find matching time bin for period ${period} which should start `,
      project.performancePeriodFrom
        .plus({ months: payoutIntervalAsNumber(period) })
        .toFormat("yyyy mm dd")
    );
  }
  const out: PayoutStatistics = {
    ...targetPayout,
    project,
    timeBin,
    nationalBaseline: undefined,
    nationalCurrent: undefined,
    nationalRate: undefined,
    projectBaseline: undefined,
    projectCurrent: undefined,
    projectRate: undefined,
    did: undefined,
    payoutFraction: undefined,
    saturatedPayoutFraction: undefined,
    estimatedPayout: undefined,
  };

  // FIXME: for 4.0 release, updating cardio target rate to divide by 100 to stay displaying 0.50% instead of 50% on UI
  // Need a better solution or update on the data end
  // TODO: rip out / 100 during ticket OUTCOME_TOOLKIT-591
  if (project.outcomeKey === "cardio") {
    out.targetRate = out.targetRate / 100;
  }

  const baseline = out.project.projectMeasurements["baseline"];
  if (!baseline) {
    console.error("When computing payout, could not find baseline measurements");
    return out;
  }

  out.nationalBaseline = baseline.nationalMetric;
  out.projectBaseline = baseline.projectMetric;

  const datumProps: DatumProps = {
    outcomeKey: out.project.outcomeKey,
    dataFilterKey: "t6mo",
    timeBin: out.timeBin,
  };

  out.nationalCurrent = dataStore.nationalAverage(datumProps)?.value ?? undefined;
  if (_.isNil(out.nationalCurrent)) {
    console.warn("When computing payout, could not compute national current.", datumProps);
  }

  out.projectCurrent =
    areaMetricAverage({
      ...datumProps,
      mids: new Set(out.project.areas),
    })?.value ?? undefined;

  if (_.isNil(out.projectCurrent)) {
    console.warn("When computing payout, could not compute current project value.");
  }

  if (!_.isNil(out.nationalCurrent) && !_.isNil(out.nationalBaseline)) {
    out.nationalRate = (out.nationalBaseline - out.nationalCurrent) / out.nationalBaseline;
  }
  if (!_.isNil(out.projectCurrent) && !_.isNil(out.projectBaseline)) {
    out.projectRate = (out.projectBaseline - out.projectCurrent) / out.projectBaseline;
  }
  // Difference in differences
  if (!_.isNil(out.projectRate) && !_.isNil(out.nationalRate)) {
    out.did = out.projectRate - out.nationalRate;
  }

  // NOTE: We also want to skip these computations if the denom is zero, so use simple `!!` truthiness
  if (!_.isNil(out.did) && !!out.targetRate) {
    out.payoutFraction = out.did / out.targetRate;
    out.saturatedPayoutFraction = Math.min(1, Math.max(0, out.payoutFraction));
    out.estimatedPayout = Math.max(
      out.minimumPayout,
      out.saturatedPayoutFraction * out.maximumPayout
    );
  }

  return out;
}
