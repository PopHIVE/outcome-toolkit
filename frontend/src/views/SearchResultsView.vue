<script setup lang="ts">
import ContiguousGauge from "@/components/ContiguousGauge.vue";
import DemographicDistribution from "@/components/DemographicDistribution.vue";
import MetricGauge from "@/components/MetricGauge.vue";
import AreaList from "@/components/areaSelector/AreaList.vue";
import DataFilterPicker from "@/components/common/DataFilterPicker.vue";
import OutcomeButtons from "@/components/common/OutcomeButtons.vue";
import ResultsGraphHolder from "@/components/graph/ResultsGraphHolder.vue";
import AreaMap from "@/components/map/AreaMap.vue";

import { useDataStore } from "@/stores/data";
import { useNavigationStore } from "@/stores/nav";
import { useSelectionStore } from "@/stores/selection";
import { type MetricHistoryGraphSize } from "@/types";
import {
  LOCAL_STORAGE_METRIC_HISTORY_GRAPH_SIZE,
  LOCAL_STORAGE_OUTCOME_SHOWN,
} from "@/util/Consts";
import { cyanToPink10 } from "@/util/colorUtils";
import { createCSV } from "@/util/downloadCSV";
import { downloadPDF } from "@/util/downloadPDF";
import { compactNumber } from "@/util/formatters";
import { areaMetricAverage } from "@/util/metricUtils";
import { useLocalStorage } from "@vueuse/core";
import _ from "lodash";
import { computed, ref } from "vue";
import { areaStyleBase, geoStylerMaker } from "@/util/mapUtils";

const dataStore = useDataStore();
const navStore = useNavigationStore();
const selStore = useSelectionStore();

const outcomeShown = useLocalStorage(LOCAL_STORAGE_OUTCOME_SHOWN, true);

const graphModel = useLocalStorage<{ size: MetricHistoryGraphSize }>(
  LOCAL_STORAGE_METRIC_HISTORY_GRAPH_SIZE,
  { size: "normal" }
);

const dataFilterKey = computed(() => navStore.dataFilter().key);
if (dataFilterKey.value === "did") {
  // If the user came from a project, DiD doesn't make sense.
  navStore.setDataFilter("t6mo");
}
const outcome = computed(() => navStore.outcome());
const timeBin = computed(() => selStore.currentTimeBin);
if (!selStore.currentTimeBin) {
  selStore.chooseBestTimeBin({ metricKey: navStore.outcome().metric.key });
}

const mapRef = ref();

const toggleOutcomeArea = () => {
  outcomeShown.value = !outcomeShown.value;
  setTimeout(function () {
    mapRef.value.resizeMap();
  }, 1);
};

const totalPopulation = computed(() => {
  // TODO remove cast to Array when Typescript 5.6 is stable
  const mids = [...selStore.midSelections];
  return _.sumBy(mids, (mid) => dataStore.population(mid));
});

const selectedAverage = computed(() =>
  areaMetricAverage({
    mids: selStore.midSelections,
    dataFilterKey: dataFilterKey.value,
    outcomeKey: outcome.value.key,
    timeBin: timeBin.value,
  })
);
const metricTarget = computed(
  () =>
    dataStore.nationalAverage({
      dataFilterKey: dataFilterKey.value,
      outcomeKey: outcome.value.key,
      timeBin: timeBin.value,
    })?.value ?? 0
);

const metricLabel = computed(() => {
  return metricTarget.value
    ? `priority given when above National Average (${navStore.metric().valueFormatter(metricTarget.value)})`
    : "priority given when above National Average";
});

const populationFormatter = computed(() => (population: number): string => {
  const s = compactNumber(population, { precision: 0, noAbbreviation: true });
  if (selStore.coversState && population < navStore.outcome().populationTarget) {
    return `${s} (Entire State/Territory)`;
  } else {
    return s;
  }
});

const areaSelected = computed(() => {
  return selStore.midSelections.size !== 0;
});

const geoStyler = computed(() => {
  const dataFilterKey = navStore.dataFilter().key;
  const outcomeKey = navStore.outcome().key;
  const timeBin = selStore.currentTimeBin;
  if (dataStore.dataIsReady(outcome.value.key)) {
    return geoStylerMaker(
      dataStore.overviewData({
        dataFilterKey,
        outcomeKey,
        timeBin,
      }),
      new Set(selStore.midSelections),
      cyanToPink10
    );
  } else {
    return () => areaStyleBase;
  }
});
</script>

<template>
  <main class="search-results" :class="{ 'outcome-expanded': outcomeShown }">
    <section v-show="outcomeShown" class="card outcome-section" id="outcome-selection">
      <h3 class="card-header d-flex flex-nowrap gap-1 justify-items-stretch">
        <div class="number-badge">1</div>
        <div class="me-auto">Select Outcome</div>
        <button
          aria-controls="outcome-selection"
          class="btn btn-secondary btn-sm"
          @click="toggleOutcomeArea">
          <i class="bi-chevron-double-up"></i> Collapse Outcome Area
        </button>
      </h3>

      <div class="card-body outcome-area-body">
        <OutcomeButtons class="flex-grow-0" />
        <div class="outcome-description-area">
          <h3>Problem</h3>
          <!-- eslint-disable-next-line vue/no-v-html // Sourcing HTML from local file, not user -->
          <p class="text-wrap"><span v-html="outcome.searchProblem"></span></p>
          <h3>Metric</h3>
          <!-- eslint-disable-next-line vue/no-v-html // Sourcing HTML from local file, not user -->
          <p><span v-html="navStore.metric().label"></span></p>
          <h3>Selection Constraints:</h3>
          <p>
            Applications will be given priority if they cover more than
            {{
              compactNumber(outcome.populationTarget, {
                noAbbreviation: true,
                precision: 0,
              })
            }}
            people, are contiguous, and the outcome rate is worse than the national average.
          </p>
        </div>
      </div>
    </section>

    <section class="card region-section">
      <h3 class="card-header d-flex flex-wrap gap-2 align-items-center">
        <div class="number-badge">2</div>
        <div class="flex-grow-1">
          Select {{ navStore.granularityData().plural }} for Intervention
        </div>

        <div class="d-flex flex-wrap gap-2">
          <DataFilterPicker />

          <button
            v-if="!outcomeShown"
            class="outcome-selector-button btn btn-secondary btn-sm"
            aria-controls="outcome-selection"
            :title="`Current outcome: ${navStore.outcome().label}. Click to change to another outcome.`"
            @click="toggleOutcomeArea">
            <img class="outcome-icon" :src="navStore.outcome().icon" alt="" width="20" />
            <span>Outcome <i class="bi-chevron-double-down"></i></span>
          </button>
        </div>
      </h3>
      <div class="card-body region-section-body" :class="`graph-${graphModel.size}`">
        <div
          class="how-to-use d-flex flex-row align-items-center"
          v-if="graphModel.size !== 'expanded'">
          <div class="flex-grow-1">
            Showing {{ navStore.granularityData().definition }}
            Click on a region of the map to get started!
          </div>
        </div>

        <AreaList v-if="graphModel.size !== 'expanded'" />
        <ResultsGraphHolder class="metric-history-graph" v-model="graphModel" />
        <AreaMap
          v-if="graphModel.size !== 'expanded'"
          ref="mapRef"
          :color-ramp="cyanToPink10"
          :geo-styler="geoStyler"
          :outcome-key="outcome.key" />
      </div>
    </section>

    <section class="card gauges-section" :class="{ 'area-selected': areaSelected }">
      <h3 class="card-header">
        <div class="number-badge">3</div>
        Evaluate Area Suitability
      </h3>
      <div class="card-body gauges-body">
        <header>
          Priority will be given to applications where the selected area(s) meet the requirements
          below. Hover your cursor over the question-mark icons for more information on each
          requirement.
        </header>

        <h4 v-if="selStore.midSelections.size === 0" class="alert alert-secondary">
          Select one or more areas to view suitability.
        </h4>
        <template v-else>
          <ContiguousGauge />
          <hr />
          <MetricGauge
            :actual="totalPopulation"
            :targetMin="navStore.outcome().populationTarget"
            :targetLabel="`above ${populationFormatter(navStore.outcome().populationTarget)} or an entire US State/Territory`"
            :valid="selStore.coversState || totalPopulation > navStore.outcome().populationTarget"
            :valueFormatter="populationFormatter"
            class="population-gauge"
            details="Priority will be given to applications when population is greater than the minimum listed below."
            label="Population"
            labelIcon="bi-people-fill" />

          <hr />

          <MetricGauge
            v-if="selectedAverage.value !== null"
            :actual="selectedAverage.value"
            label="Rate"
            :labelIcon="navStore.outcome().icon"
            :targetMin="metricTarget"
            :valid="_.gte(selectedAverage.value, metricTarget)"
            :valueFormatter="navStore.metric().valueFormatter"
            class="outcome-gauge"
            details="Priority will be given to applications when average rate is worse than the national average."
            :target-label="metricLabel" />
        </template>
      </div>
    </section>

    <section class="card demographics-section">
      <h5 class="card-header text-center">Demographics</h5>
      <DemographicDistribution class="card-body" />
    </section>

    <section class="card export-section">
      <h3 class="card-header">
        <div class="number-badge">4</div>
        Export Selected Data
      </h3>
      <div class="card-body d-flex flex-row justify-content-center gap-2">
        <button
          class="btn btn-outline-primary big-button"
          title="Click to export CSV"
          :disabled="selStore.midSelections.size === 0"
          @click="createCSV">
          {{ "Export as CSV" }}
        </button>
        <button
          class="btn btn-outline-primary big-button"
          title="Click to export PDF"
          :disabled="selStore.midSelections.size === 0"
          @click="downloadPDF">
          Export as PDF
        </button>
      </div>
    </section>
  </main>
  <footer class="page-footer">
    <p>
      For more information on data sources, limitations, and calculations, please see our
      <a href="/aboutdata">About the Data</a> page.
    </p>
    <p>
      {{ navStore.metric().dataUsage }}
    </p>
  </footer>
</template>

<style scoped>
.search-results {
  box-sizing: border-box;
  display: grid;
  background-color: var(--brand-cool-gray-10);
  gap: 0.5rem;
  padding: 0.5rem;

  /* Narrowest breakpoint--single column */
  grid-template-columns: 1fr;
  grid-template-rows: auto repeat(4, min-content);
  grid-template-areas:
    "region"
    "gauges"
    "demographics"
    "export";

  &.outcome-expanded {
    grid-template-areas:
      "outcome"
      "region"
      "gauges"
      "demographics"
      "export";
    grid-template-rows: auto auto repeat(3, min-content);
  }
}
.outcome-area-body {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  justify-content: center;
}
.outcome-description-area {
  max-width: 30em;
  text-wrap: balance;
}
.outcome-selector-button {
  display: flex;
  flex: row nowrap;
  white-space: nowrap;
  gap: 1em;
  align-items: center;
}

/* When the screen is wide, use two columns instead. */
@media (min-width: 64rem) {
  .search-results {
    align-content: start;
    grid-template-areas:
      "region gauges"
      "region demographics"
      "region export";
    grid-template-columns: 1fr min-content;
    grid-template-rows: auto 1fr auto;
  }

  .search-results.outcome-expanded {
    grid-template-areas:
      "outcome outcome"
      "region gauges"
      "region demographics"
      "region export";
    grid-template-columns: 1fr min-content;
    grid-template-rows: min-content auto 1fr auto;
  }
}

.outcome-section {
  grid-area: outcome;

  .outcome-select {
    min-width: min-content;
  }
}

.region-section {
  grid-area: region;
}

.how-to-use {
  grid-area: how;
}

.area-list {
  grid-area: area-list;
  height: 24rem;
}

.metric-history-graph {
  grid-area: metric-history-graph;
}

.area-map {
  grid-area: area-map;
}

.region-section-body {
  display: grid;
  gap: 0.5rem;

  /* Default to single-column layout */
  grid-template-areas:
    "how"
    "area-list"
    "metric-history-graph"
    "area-map";
  grid-template-columns: 1fr;
  grid-template-rows: min-content repeat(3, 24rem);

  .outcome-expanded .graph-expanded {
    grid-template-rows: 40vh; /* auto gives wrong value since there's nothing to auto off of except the reactive chart. */
  }
}

/* If there's enough space, use two columns for the "intervention" section */
@media (min-width: 64rem) {
  .region-section-body {
    grid-template-areas:
      "how       how"
      "area-list metric-history-graph"
      "area-map  area-map";
    grid-template-columns: auto 1fr;
    grid-template-rows: min-content 24rem 1fr;

    &.graph-expanded {
      grid-template-areas: "metric-history-graph";
      grid-template-rows: auto;
      grid-template-columns: auto;
    }

    &.graph-collapsed {
      grid-template-areas:
        "how                  how"
        "metric-history-graph area-map"
        "area-list            area-map";
      grid-template-rows: min-content auto 1fr;

      .area-list {
        height: calc(100vh - 23rem + 4px);
      }
    }

    .outcome-expanded .graph-collapsed .area-list {
      height: calc(100vh - 52rem);
    }
  }
}

.gauges-section {
  grid-area: gauges;

  hr {
    margin-top: 0em;
  }
}

.gauges-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding-block-end: 0.25rem;

  hr {
    margin: 0;
  }
}

.demographics-section {
  grid-area: demographics;
}

.export-section {
  grid-area: export;
}

.page-footer {
  font-size: 80%;
  margin: auto;
  padding: 0.5rem 1rem;
  text-align: center;
  text-wrap: balance;

  p {
    margin: 0;
  }

  p + p {
    margin-top: 1em;
  }
}
</style>
