import { useSelectionStore } from "@/stores/selection";
import { useLocalStorage } from "@vueuse/core";
import { defineStore } from "pinia";

import { SPATIAL_GRANULARITY_DATA } from "@/stores/SPATIAL_GRANULARITY_DATA";
import {
  isDataFilterKeyType,
  isOutcomeKeyType,
  isRoleKeyType,
  key2dataFilter,
  type DataFilterKeyType,
  type OutcomeKeyType,
  type RoleKeyType,
} from "@/types";
import {
  LOCAL_STORAGE_SELECTED_DATA_STREAM,
  LOCAL_STORAGE_SELECTED_OUTCOME,
  LOCAL_STORAGE_SELECTED_ROLE,
} from "@/util/Consts";
import { key2outcome } from "@/util/metricUtils";

export type NavStoreType = {
  /** The outcome the user has selected to investigate. */
  _outcomeKey: OutcomeKeyType;
  /** The role played by the current user. */
  _roleKey: RoleKeyType | undefined;
  /** Which data filter the user is looking at. */
  _dataFilterKey: DataFilterKeyType;
};

export const useNavigationStore = defineStore("outcome-toolkit-nav", {
  state: () => {
    const _outcomeKey = useLocalStorage<NavStoreType["_outcomeKey"]>(
      LOCAL_STORAGE_SELECTED_OUTCOME,
      "soc"
    );
    const _roleKey = useLocalStorage<NavStoreType["_roleKey"]>(
      LOCAL_STORAGE_SELECTED_ROLE,
      "public"
    );

    const _dataFilterKey = useLocalStorage<NavStoreType["_dataFilterKey"]>(
      LOCAL_STORAGE_SELECTED_DATA_STREAM,
      "t6mo"
    );

    // Check that local storage has valid values, and if not, revert to valid.
    if (!isOutcomeKeyType(_outcomeKey.value)) {
      _outcomeKey.value = "soc";
    }
    if (!isRoleKeyType(_roleKey.value)) {
      _roleKey.value = "public";
    }
    if (!isDataFilterKeyType(_dataFilterKey.value)) {
      _dataFilterKey.value = "t6mo";
    }

    return { _dataFilterKey, _outcomeKey, _roleKey };
  },
  actions: {
    granularityData() {
      return SPATIAL_GRANULARITY_DATA[key2outcome(this._outcomeKey).spatialGranularity];
    },
    outcome() {
      return key2outcome(this._outcomeKey);
    },
    metric() {
      return key2outcome(this._outcomeKey).metric;
    },
    dataFilter() {
      return key2dataFilter(this._dataFilterKey);
    },

    /** Set whether the user is using raw or t6mo data. */
    setDataFilter(s: DataFilterKeyType) {
      this._dataFilterKey = s;
    },

    /**
     * Select the given outcome.
     *
     * **Side effects**: This also resets selections and chooses an appropriate time bin.
     */
    setOutcome(outcomeKey: OutcomeKeyType) {
      const selStore = useSelectionStore();
      this._outcomeKey = outcomeKey;
      selStore.clearSelections();
      selStore.chooseBestTimeBin({ metricKey: this.outcome().metric.key });
    },
  },
});
