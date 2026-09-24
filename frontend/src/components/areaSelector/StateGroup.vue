<script setup lang="ts">
/**
 * Shows a compact list of areas in a state.
 */
import { useDataStore } from "@/stores/data";
import { useNavigationStore } from "@/stores/nav";
import { useSelectionStore } from "@/stores/selection";
import type { AreaListState, MID } from "@/types";
import { isOfGranularity } from "@/util/mapUtils";
import _ from "lodash";
import { computed } from "vue";
import { compactNumber } from "@/util/formatters";

const props = defineProps<{ stateGroup: AreaListState }>();

const dataStore = useDataStore();
const navStore = useNavigationStore();
const selStore = useSelectionStore();

const areasOfRightGranularity = computed<Record<MID, string /* label */>>(() => {
  const g = navStore.outcome().spatialGranularity;
  const result: Record<MID, string> = {};
  _.keys(props.stateGroup.areas).forEach((mid) => {
    if (isOfGranularity(mid, g)) {
      result[mid] = props.stateGroup.areas[mid];
    }
  });
  return result;
});

const numberOfSelectionsInState = computed(
  () =>
    _.keys(areasOfRightGranularity.value).filter((mid) => selStore.midSelections.has(mid)).length
);

function selectAllInState(selected: boolean) {
  selStore.setSelections(Object.keys(areasOfRightGranularity.value), selected);
}
</script>

<template>
  <details class="state-group" v-if="dataStore._dataIsReady['demographics']">
    <summary class="state-group-summary">
      <div class="flex-grow-1">
        {{ dataStore.areaName(props.stateGroup.mid) }} ({{ numberOfSelectionsInState }} of
        {{ _.size(areasOfRightGranularity) }})
      </div>
      <button
        class="btn btn-sm btn-outline-primary text-nowrap"
        @click="selectAllInState(numberOfSelectionsInState !== _.size(areasOfRightGranularity))">
        {{
          numberOfSelectionsInState === _.size(areasOfRightGranularity) ? "Remove All" : "Add All"
        }}
      </button>
    </summary>

    <section class="state-group-body" aria-label="State group section">
      <div v-if="_.size(areasOfRightGranularity) === 0" class="px-4 py-2 text-muted">
        No areas found.
      </div>

      <div v-else v-for="(label, mid) in areasOfRightGranularity" :key="mid" class="area-row">
        <input
          :id="`area-row-check-${mid}`"
          type="checkbox"
          :checked="selStore.midSelections.has(mid)"
          @click="() => selStore.toggleSelection(mid)" />
        <label :for="`area-row-check-${mid}`">{{ label }} </label>
        <details v-if="navStore.outcome().spatialGranularity === 'ZCTA3'">
          <summary>[Show all]</summary>
          <ul>
            <li v-for="countyMID in dataStore.areaIntersects(mid, 'COUNTY')" :key="countyMID">
              {{ dataStore.areaName(countyMID) }}
              (Pop: {{ compactNumber(dataStore.population(countyMID)) }})
            </li>
          </ul>
        </details>
      </div>
    </section>
  </details>
</template>

<style scoped>
.state-group {
  min-width: 18rem; /* Chosen so that `Northern Mariana Islands (0 of 1)` doesn't wrap or collide. */
  .state-group-summary {
    align-items: center;
    background: white;
    cursor: pointer;
    display: flex;
    flex-direction: row;
    font-size: 0.85em;
    font-weight: bold;
    list-style: none;
    padding: 0.25em 0.5em;

    &:before {
      /* Make a triangle using CSS borders, which looks good at all font sizes */
      display: inline-block;
      height: 0px;
      width: 0px;
      border-block: 0.5rem solid transparent;
      border-inline-start: 0.5rem solid black;
      content: " ";
      margin-right: 0.35em;

      transition-duration: 200ms;
    }
    &:hover {
      background-color: var(--brand-cool-gray-10);
    }
  }
  &[open] {
    background-color: var(--brand-cool-gray-10);
    & summary:before {
      transform: rotate(90deg);
    }
  }
}

.state-group-body {
  display: block;
}
.area-row {
  align-items: start;
  display: grid;
  grid-template-areas:
    "check label"
    "blank counties";
  grid-template-columns: auto 18rem;

  font-size: 0.85rem;
  padding: 0.25em 0.5em;
  &:hover {
    background-color: var(--brand-cool-gray-40);
  }

  input {
    grid-area: check;
    margin: 0.25em 0.5em 0em 0em;
  }
  label {
    grid-area: label;
  }
  details {
    grid-area: counties;
    summary {
      color: var(--bs-link-color);
      text-decoration: underline;
      &:hover {
        color: var(--bs-link-hover-color);
      }
    }
  }
}
</style>
