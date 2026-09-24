<script setup lang="ts">
/**
  Shows a list of selectable map entries, grouped by state.
 */

import SelectionDropdown from "@/components/areaSelector/SelectionDropdown.vue";
import StateGroup from "@/components/areaSelector/StateGroup.vue";
import LoadingWidget from "@/components/common/LoadingWidget.vue";
import { useDataStore } from "@/stores/data";
import { useNavigationStore } from "@/stores/nav";
import SimpleTooltip from "@/components/common/SimpleTooltip.vue";

const navStore = useNavigationStore();
const dataStore = useDataStore();
</script>

<template>
  <section class="area-list" aria-label="Area list section">
    <header class="area-list-header">
      <div>
        {{ navStore.granularityData().plural }} By Region
        <SimpleTooltip
          hasInfoIcon
          :text="navStore.granularityData().definition"
          data-position="bottom"
          min-width="12em" />
      </div>
      <SelectionDropdown />
    </header>
    <main class="state-groups">
      <LoadingWidget v-if="!dataStore.areasByState.length" label="Loading data..." />
      <StateGroup v-else v-for="sg in dataStore.areasByState" :key="sg.mid" :stateGroup="sg" />
    </main>
  </section>
</template>

<style scoped>
.area-list {
  background-color: white;
  border: 1px solid var(--brand-cool-gray-20);

  min-width: max-content;
  overflow: clip scroll;
  .dropdown-menu {
    position: relative;
    z-index: 99999; /* Get it in front of the leaflet Legend, which is at 1000. */
    :is(ul) {
      max-height: min(48em, calc(100vh - 30em));
      overflow-y: scroll;
    }
  }
  .area-list-header {
    background: var(--brand-cool-gray-5);
    display: grid;
    align-items: center;
    grid-template-columns: 1fr auto;
    gap: 1rem;
    padding: 0.25rem 0.5rem;
  }
  .state-groups {
    padding: 0.25rem;
  }
}
</style>
