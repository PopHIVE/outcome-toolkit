<script setup lang="ts">
import { useDataStore } from "@/stores/data";
import { useSelectionStore } from "@/stores/selection";
const dataStore = useDataStore();
const selStore = useSelectionStore();
</script>

<template>
  <div class="selection-dropdown">
    <button
      aria-expanded="false"
      class="btn btn-sm btn-info dropdown-toggle"
      data-bs-toggle="dropdown"
      type="button">
      {{ selStore.midSelections.size }} selected
    </button>
    <div class="dropdown-menu">
      <ul class="p-0 m-0">
        <li v-if="selStore.midSelections.size === 0" class="dropdown-item disabled">
          No selections
        </li>
        <template v-else>
          <li class="dropdown-item d-flex justify-content-start">
            <button class="btn btn-sm btn-warning" @click="selStore.clearSelections">
              Remove All
            </button>
          </li>
          <li
            v-for="mid in selStore.midSelections"
            :key="mid"
            class="dropdown-item selected-area-item">
            <div>{{ dataStore.areaName(mid) }}</div>
            <button
              class="btn btn-sm btn-outline-warning"
              @click="() => selStore.toggleSelection(mid)"
              :title="`Remove ${dataStore.areaName(mid)} from selection`">
              <i class="bi-dash-circle-fill"></i>
            </button>
          </li>
        </template>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.dropdown-menu {
  z-index: 99999; /* Get in front of parent's scrollbar */
  user-select: none;
}
.selected-area-item {
  display: flex;
  align-items: center;
  cursor: default;
  gap: 1rem;
  justify-content: space-between;
  user-select: none;
  &:hover {
    background: var(--brand-cool-gray-10);
  }
}
</style>
