<script setup lang="ts">
import { useDataStore } from "@/stores/data";
import { useProjectStore } from "@/stores/project";
import { computed } from "vue";
import { pln } from "@/util/formatters";

const dataStore = useDataStore();
const projectStore = useProjectStore();

// TODO: group areas by state in ProjectAreaDropdown?
const areas = computed(() => {
  const project = projectStore.project();
  return project ? project.areas.map((mid) => dataStore.getGranularName(mid)) : [];
});
</script>

<template>
  <div class="project-areas dropdown">
    <button
      aria-expanded="false"
      class="dropdown-toggle btn btn-sm btn-primary"
      data-bs-toggle="dropdown"
      id="project-areas-toggle"
      title="Project geography">
      {{ pln(areas.length, "project geography", "project geographies") }}
    </button>

    <ul class="dropdown-menu dropdown-menu-end project-area-dropdown user-select-none">
      <li v-for="a in areas" :key="a" class="dropdown-item disabled text-secondary" disabled>
        {{ a }}
      </li>
    </ul>
  </div>
</template>

<style scoped></style>
