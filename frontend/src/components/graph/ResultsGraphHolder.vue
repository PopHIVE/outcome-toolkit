<script lang="ts" setup>
// import TimeBinPicker from "@/components/TimeBinPicker.vue";
import ListOfNames from "@/components/common/ListOfNames.vue";
import SimpleTooltip from "@/components/common/SimpleTooltip.vue";
import MetricHistoryGraph from "@/components/graph/MetricHistoryGraph.vue";
import { useDataStore } from "@/stores/data";
import { useNavigationStore } from "@/stores/nav";
import { useSelectionStore } from "@/stores/selection";
import { type MetricHistoryGraphSize } from "@/types";
import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  SubTitle,
  TimeScale,
  Title,
  Tooltip,
} from "chart.js";
import annotationPlugin from "chartjs-plugin-annotation";
import zoomPlugin from "chartjs-plugin-zoom";
import { computed } from "vue";

const model = defineModel<{ size: MetricHistoryGraphSize }>({ required: true });

const dataStore = useDataStore();
const navStore = useNavigationStore();
const selStore = useSelectionStore();

/* NOTE: ChartJS requires explicit registration of the elements you intend to use, or the page will not load. Wonderful DX. */
ChartJS.register(
  CategoryScale,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  SubTitle,
  TimeScale,
  Title,
  Tooltip,
  annotationPlugin,
  zoomPlugin
);

const mids = computed(() => selStore.midSelections);

const names = computed(() => [...mids.value].map((mid) => dataStore.areaName(mid)));

const instructions = computed(
  () =>
    `Each point shows ${navStore.dataFilter()?.label ?? "a moment in time"}. Click and drag to pan the graph. Use mousewheel or scroll gesture to zoom in.`
);

const timesAvailable = computed(
  () => dataStore.timeBins({ metricKey: navStore.metric().key }).length
);

const message = computed(() => {
  if (timesAvailable.value > 2) {
    if (selStore.midSelections.size === 0) {
      return "Select one or more areas to see data.";
    } else {
      return undefined;
    }
  } else {
    return "Insufficient data available for trend analysis for this outcome.";
  }
});
</script>

<template>
  <section class="srv-graph-holder" :class="model.size">
    <header class="trended-data-header">
      <span>Historical Data</span>
      <SimpleTooltip
        hasInfoIcon
        class="flex-grow-1 justify-left"
        :text="instructions"
        :data-position="model.size === 'collapsed' || message ? 'right' : 'bottom'"
        minWidth="12em">
        <i class="bi-question-circle-fill"></i>
      </SimpleTooltip>
      <button
        v-show="timesAvailable > 2"
        class="btn btn-sm btn-text collapse-model"
        :name="model.size === 'collapsed' ? 'Expand history graph' : 'Collapse history graph'"
        title="Collapse history graph"
        @click="model.size = model.size === 'collapsed' ? 'normal' : 'collapsed'">
        <i
          class="bi"
          :class="{
            [model.size === 'collapsed' ? 'bi-chevron-double-down' : 'bi-chevron-double-up']: true,
          }"></i>
      </button>
      <button
        v-show="timesAvailable > 2"
        class="btn btn-sm btn-text expand-model"
        name="Maximize history graph"
        title="Maximize history graph"
        @click="model.size = model.size === 'expanded' ? 'normal' : 'expanded'">
        <i
          class="bi"
          :class="{
            [model.size === 'expanded' ? 'bi-arrows-angle-contract' : 'bi-arrows-angle-expand']:
              true,
          }" />
      </button>
    </header>
    <main>
      <template v-if="model.size !== 'collapsed'">
        <div v-if="model.size === 'expanded'" class="d-flex gap-1 p-2 text-align-center">
          Selected areas: <ListOfNames :names="names" />
        </div>

        <MetricHistoryGraph :class="model.size" :mids="mids" />
      </template>
    </main>
  </section>
</template>

<style scoped>
.srv-graph-holder {
  border: 1px solid var(--brand-cool-gray-20);
  display: grid;
  grid-template-rows: auto 1fr;
}
.trended-data-header {
  font-family: "Poppins", sans-serif;
  align-content: center;
  align-items: center;
  align-self: stretch;
  background: var(--brand-cool-gray-5);
  display: flex;
  flex: row nowrap;
  gap: 0.5rem;
  margin: 0;
  padding: 0.25rem 0.5rem;
}
.graph-controls {
  margin: 1rem;
}
</style>
