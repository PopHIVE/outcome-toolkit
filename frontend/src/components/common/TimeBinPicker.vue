<script lang="ts" setup>
/**
 * TimeBin picker lets the user change which slice of time is being used to
 * populate the map.
 */
import { useDataStore } from "@/stores/data";
import { useNavigationStore } from "@/stores/nav";
import { useSelectionStore } from "@/stores/selection";
import { computed } from "vue";

const dataStore = useDataStore();
const navStore = useNavigationStore();
const selStore = useSelectionStore();
const metricKey = computed(() => navStore.metric().key);

const bins = computed(() => dataStore.timeBins({ metricKey: metricKey.value }));
</script>

<template>
  <div class="time-bin-picker btn-group btn-group-sm" aria-label="Choose date range to show">
    <button
      aria-expanded="false"
      class="btn btn-secondary btn-sm dropdown-toggle"
      data-bs-toggle="dropdown"
      type="button">
      {{ selStore.currentTimeBin?.asString ?? "Choose a date range..." }}
    </button>
    <ul class="dropdown-menu">
      <li
        v-for="bin of bins"
        :key="bin.raw"
        class="time-bin-item dropdown-item user-select-none"
        :class="{ active: bin.raw === selStore.currentTimeBin?.raw }"
        :aria-current="bin.raw === selStore.currentTimeBin?.raw"
        @click="selStore.setCurrentTimeBin(bin)">
        {{ bin.asString }}
      </li>
    </ul>
  </div>
</template>

<style scoped>
.dropdown-menu {
  max-height: 50vh;
  overflow-y: auto;
}
li,
button {
  white-space: nowrap;
  user-select: none;
}
</style>
