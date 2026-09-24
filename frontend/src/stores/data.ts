import type { SpatialGranularity } from "@/stores/SPATIAL_GRANULARITY_DATA";
import { useNavigationStore } from "@/stores/nav";
import {
  DATA_FILTERS,
  OUTCOME_KEYS,
  PAYOUT_INTERVALS,
  type APIV2BinsType,
  type APIV2DataDetails,
  type APIV2Details,
  type AreaDemographicsType,
  type AreaListState,
  type DataFilterKeyType,
  type MID,
  type MetricBin,
  type MetricData,
  type MetricKeyType,
  type OutcomeKeyType,
  type PayoutInterval,
  type PayoutTarget,
  type TargetPayoutsType,
  type TimeBin,
} from "@/types";
import { COUNTRY_USA, LOADING_STRING, EMPTY_DATA_DETAILS } from "@/util/Consts";
import { key2outcome, outcome2metric } from "@/util/metricUtils";
import _ from "lodash";
import { Interval } from "luxon";
import { defineStore } from "pinia";

export type DatumProps = {
  dataFilterKey: DataFilterKeyType;
  outcomeKey: OutcomeKeyType;
  timeBin: TimeBin | undefined;
};

/** Make the complex payout data structure so we can import on top of it. */
export function makeEmptyPayouts(): TargetPayoutsType {
  // Start with permissive type as we're going to add the keys manually.
  const out: { [p: string]: { [o: string]: PayoutTarget } } = {};

  OUTCOME_KEYS.forEach((outcomeKey: OutcomeKeyType) => {
    out[outcomeKey] = {};
    PAYOUT_INTERVALS.forEach((period) => {
      out[outcomeKey][period] = {
        period,
        outcomeKey,
        minimumPayout: 0,
        maximumPayout: 0,
        targetRate: 0,
      };
    });
  });

  // Tighten type constraints here.
  return out as TargetPayoutsType;
}

/** The data as exposed to the GUI. */
export type DataStoreType = {
  /**
   * Metric bins for each outcome.
   * @private Do not access directly; use metricBins().
   */
  _metricBins: APIV2BinsType;

  /**
   * Internal store of annotated time bins, keyed by metric.
   * @private Do not access directly; use timeBins() and closestTimeBin().
   */
  _timeBins: Record<MetricKeyType, TimeBin[]>;

  /**
   * Stores fetched outcome data by outcome and time bin.
   * @private Do not access directly; use overviewData()
   */
  _overviewData: APIV2Details;

  /**
   * Stores data details
   * @private Do not access directly; use dataDetails()
   */
  _dataDetails: APIV2DataDetails;
  /**
   *
   */
  _dataIsReady: Record<OutcomeKeyType | "demographics", boolean>;

  /**
   * Display names for all the keyed props in the API.
   * e.g. `"acs.between_10k_15k"` keys to `"Households With Income - Between $10,000 - $15,000"`
   */
  displayNames: Record<string, string>;

  /**
   * For each demographic category (e.g. "age"), store metadata about that category.
   * Right now, there is only one key--`bands`, which enumerates the keys to use to reach into
   * the areaDemographics dictionary below, and their order.
   */
  demographicsCategories: Record<string, { bands: string[] }>;

  /**
   * Human-readable explanation of the sourcing behind all the demographic data.
   */
  demographicsSource: string;

  /**
   * Demographic data for each area
   */
  areaDemographics: Record<MID, AreaDemographicsType>;

  /**
   * State list sorted alphabetically by *state name*, for display ordering
   */
  areasByState: AreaListState[];

  dataProvenance: {
    dataProvider: string;
    dataRelease: string;
  };

  /**
   * Target payouts keyed by outcome, then by interval.
   */
  _targetPayouts: TargetPayoutsType;
};

export const useDataStore = defineStore("outcome-toolkit-data", {
  //defines default values
  state: () => {
    const state: DataStoreType = {
      areaDemographics: {},
      demographicsCategories: {},
      demographicsSource: LOADING_STRING,
      dataProvenance: {
        dataProvider: LOADING_STRING,
        dataRelease: LOADING_STRING,
      },
      areasByState: [],
      displayNames: {},
      _dataIsReady: {
        demographics: false,
        alcohol: false,
        cardio: false,
        opioid: false,
        soc: false,
      },
      _metricBins: {
        alcohol: {},
        cardio: {},
        opioid: {},
        soc: {},
      },
      _dataDetails: EMPTY_DATA_DETAILS,
      _overviewData: {},
      _timeBins: {},
      _targetPayouts: makeEmptyPayouts(),
    };
    return state;
  },
  actions: {
    /** Whether overview data has finished loading.
     * @param outcomeKey Whether outcome data of a particular outcome has loaded. Defaults to the currently selected outcome.
     */
    dataIsReady(outcomeKey?: OutcomeKeyType) {
      const navStore = useNavigationStore();
      return this._dataIsReady[outcomeKey ?? navStore.outcome().key];
    },
    setDataIsReady(outcomeKey: OutcomeKeyType, ready: boolean) {
      this._dataIsReady[outcomeKey] = ready;
    },
    dataDetails(outcomeKey: OutcomeKeyType) {
      return this._dataDetails[outcomeKey];
    },
    /**
     * getter function for the target payouts for given outcome
     * @param outcomeKey
     */
    targetPayouts(outcomeKey: OutcomeKeyType): Record<PayoutInterval, PayoutTarget> {
      return this._targetPayouts[outcomeKey];
    },
    targetPayout(outcomeKey: OutcomeKeyType, period: PayoutInterval): PayoutTarget | undefined {
      return this._targetPayouts?.[outcomeKey]?.[period];
    },

    /** Get the set of valid time bins for a given metric. By default returns a sorted list of
     * only the bins which represent a single month (i.e. not the 'overall' bin). */
    timeBins(props: { metricKey: MetricKeyType; includeWideBins?: boolean }): TimeBin[] {
      const bins = this._timeBins[props.metricKey] ?? [];
      if (props.includeWideBins) {
        return bins;
      } else {
        return bins
          .filter((t) => Interval.fromDateTimes(t.startDate, t.endDate).length("days") < 33)
          .toSorted((a, b) => a.startDate.toMillis() - b.startDate.toMillis());
      }
    },

    /** Get the metric value bins (i.e. an object representing the "0.01 to 0.05 ASCVD rate" bucket)
     *  for a given outcome, metric, and time bin.
     */
    metricBins(props: DatumProps): MetricBin[] {
      const { outcomeKey, timeBin } = props;

      const outcomeBin = this._metricBins[outcomeKey];
      // Bail gracefully if data hasn't loaded yet.
      if (!outcomeBin) {
        console.error("couldn't retrieve bin for outcome", outcomeKey, this.metricBins);
        return [];
      }
      if (_.size(outcomeBin) === 0 || !timeBin) {
        return [];
      }

      const metricKey = outcome2metric(outcomeKey);
      const metricBinsForOutcome = outcomeBin[metricKey];
      if (!metricBinsForOutcome) {
        console.error("couldn't retrieve bin for metric", metricKey);
        return [];
      }

      if (!(timeBin.raw in metricBinsForOutcome)) {
        console.error(
          "Couldn't retrieve metric bin",
          metricKey,
          " for time bin",
          timeBin.asString,
          metricBinsForOutcome
        );
        return [];
      }

      return metricBinsForOutcome[timeBin.raw];
    },

    /**
     * Get the MetricBin that a metric value falls within.
     */
    metricBin(
      props: DatumProps & { metricValue: number | undefined | null }
    ): MetricBin | undefined {
      const { metricValue, ...otherProps } = props;
      if (_.isNil(metricValue)) {
        return undefined;
      }
      return _.find(
        this.metricBins(otherProps),
        (bin) => bin.min <= metricValue && bin.max >= metricValue
      );
    },

    /**
     * Get the MetricBin for a given rank.
     */
    metricBinByRank(
      props: DatumProps & {
        metricRank: number | undefined | null;
      }
    ): MetricBin | undefined {
      const { metricRank, ...rest } = props;
      if (_.isNil(metricRank)) {
        return undefined;
      }
      return _.find(this.metricBins(rest), ({ rank }) => rank === metricRank);
    },

    /** Get the national average for the current or specified (outcome + data stream + time bin).
     * Defaults are the same as for overviewDatum.
     */
    nationalAverage(props: DatumProps): MetricData | undefined {
      return this.overviewDatum({ mid: COUNTRY_USA, ...props });
    },

    /** Convenience function to get population for a MID. Returns 0 if the MID or data was not found. */
    population(mid: MID): number {
      return Number(this.areaDemographics[mid]?.["census.total_population"] ?? 0);
    },

    /** Convenience function to get display name for a MID. Returns LOADING_STRING if the MID or metadata was not found. */
    areaName(mid: MID): string {
      return String(this.areaDemographics[mid]?.["census.name"] ?? LOADING_STRING);
    },

    /** A list of the MIDs that intersect this area of the given size. */
    areaIntersects(mid: MID, withSize: SpatialGranularity): MID[] {
      return this.areaDemographics?.[mid]?.intersections?.[withSize] ?? [];
    },

    /**
      @returns Returns granular name for any MID.
      (Ex. "COUNTY 01001" :	"Autauga County, AL (Pop: 58.80K)")
    */
    getGranularName(mid: MID) {
      const result: Record<MID, string> = {};

      this.areasByState.forEach(({ areas }) => {
        Object.assign(result, areas);
      });

      return result[mid];
    },

    /**
      @returns Dictionary of all Granular Names from every state
      (Ex. "COUNTY 01001" :	"Autauga County, AL (Pop: 58.80K)")
    */
    getAllGranularNames() {
      const result: Record<MID, string> = {};

      this.areasByState.forEach(({ areas }) => {
        Object.assign(result, areas);
      });
    },

    /** Returns true if two areas are considered adjacent according to the database. */
    areAdjacent(mid1: MID, mid2: MID): boolean {
      return this.areaDemographics[mid1]?.adjacency?.includes(mid2) ?? false;
    },

    /**
     * Get the `{ bin_rank, value }` object for the specified MID, the given or current outcome,
     * and the given or current time bin.
     * @return undefined if it's not found.
     */
    overviewDatum(props: DatumProps & { mid: MID | undefined | null }): MetricData | undefined {
      const { dataFilterKey, mid, outcomeKey, timeBin } = props;
      if (!mid || !timeBin) {
        return undefined;
      }

      return _getDatum({
        overviewData: this._overviewData,
        dataFilterKey,
        mid,
        outcomeKey,
        timeBin,
      });
    },

    /**
     * Pluck all the MetricData for specified (outcome + data stream + time bin).
     */
    overviewData(props: DatumProps): Record<MID, MetricData> {
      // TODO: add memoizing to overviewData in a sane way.
      const { dataFilterKey, outcomeKey, timeBin } = props;

      if (!timeBin) {
        return {};
      }
      const data: Record<MID, MetricData> = {};
      _.forEach(_.keys(this._overviewData), (mid) => {
        const datum = _getDatum({
          overviewData: this._overviewData,
          mid,
          dataFilterKey,
          outcomeKey,
          timeBin,
        });
        if (datum) {
          data[mid] = datum;
        }
      });

      return data;
    },
  },
});

/** Local function to do the complicated addressing into _overviewData quickly. Does not check for null/etc. */
function _getDatum(
  props: DatumProps & {
    overviewData: DataStoreType["_overviewData"];
    mid: MID;
    timeBin: TimeBin;
  }
): MetricData | undefined {
  const { dataFilterKey, outcomeKey, overviewData, mid, timeBin } = props;

  const apiMetricKey = DATA_FILTERS[dataFilterKey].apiMetricKey;
  const filteredMetricKey = key2outcome(outcomeKey).metric[apiMetricKey];

  return overviewData[mid]?.[filteredMetricKey]?.[timeBin.raw];
}
