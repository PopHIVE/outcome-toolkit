import { useDataStore, type DataStoreType } from "@/stores/data";
import { type SelectionStoreType } from "@/stores/selection";
import { isSpatialGranularity, type SpatialGranularity } from "@/stores/SPATIAL_GRANULARITY_DATA";
import { type AreaShapeProps, type ColorRamp, type MetricData, type MID } from "@/types";
import {
  MISSING_COLOR,
  PROJECT_IGNORED_COLOR,
  SELECTED_COLOR,
  SELECTED_COLOR_FILL,
} from "@/util/colorUtils";
import { LOADING_STRING } from "@/util/Consts";
import _ from "lodash";

/** Type-safe way to determine if a MID is for the specific granularity.
 * Example:
 * ```
 *   isOfGranularity("COUNTY 01", "COUNTY"); // true
 *   isOfGranularity("COUNTY 01", "STATE"); // false
 */
export function isOfGranularity(mid: MID, key: SpatialGranularity) {
  return mid.startsWith(key);
}

/** Type-safe way to determine the granularity (e.g. "COUNTY") of a MID. */
export function midGranularity(mid: MID | null | undefined): SpatialGranularity | undefined {
  const g = mid?.split(" ")?.[0];
  return isSpatialGranularity(g) ? g : undefined;
}

/** Pluck the MID out of GeoJSON feature. */
export function getMID(f: GeoJSON.Feature<GeoJSON.Geometry, AreaShapeProps>): string {
  return f.properties.mid ?? LOADING_STRING;
}

/**
 * This function checks if the set of features is contiguous by
 * checking if each of its members intersect.
 */
export function areasAreContiguous(selections: Set<MID>) {
  const dataStore = useDataStore();
  if (selections.size === 0) {
    return undefined;
  } else if (selections.size === 1) {
    return true;
  }

  // Make our working sets
  const [first, ...rest] = [...selections];
  const searched = new Set([first]);
  const unsearched = new Set(rest);

  while (unsearched.size > 0) {
    const pre_size = searched.size;

    for (const mid1 of unsearched) {
      for (const mid2 of searched) {
        if (dataStore.areAdjacent(mid1, mid2)) {
          searched.add(mid1);
          unsearched.delete(mid1);
        }
      }
    }

    // Full Round of no additions
    if (pre_size === searched.size) {
      break;
    }
  }

  return searched.size >= _.size(selections);
}
/**
 * This function checks if the set of features covers at least one
 * entire state.
 */
export function areasCoverState(
  spatialGranularity: SpatialGranularity,
  mids: SelectionStoreType["midSelections"],
  areaList: DataStoreType["areasByState"]
): boolean {
  // Have to check each state that the selection touches
  const statesInSelection = areaList
    .filter((a) => isOfGranularity(a.mid, "STATE"))
    .filter((a) => {
      for (const mid of mids) {
        if (mid in a.areas) {
          // Return early as we only need one mid to match.
          return true;
        }
      }
      return false;
    });

  for (const state of statesInSelection) {
    // If every area in this state is also in the selection, we're good.
    if (
      Object.keys(state.areas)
        .filter((mid) => isOfGranularity(mid, spatialGranularity))
        .every((mid) => mids.has(mid))
    ) {
      // Return early as we only need one state to match.
      return true;
    }
  }

  return false;
}

export const areaStyleBase: L.PathOptions = {
  // stroke
  color: "transparent",
  weight: 3,

  // fill
  opacity: 1, // Override Leaflet default as we set opacity in the color itself.
  fillColor: "#001B5E40",
  fillOpacity: 1, // Override Leaflet default as we set opacity in the color itself.
};

export const areaStyleSelected: L.PathOptions = {
  ...areaStyleBase,
  color: SELECTED_COLOR,
  fillColor: SELECTED_COLOR + "80",
};

export const areaStyleMissing: L.PathOptions = {
  ...areaStyleBase,
  color: MISSING_COLOR,
  fillColor: MISSING_COLOR,
};

/** Show states as noninteractable outlines. */
export const stateStyle: L.StyleFunction = () => ({
  // stroke
  color: "var(--brand-cool-gray-60)",
  weight: 2,

  // fill
  fill: false,

  // don't allow selection of states
  interactive: false,
});

export type GeoStylerMaker = (
  data: Record<MID, MetricData> | undefined,
  midSelections: Set<MID>,
  colorRamp: ColorRamp
) => L.StyleFunction<AreaShapeProps>;

/**
 * Makes a new GeoStyler function for the Search Results page when the data changes.
 * The thunk construction allows it to be reactive to changes in time bin and/or outcome.
 */
export const geoStylerMaker: GeoStylerMaker = (data, midSelections, colorRamp) => (feature) => {
  const mid = feature?.properties?.mid;
  if (_.isNil(mid) || _.isNil(data)) {
    // We haven't loaded yet
    return areaStyleBase;
  } else if (!(mid in data) && !midSelections.has(mid)) {
    // Provider didn't give us any data for this point and its not selected
    return areaStyleMissing;
  }

  if (midSelections.has(mid)) {
    return {
      ...areaStyleBase,
      color: SELECTED_COLOR,
      fillColor: SELECTED_COLOR_FILL,
    };
  } else {
    const { bin_rank } = data[mid];

    if (!_.isNil(bin_rank) && !(bin_rank in colorRamp)) {
      console.error(`Couldn't find value ${bin_rank} in color ramp`, colorRamp);
      return areaStyleBase;
    }
    const c = colorRamp[bin_rank ?? -1];
    return {
      ...areaStyleBase,
      color: c,
      fillColor: c,
    };
  }
};
export const areaStyleIgnored: L.PathOptions = {
  ...areaStyleBase,
  color: PROJECT_IGNORED_COLOR,
  fillColor: PROJECT_IGNORED_COLOR,
};
