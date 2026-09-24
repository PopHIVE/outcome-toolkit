<script lang="ts" setup>
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import _ from "lodash";
import { computed, onMounted, onUnmounted, ref } from "vue";

import MetricBinRow from "@/components/common/MetricBinRow.vue";
import SimpleTooltip from "@/components/common/SimpleTooltip.vue";
import ValueBox from "@/components/common/ValueBox.vue";
import { makeCustomControl } from "@/components/map/customControl";
import { useDataStore, type DatumProps } from "@/stores/data";
import { useNavigationStore } from "@/stores/nav";
import { useProjectStore } from "@/stores/project";
import { useSelectionStore } from "@/stores/selection";
import { LOADING_STRING } from "@/util/Consts";
import { compactNumber } from "@/util/formatters";
import { key2outcome } from "@/util/metricUtils";

const props = defineProps<{
  position?: L.ControlPosition;
  map: L.Map;
}>();

let loadingTimer: ReturnType<typeof setTimeout>;

let mapTooltip: L.Control;
const areaTooltipRef = ref<undefined | HTMLElement>();

const dataStore = useDataStore();
const navStore = useNavigationStore();
const projectStore = useProjectStore();
const selStore = useSelectionStore();

const outcomeKey = computed(() => {
  return projectStore.project()?.outcomeKey ?? navStore.outcome().key;
});

const outcome = computed(() => key2outcome(outcomeKey.value));

const datumProps = computed<DatumProps>(() => ({
  dataFilterKey: navStore.dataFilter().key,
  outcomeKey: outcome.value.key,
  timeBin: selStore.currentTimeBin,
}));

const metricData = computed(() =>
  dataStore.overviewDatum({
    ...datumProps.value,
    mid: selStore.hoverMID,
  })
);

// TODO: Display this information somewhere
const dataDetails = computed(() => {
  return dataStore.dataDetails(outcomeKey.value);
});

onMounted(() => {
  setupComponent();
});

onUnmounted(() => {
  clearTimeout(loadingTimer);
});

function setupComponent() {
  if (!props.map || !areaTooltipRef.value) {
    loadingTimer = setTimeout(setupComponent, 250);
    return;
  }
  clearTimeout(loadingTimer);
  mapTooltip = makeCustomControl(areaTooltipRef.value, {
    position: props.position,
  });
  mapTooltip.addTo(props.map);
}
</script>

<template>
  <div class="area-tooltip controls" ref="areaTooltipRef">
    <h4 v-if="!dataStore.dataIsReady()" class="header whole-tooltip">{{ LOADING_STRING }}</h4>
    <h4 v-else-if="!selStore.hoverMID" class="header whole-tooltip">
      Hover over an area for details
    </h4>
    <template v-else>
      <h4 class="text-center">
        {{
          dataStore.areaName(selStore.hoverMID) +
          (outcome.spatialGranularity === "ZCTA3" ? "xx" : "")
        }}
        <SimpleTooltip
          hasInfoIcon
          :text="navStore.granularityData().definition"
          data-position="bottom-left"
          minWidth="30em">
          <i class="bi-question-circle-fill"></i>
        </SimpleTooltip>
      </h4>

      <div class="pop-label">Total population</div>
      <ValueBox
        class="pop-value"
        :metricValue="dataStore.population(selStore.hoverMID)"
        :value-formatter="compactNumber"
        popoverPrefix="USA 2020 Census population:"
        :key="dataStore.population(selStore.hoverMID)" />

      <hr class="hr1" />

      <div
        v-if="
          !metricData ||
          _.isNil(navStore.metric().hasMetricValues ? metricData?.value : metricData?.bin_rank) ||
          !selStore.currentTimeBin
        "
        class="actual-warning">
        No data available.
      </div>
      <template v-else>
        <template v-if="navStore.metric().hasMetricValues">
          <div class="actual-label">{{ navStore.metric().label }}</div>
          <ValueBox
            class="actual-value"
            :metric-value="metricData.value"
            :value-formatter="outcome.metric.valueFormatter" />
        </template>
        <template v-else>
          <div class="actual-warning">Precise data is unavailable. Value is in range below.</div>
        </template>
        <MetricBinRow
          class="bin-row"
          :binRank="metricData?.bin_rank"
          :datum-props="datumProps"
          :showFullText="navStore.metric().hasMetricValues" />
      </template>

      <hr class="hr2" />

      <div class="data-source">
        Data from {{ selStore.currentTimeBin?.asString }}. Data source:
        {{ navStore.metric().dataSource }}
        <SimpleTooltip
          hasInfoIcon
          :text="navStore.metric().dataUsage"
          data-position="bottom-left"
          minWidth="35em"
          :key="navStore.metric().dataUsage">
          <i class="bi-question-circle-fill"></i>
        </SimpleTooltip>
      </div>
    </template>
  </div>
</template>

<style scoped>
.area-tooltip {
  display: grid;

  align-items: center;
  grid-auto-rows: auto;
  grid-template-areas:
    "header header"
    "pop-label pop-value"
    "covered-label covered-value"
    "hr1 hr1"
    "actual-label actual-value"
    "avg-label avg-value"
    "bin-row bin-row"
    "hr2 hr2"
    "data-source data-source";
  grid-template-columns: minmax(auto, 24em) 1fr;

  background: white;
  border-radius: 2px;
  border: 1px solid black;
  cursor: default;
  font-family: var(--bs-body-font-family);
  /* Un-override Leaflet's font choice. */
  gap: 0em 1em;
  padding: 0.5em 1em;
}

hr {
  margin: 0.25em 0;
}

.whole-tooltip {
  grid-area: header;
  grid-row-end: -1;
  margin: 0;
  text-align: center;
}

.header {
  grid-area: header;
  text-align: center;
  padding: 0.2em;
  font-size: 1.25rem;
}

.pop-label {
  grid-area: pop-label;
}

.pop-value {
  grid-area: pop-value;
}

.pop-label,
.actual-label,
.actual-warning {
  font-size: 0.95rem;
}

.covered-label {
  grid-area: covered-label;
}

.covered-value {
  grid-area: covered-value;
}

.actual-warning {
  grid-area: actual-label;
  grid-column: span 2;
  text-align: center;
}

.actual-label {
  grid-area: actual-label;
  padding-bottom: 0.5em;
}

.actual-value {
  grid-area: actual-value;
}

.avg-label {
  grid-area: avg-label;
}

.avg-value {
  grid-area: avg-value;
}

.hr1 {
  grid-area: hr1;
}

.hr2 {
  grid-area: hr2;
}

.bin-row {
  grid-area: bin-row;
  /* Because MetricBinRow uses subgrid, need to give it its own outer grid here.*/
  grid-template-columns: auto auto auto auto;
}

.data-source {
  grid-area: data-source;
  justify-self: center;

  display: flex;
  align-items: center;
  color: var(--brand-cool-gray-80);
  font-style: italic;
  gap: 0.5em;
  text-align: center;
}
</style>
