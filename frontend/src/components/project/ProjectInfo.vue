<script setup lang="ts">
import DataFilterPicker from "@/components/common/DataFilterPicker.vue";
import TimeBinPicker from "@/components/common/TimeBinPicker.vue";
import ProjectAreasDropdown from "@/components/project/ProjectAreasDropdown.vue";
import ProjectDetailsArea from "@/components/project/ProjectDetailsArea.vue";
import ProjectMembers from "@/components/project/ProjectMembers.vue";
import { useProjectStore } from "@/stores/project";
import ProjectFilters from "./ProjectFilters.vue";

const projectStore = useProjectStore();
</script>

<template>
  <section class="project-info card">
    <div class="project-details card-header">
      <h3
        class="text-white p-0 m-0"
        title="Project name
      ">
        {{ projectStore.project()?.projectName ?? "No project selected" }}
      </h3>
      <div class="d-flex flex-wrap gap-4">
        <ProjectAreasDropdown />
        <ProjectMembers />
        <label>Selected Data To Display: </label>
        <DataFilterPicker includeDID id="project-data-filter-picker" />
        <label>Selected Period To Display:</label>
        <TimeBinPicker id="project-time-picker" />
      </div>
    </div>
    <ProjectDetailsArea />
    <ProjectFilters />
  </section>
</template>

<style scoped>
.project-info {
  display: flex;
  flex-direction: column;
}

.project-details {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem 2rem;
  justify-content: space-between;
  padding: 1rem;
  label {
    display: flex;
    gap: 0.5rem;
    white-space: nowrap;
    place-items: center;
  }
}
</style>
