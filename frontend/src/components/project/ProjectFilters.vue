<script setup lang="ts">
import { useProjectStore } from "@/stores/project";
import { useDataStore } from "@/stores/data";
import { computed } from "vue";
import { LOADING_STRING } from "@/util/Consts";
import { formattedDate } from "@/util/dateUtils";

const projectStore = useProjectStore();
const outcomeKey = computed(() => {
  return projectStore.project()?.outcomeKey ?? "soc";
});

const dataStore = useDataStore();

const dataDetails = computed(() => dataStore.dataDetails(outcomeKey.value));
</script>

<template>
  <section class="project-filters card">
    <!-- TODO: Move filters from ProjectInfo here -->
    <div class="filters"></div>

    <h4 v-if="!dataStore.dataIsReady()" class="header whole-tooltip">{{ LOADING_STRING }}</h4>
    <div v-else>
      <p class="mb-0 last-updated">
        Outcome Toolkit Data last updated {{ formattedDate(dataDetails.latest_date) }}
      </p>
    </div>
  </section>
</template>

<style scoped>
.project-filters {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  padding: 0.5rem;
}

.last-updated {
  font-style: italic;
  font-size: small;
}
</style>
