<script setup lang="ts">
import MetricBinRow from "@/components/common/MetricBinRow.vue";
import { makeCustomControl } from "@/components/map/customControl";
import { type DatumProps } from "@/stores/data";
import { useNavigationStore } from "@/stores/nav";
import { useSelectionStore } from "@/stores/selection";
import { MISSING_INDEX, SELECTED_INDEX } from "@/util/colorUtils";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { computed, onMounted, onUnmounted, ref } from "vue";

const props = defineProps<{
  position?: L.ControlPosition;
  map: L.Map;
}>();

let loadingTimer: ReturnType<typeof setTimeout>;

onUnmounted(() => {
  clearTimeout(loadingTimer);
});

const mapLegendRef = ref<undefined | HTMLElement>();
let mapLegend: L.Control;

const navStore = useNavigationStore();
const selStore = useSelectionStore();

const datumProps = computed<DatumProps>(() => ({
  dataFilterKey: navStore.dataFilter().key,
  outcomeKey: navStore.outcome().key,
  timeBin: selStore.currentTimeBin,
}));

const open = ref(true);

onMounted(() => {
  setupComponent();
});

function setupComponent() {
  if (!props.map || !mapLegendRef.value) {
    loadingTimer = setTimeout(setupComponent, 250);
    return;
  }
  mapLegend = makeCustomControl(mapLegendRef.value, {
    position: props.position,
  });
  mapLegend.addTo(props.map);
}
</script>

<template>
  <div
    class="map-legend leaflet-control"
    :class="`map-legend-${navStore.outcome().key}`"
    ref="mapLegendRef"
    position="bottomright">
    <button
      class="btn btn-sm btn-light legend-collapser"
      :class="{ open: open && !selStore.hoverMID }"
      @click="open = !open"
      :title="`${open ? 'Collapse' : 'Expand'} Map Legend`"
      :aria-label="`${open ? 'Collapse' : 'Expand'} Map Legend button`">
      <i
        class="bi"
        :class="{ [open ? 'bi-arrows-angle-contract' : 'bi-arrows-angle-expand']: true }" />
    </button>
    <template v-if="open && !selStore.hoverMID">
      <div class="legend-title">
        {{ navStore.metric().label }}
      </div>
      <div class="legend-bins">
        <MetricBinRow
          v-for="bin_rank in 10"
          :binRank="bin_rank - 1"
          :datumProps="datumProps"
          :key="bin_rank" />
        <MetricBinRow :binRank="MISSING_INDEX" :datum-props="datumProps" />
        <MetricBinRow :binRank="SELECTED_INDEX" :datum-props="datumProps" />
      </div>
      <div class="legend-time-data" v-if="selStore.currentTimeBin">
        Viewing {{ navStore.dataFilter().label }} ending
        {{ selStore.currentTimeBin.endDate.toFormat("MMM yyyy") }}
      </div>
    </template>
  </div>
</template>

<style scoped>
.map-legend {
  background: white;
  border-radius: 2px;
  border: 1px solid var(--brand-cool-gray-80);
  display: grid;
  font-family: var(--bs-body-font-family);
  gap: 2px;
  padding: 1em;
  position: relative;
  max-width: max-content;
}
.legend-title {
  max-width: 26em;
  text-align: left;
}
.legend-bins {
  display: grid;
  grid-template-columns: auto auto auto auto;
}

.legend-time-data {
  color: var(--brand-cool-gray-70);
  text-align: left;
}

.legend-collapser {
  /* font-size: 0.8rem; */
  margin: 0 !important;
  &.open {
    position: absolute;
    /* Manually position to take into account borders and padding, so button doesn't jump around when minimized. */
    right: calc(1em - 2px);
    bottom: calc(1em - 2px);
  }
}
</style>
