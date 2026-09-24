<script setup lang="ts">
import { useDataStore } from "@/stores/data";
import { key2outcome } from "@/util/metricUtils";

import { useProjectStore } from "@/stores/project";
import { useSelectionStore } from "@/stores/selection";
import { DATA_FILTERS } from "@/types";
import _ from "lodash";
import { computed } from "vue";

const dataStore = useDataStore();
const projectStore = useProjectStore();
const project = computed(() => projectStore.project());
const selStore = useSelectionStore();

// Set-ify it for speed of access later.
const projectMIDs = computed(() => new Set(project.value?.areas));

const hoverText = computed(() => {
  const p = project.value; // So we can close over p in the map below.
  if (!p) {
    return undefined;
  }
  const formatter = key2outcome(project.value.outcomeKey).metric.valueFormatter;
  const timeBin = selStore.currentTimeBin;

  return _.mapValues(DATA_FILTERS, (f) => {
    const d = timeBin
      ? dataStore.overviewDatum({
          dataFilterKey: f.key,
          mid: selStore.hoverMID,
          outcomeKey: p.outcomeKey,
          timeBin,
        })?.value
      : undefined;

    if (_.isNil(d)) {
      return "no data";
    } else {
      return formatter(d);
    }
  });
});
</script>

<template>
  <div class="project-map-tooltip">
    <div v-if="project && selStore.hoverMID && projectMIDs.has(selStore.hoverMID)">
      <h6>{{ dataStore.getGranularName(selStore.hoverMID) }}</h6>
      <div>{{ key2outcome(project.outcomeKey).metric.shortLabel }}:</div>
      <ul>
        <li v-for="f in DATA_FILTERS" :key="f.key">
          {{ f.label }}: {{ hoverText?.[f.key] ?? f.description }}
        </li>
      </ul>
    </div>
    <div v-else>Hover over a project geography to get details.</div>
  </div>
</template>
<style scoped>
.project-map-tooltip {
  background-color: var(--brand-cool-gray-5);
  padding: 0.5rem;
  h6 {
    background-color: var(--brand-cool-gray-10);
    text-align: center;
  }
}
</style>
