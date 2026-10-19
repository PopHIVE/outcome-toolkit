import { type DemographicKeyType } from "@/stores/DEMOGRAPHIC_DATA";
import { useDataStore } from "@/stores/data";
import { useSelectionStore } from "@/stores/selection";
import { type MID } from "@/types";
import _ from "lodash";

export type DemographicStack = {
  [demographicValue: string]: { label: string; value: number; displayName: string };
};

/**
 * Sum over each area for the given demographic and outcome.
 * @returns an object keyed by demographic label, e.g. { "pop_0_4": 1234, "pop_5_9": 2345 }
 */

export function stackDemographics(demographicKey: DemographicKeyType): DemographicStack {
  const selStore = useSelectionStore();
  const demographicStack: DemographicStack = {};
  const dataStore = useDataStore();

  if (_.size(dataStore.areaDemographics) === 0) {
    return demographicStack;
  }
  selStore.midSelections.forEach((mid: MID) => {
    const areaData = dataStore.areaDemographics[mid];
    if (!areaData) {
      console.warn(`In stackDemographics, couldn't find area data for '${mid}'`);
    } else {
      // Handle mismatch between demographic key and api response key
      let categoryKey: string;
      demographicKey == "re" ? (categoryKey = "race/ethnicity") : (categoryKey = demographicKey);
      // Not every data source provides demographic breakdowns.
      if (!dataStore.demographicsCategories[categoryKey]) {
        return;
      }
      //for each band within a given category, create new demographics stack or add to existing value
      dataStore.demographicsCategories[categoryKey].bands.forEach((bandName) => {
        // displayName: lookup full name of the bandName in displayNames, format for table to just be range
        // value: accumulate values for selection under demographicStack[bandName].value, 0 if null
        demographicStack[bandName] = {
          displayName: dataStore.displayNames[bandName].substring(
            2 + dataStore.displayNames[bandName].indexOf("-")
          ),
          label: bandName,
          value: Number(areaData[bandName] ?? 0) + (demographicStack[bandName]?.value ?? 0),
        };
      }); //for each band in given demographicKey
    }
  }); //for each mid

  return demographicStack;
}
