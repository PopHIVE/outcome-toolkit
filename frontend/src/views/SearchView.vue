<script setup lang="ts">
/**
 * Search View guides the user through the process of selecting their role, navStore.outcome(), and an initial location for inquiry.
 * It then continues to the search results page.
 */
import OutcomeButtons from "@/components/common/OutcomeButtons.vue";
import AreaMap from "@/components/map/AreaMap.vue";
import { useDataStore } from "@/stores/data";
import { useNavigationStore } from "@/stores/nav";
import { useSelectionStore } from "@/stores/selection";
import { cyanToPink10 } from "@/util/colorUtils";
import { geoStylerMaker } from "@/util/mapUtils";
import { computed } from "vue";
import { useRouter } from "vue-router";
import type { OutcomeKeyType } from "@/types";

const router = useRouter();
const dataStore = useDataStore();
const navStore = useNavigationStore();
const selStore = useSelectionStore();
const outcomeKey = computed<OutcomeKeyType>(() => navStore.outcome().key);

const dataFilterKey = navStore.dataFilter().key;
if (dataFilterKey === "did") {
  // If the user came from a project, DiD doesn't make sense.
  navStore.setDataFilter("t6mo");
}

if (!selStore.currentTimeBin) {
  // If the user came straight here, they may have arrived before the time bin data.
  setTimeout(() => selStore.chooseBestTimeBin({ metricKey: navStore.outcome().metric.key }), 500);
}

const geoStyler = computed(() => {
  const timeBin = selStore.currentTimeBin;
  // Note: hover style is done in theme.css
  return geoStylerMaker(
    dataStore.overviewData({ dataFilterKey: "t6mo", outcomeKey: outcomeKey.value, timeBin }),
    new Set(), // No selections on Search page.
    cyanToPink10
  );
});
</script>

<template>
  <main class="search-main">
    <section class="card select-outcome" aria-label="Select Outcome section">
      <h3 class="card-header">
        <div class="number-badge">1</div>
        Select a health outcome to explore
      </h3>
      <div class="card-body d-flex flex-column gap-2">
        <OutcomeButtons />
        <h4>{{ navStore.outcome().label }}</h4>
        <!-- eslint-disable-next-line vue/no-v-html // Sourcing HTML from local file, not user -->
        <p v-html="navStore.outcome().selectDescription"></p>
        <button
          class="btn btn-outline d-flex gap-2 align-self-center"
          @click="router.push({ path: '/healthoutcomes', hash: `#nav-${navStore.outcome().key}` })"
          aria-label="Learn More link"
          :style="{ textDecoration: 'underline', textDecorationColor: 'var(--brand-cyan)' }">
          Learn More
          <i class="bi-box-arrow-up-right"></i>
        </button>
      </div>
    </section>

    <section class="card select-area" aria-label="Select Area section">
      <h3 class="card-header">
        <div class="number-badge">2</div>
        <span>Select a region to explore</span>
      </h3>
      <AreaMap :color-ramp="cyanToPink10" :geo-styler="geoStyler" :outcome-key="outcomeKey" />
    </section>

    <section class="to-search-results">
      <a class="btn btn-info px-5 text-black" href="/results">
        Proceed with selecting a region <i class="bi-arrow-right"></i>
      </a>
    </section>
    <section class="data-usage">{{ navStore.metric().dataUsage }}</section>
  </main>
</template>

<style scoped>
.search-main {
  box-sizing: border-box;
  background-color: var(--brand-cool-gray-10);
  display: grid;
  gap: 1rem;
  grid-template-areas:
    "outcome region"
    "proceed proceed"
    "usage usage";
  grid-template-columns: minmax(22rem, 1fr) 2fr;
  grid-template-rows: 1fr auto auto;
  justify-items: stretch;
  padding: 1rem;
  height: calc(100vh - 7rem + 6px);
}

.select-area {
  grid-area: region;
  display: grid;
  grid-template-rows: auto 1fr;
}
.select-outcome {
  grid-area: outcome;
}
.to-search-results {
  grid-area: proceed;
  display: grid;
  align-content: center;
  justify-content: center;
  margin: 2rem;
}
.data-usage {
  grid-area: usage;
  margin: 1rem;
  text-align: center;
  text-wrap: balance;
}
</style>
