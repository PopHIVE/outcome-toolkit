<script setup lang="ts">
import SimpleTooltip from "@/components/common/SimpleTooltip.vue";
import { useNavigationStore } from "@/stores/nav";
import { DATA_FILTERS } from "@/types";
import _ from "lodash";
import { computed } from "vue";
const navStore = useNavigationStore();
const props = withDefaults(defineProps<{ includeDID?: boolean }>(), { includeDID: false });

const dataFilter = computed(() => navStore.dataFilter());

const filtersToShow = computed(() =>
  props.includeDID ? DATA_FILTERS : _.omit(DATA_FILTERS, "did")
);
</script>

<template>
  <div class="data-filter-picker">
    <div class="btn-group btn-group-sm">
      <button
        aria-expanded="false"
        class="btn btn-secondary dropdown-toggle"
        data-bs-toggle="dropdown">
        {{ _.startCase(dataFilter.label) }}
      </button>
      <ul class="dropdown-menu">
        <li
          v-for="{ key, label, description } in filtersToShow"
          class="data-filter-item dropdown-item user-select-none"
          :class="{ active: dataFilter.key === key }"
          name="data-filter"
          :key="key"
          @click="navStore.setDataFilter(key)">
          {{ _.startCase(label) }}
          <SimpleTooltip hasInfoIcon :text="description" min-width="24em" data-position="bottom" />
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.data-filter-picker {
  display: flex;
  align-items: center;
  gap: 1em;
  font-size: 0.75rem;
}
</style>
