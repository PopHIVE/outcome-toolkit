import { useDataStore } from "@/stores/data";
import { useNavigationStore } from "@/stores/nav";
import type { TimeBin, MetricKeyType, MID } from "@/types";
import { LOCAL_STORAGE_MID_SELECTIONS, MONTHS_OF_UNCERTAINTY } from "@/util/Consts";
import { areasAreContiguous, areasCoverState } from "@/util/mapUtils";
import { useLocalStorage } from "@vueuse/core";
import { defineStore } from "pinia";

export type SelectionStoreType = {
  /** Are the currently selected set of areas contiguous? @see featuresAreContiguous */
  contiguous: boolean | undefined;

  /** MID currently being inspected (by being hovered over on the map), or undefined if none. */
  hoverMID: MID | undefined;

  /** The MIDs that the user has selected on the map. */
  midSelections: Set<string>;

  /** Do currently selected set of areas span an entire state? Cached as it's expensive to compute. */
  coversState: boolean | undefined;

  /** What time bin the user is currently looking at. */
  currentTimeBin: TimeBin | undefined;

  /**
   * The time period the user is currently looking at. May not contain the currentTimeBin.
   * TODO: Investigate if we want to reselect/force the currentTimeBin to always be within the current focused period.
   */
  currentFocusedPeriod: string | undefined;
};

/**
 * The Selection store maintains state for the set of
 * areas the user has selected.
 */
export const useSelectionStore = defineStore("outcome-toolkit-selection", {
  state: () => {
    const midSelections = useLocalStorage<SelectionStoreType["midSelections"]>(
      LOCAL_STORAGE_MID_SELECTIONS,
      new Set<MID>()
    );
    const state: SelectionStoreType = {
      // TODO: How do we make these so they cannot be directly mutated?
      contiguous: undefined,
      coversState: undefined,
      hoverMID: undefined,
      midSelections: midSelections.value,
      currentTimeBin: undefined,
      currentFocusedPeriod: undefined,
    };
    return state;
  },

  actions: {
    /** Toggle a selection. Returns true if the area is now selected. */
    toggleSelection(mid: MID) {
      const has = this.midSelections.has(mid);
      if (has) {
        this.midSelections.delete(mid);
      } else {
        this.midSelections.add(mid);
      }
      this.recomputeSelection();
      return !has;
    },

    /** Set or unset selection of an array of areas, resulting in a unique set of selections. */
    setSelections(mids: string[], selection: boolean) {
      // HACK: Have to update members individually as Set.union / Set.difference don't work on proxies.
      if (selection) {
        for (const m of mids) {
          this.midSelections.add(m);
        }
      } else {
        for (const m of mids) {
          this.midSelections.delete(m);
        }
      }
      this.recomputeSelection();
    },

    /** Clear all selections */
    clearSelections() {
      this.midSelections.clear();
      this.recomputeSelection();
    },

    /** Update contiguity and whole-state checks */
    recomputeSelection() {
      const dataStore = useDataStore();
      const navStore = useNavigationStore();
      // Compute contiguity and whole-state coverage
      if (this.midSelections.size <= 1) {
        // Zero or one selection is always contiguous
        this.contiguous = true;
      } else {
        this.contiguous = areasAreContiguous(this.midSelections);

        this.coversState = areasCoverState(
          navStore.outcome().spatialGranularity,
          this.midSelections,
          dataStore.areasByState
        );
      }
    },

    /**
     * Set the current time bin to the specified bin, IF it is a valid bin for the
     * current outcome + metric. Otherwise, calls chooseBestTimeBin.
     */
    setCurrentTimeBin(bin: TimeBin) {
      const dataStore = useDataStore();
      const metricKey = useNavigationStore().metric().key;
      const timeBins = dataStore.timeBins({ metricKey });
      if (timeBins.find((b) => b.raw === bin.raw)) {
        this.currentTimeBin = bin;
      } else {
        console.warn(`couldn't find bin ${bin.raw} when selecting`);
        this.chooseBestTimeBin({ metricKey });
      }
    },

    /**
     * This selects the 'best' time bin to use given the current outcome and metric.
     * As of v3.2 it is locked to the time bin for January, 2024, per sponsor request.
     *
     * It gets called after the bins load, and whenever the user changes the outcome.
     */
    chooseBestTimeBin(props: { metricKey: MetricKeyType }) {
      const dataStore = useDataStore();
      const timeBins = dataStore.timeBins({ metricKey: props.metricKey });
      if (timeBins.length === 0) {
        console.warn("No bins found when choosing best time", props.metricKey, dataStore._timeBins);
        return;
      }
      // NOTE: As of May 2025, always select X month old data point.
      const inverseMonthsofUncertainty = MONTHS_OF_UNCERTAINTY * -1;
      // Clamp so sources with fewer months (e.g. a single snapshot) still get a bin.
      this.currentTimeBin = timeBins.at(Math.max(inverseMonthsofUncertainty, -timeBins.length));
    },
  },
});
