import type { AreaFeatureCollection } from "@/types";
import { defineStore } from "pinia";
import type { SpatialGranularity } from "@/stores/SPATIAL_GRANULARITY_DATA";

export type GeometryStoreType = Record<SpatialGranularity, AreaFeatureCollection | undefined>;
/**
 * The geometry store stores a local copy of the shape geometries, which are expensive to re-fetch.
 */
export const useGeometryStore = defineStore("outcome-toolkit-geo", {
  state: () =>
    ({
      COUNTY: undefined,
      STATE: undefined,
      ZCTA3: undefined,
    }) as GeometryStoreType,
});
