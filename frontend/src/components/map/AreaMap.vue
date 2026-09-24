<script lang="ts" setup>
import LoadingWidget from "@/components/common/LoadingWidget.vue";
import AreaTooltip from "@/components/map/AreaTooltip.vue";
import MapLegend from "@/components/map/MapLegend.vue";
import MapScroll from "@/components/map/MapScroll.vue";
import { useDataStore } from "@/stores/data";
import { useGeometryStore } from "@/stores/geometry";
import { useProjectStore } from "@/stores/project";
import { useSelectionStore } from "@/stores/selection";
import type { ColorRamp, OutcomeKeyType } from "@/types";
import { type AreaShapeProps } from "@/types";
import { LOCAL_STORAGE_MAP_CENTER, LOCAL_STORAGE_MAP_ZOOM } from "@/util/Consts";
import { getMID, stateStyle } from "@/util/mapUtils";
import { key2outcome } from "@/util/metricUtils";
import { useLocalStorage } from "@vueuse/core";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import _ from "lodash";
import { onMounted, onUnmounted, ref, shallowRef, watch } from "vue";

const props = defineProps<{
  colorRamp: ColorRamp;
  geoStyler: L.StyleFunction<AreaShapeProps>;
  hideLegend?: boolean;
  hideSelections?: boolean;
  hideTooltip?: boolean;
  outcomeKey: OutcomeKeyType;
}>();
const dataStore = useDataStore();
const geoStore = useGeometryStore();
const projStore = useProjectStore();
const selStore = useSelectionStore();

const lmapRef = ref<undefined | HTMLElement>();
const showMap = ref(false);

// Timers for our custom popup appear/dismiss life cycle and the loading cycle
let hoverTimer: ReturnType<typeof setTimeout>;
let loadingTimer: ReturnType<typeof setTimeout>;

// TODO: Leaflet doesn't show SVGs on every repeat of the globe, so quantize center to [-180, 180]. Ticket OUTCOME_TOOLKIT-498
const storedCenter = useLocalStorage<L.PointTuple>(LOCAL_STORAGE_MAP_CENTER, [39.5, -95]);
const storedZoom = useLocalStorage(LOCAL_STORAGE_MAP_ZOOM, 3.5);
const center = shallowRef(storedCenter.value);
const zoom = shallowRef(storedZoom.value);

const url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";

let map: L.Map | undefined;
let areasGeoJSON: L.Layer | undefined;

// Debounce the saving of these variables to local storage to avoid rubber-banding (especially on Chrome)
const saveCoords = _.debounce(
  ([c, z]: [L.PointTuple, number]) => {
    storedCenter.value = c;
    storedZoom.value = z;
  },
  500,
  { leading: false }
);

function click(e: L.LeafletEvent) {
  const feature: GeoJSON.Feature<GeoJSON.Geometry, AreaShapeProps> = e.propagatedFrom.feature;
  selStore.toggleSelection(getMID(feature));
}

// Show popup after mouseover, but schedule it to make sure we're not going to trigger during another popup event
function mouseoverArea(e: L.LeafletEvent) {
  const feature: GeoJSON.Feature<GeoJSON.Geometry, AreaShapeProps> = e.propagatedFrom.feature;
  const mid = getMID(feature);
  clearTimeout(hoverTimer);
  hoverTimer = setTimeout(() => {
    selStore.hoverMID = mid;
  }, 200);
}

// Delay popup dismissal, but first make sure we're not going to trigger during another popup event
function mouseout() {
  clearTimeout(hoverTimer);
  hoverTimer = setTimeout(() => {
    selStore.hoverMID = undefined;
  }, 1000);
}

// Keep tooltip open if the user mouses over it before it hides.
function mouseoverTooltip() {
  clearTimeout(hoverTimer);
}

/// COMPONENT LIFECYCLE METHODS ///

// Use a watch as we want to debounce this save (see above)
watch([center, zoom], saveCoords);
// Set up the map programmatically after the component is mounted, and when center or zoom change.
watch(props, setupMap, { immediate: true });
watch(() => projStore._currentProject, setupMap);

onUnmounted(() => {
  clearTimeout(hoverTimer);
  clearTimeout(loadingTimer);
  saveCoords.cancel();
});

defineExpose({
  // Allow parent components to resize the map when containers change
  resizeMap() {
    map?.invalidateSize();
  },
});

// Declaratively add layers as Leaflet doesn't play well with Vue reactivity and layers end up out of order.
function setupMap() {
  clearTimeout(loadingTimer); // In case we got called by a watch during a timeout.

  // Repeatedly wait until area is defined
  if (!lmapRef.value || !dataStore.dataIsReady(props.outcomeKey)) {
    loadingTimer = setTimeout(setupMap, 250);
    return;
  }

  // Reuse old map, base tiles, and state borders if possible.
  if (!map) {
    map = new L.Map(lmapRef.value, { zoom: zoom.value, center: center.value });

    // Base tiles
    const base = L.tileLayer(url, {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);
    const container = base.getContainer();
    if (container) {
      container.classList.add("map-gray");
    } else {
      loadingTimer = setTimeout(setupMap, 250);
      return; // Map didn't finish rendering; try again in a few ms
    }

    // GeoJSON resides on overlay at zIndex 400. Create a pane above that for the state borders.
    map.createPane("borders").style.zIndex = "402";
    const stateGeoJson = L.geoJSON(geoStore.STATE, {
      style: stateStyle(),
      pane: "borders",
    });
    stateGeoJson.addTo(map);
  }

  const shapes = geoStore[key2outcome(props.outcomeKey).spatialGranularity];
  if (!shapes?.features.length) {
    // Data is 'here' but it's not parsed/validated yet
    loadingTimer = setTimeout(setupMap, 250);
    return;
  }

  // Regenerate the layer that has the data in it.
  if (areasGeoJSON) {
    areasGeoJSON.remove();
  }
  areasGeoJSON = L.geoJSON(shapes, {
    style: props.geoStyler,
  });

  // Handlers
  areasGeoJSON.on("click", click);
  areasGeoJSON.on("mouseover", mouseoverArea);
  areasGeoJSON.on("mouseout", mouseout);

  areasGeoJSON.addTo(map);

  showMap.value = true;
}
</script>

<template>
  <div class="area-map">
    <div class="lmap" ref="lmapRef">
      <LoadingWidget v-if="!showMap || !map" label="Loading map data..." />

      <template v-else>
        <MapLegend
          v-if="!props.hideLegend"
          :color-ramp="colorRamp"
          :map="map"
          position="bottomright" />
        <MapScroll position="bottomleft" :map="map" />
        <AreaTooltip
          v-if="!props.hideTooltip"
          @mouseout="mouseout"
          @mouseover="mouseoverTooltip"
          :map="map"
          position="topright" />
      </template>
    </div>
  </div>
</template>

<style scoped>
.lmap {
  min-height: 30rem;
  height: 100%;
}

.loading-control {
  background: white;
  padding: 1em 2em;
  display: flex;
  align-items: center;
  border: 1px solid black;
  gap: 1em;

  h3 {
    margin: 0;
    color: var(--brand-violet);
  }
}
</style>
