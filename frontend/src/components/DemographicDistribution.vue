<script setup lang="ts">
import { DEMOGRAPHIC_DATA, type DemographicKeyType } from "@/stores/DEMOGRAPHIC_DATA";
import { compactNumber, compactPercent, compactTitle } from "@/util/formatters";
import { stackDemographics, type DemographicStack } from "@/util/stackDemographics";
import _ from "lodash";
import { computed, ref } from "vue";

const selectedDemographic = ref<DemographicKeyType>("age");

const baselineDemographics = computed<DemographicStack>(() =>
  stackDemographics(selectedDemographic.value)
);

// TODO: get general numbers from backend

const baselineTotal = computed(() =>
  Math.max(1, _.sum(_.map(baselineDemographics.value, "value")))
);
// const selectionTotal = computed(() => Math.max(1, _.sum(_.map(selectionDemographics.value, "value"))));
</script>

<template>
  <section class="demographic-distribution" aria-label="Demographic distribution section">
    <div class="demo-btns btn-group" role="group" aria-label="Select a demographics category">
      <template v-for="{ key, label } in DEMOGRAPHIC_DATA" :key="key">
        <input
          :aria-label="key"
          :id="`demographic-button-${key}`"
          :value="key"
          class="btn-check"
          type="radio"
          v-model="selectedDemographic" />
        <label class="btn btn-outline-primary" :for="`demographic-button-${key}`"
          >{{ label }}
        </label></template
      >
    </div>
    <div v-if="!_.size(baselineDemographics)" class="alert alert-warning text-center">
      No data found
    </div>
    <div v-else class="table-scroller">
      <table class="table table-sm table-striped table-hover border-0 p-0 m-0">
        <thead>
          <tr>
            <th>{{ DEMOGRAPHIC_DATA[selectedDemographic].label }}</th>
            <th class="text-right">Selected</th>
            <th class="text-right">%</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="{ displayName, label, value } of baselineDemographics" :key="label">
            <td cursor-default>{{ displayName }}</td>
            <td class="font-monospace" :title="compactTitle(value, { hideBelow: 100 })">
              {{ compactNumber(value, { hideBelow: 100, precision: 0, noAbbreviation: true }) }}
            </td>
            <td class="font-monospace">
              {{ compactPercent(value / baselineTotal) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.demographic-distribution {
  display: flex;
  flex-direction: column;
  overflow-x: clip;
  overflow-y: scroll;
  padding-left: 0.5rem;
  border-bottom: 2px solid #0008;

  table {
    font-size: 0.75rem;
    thead th {
      position: sticky;
      top: 0;
    }
  }
}
.demo-btns {
  justify-self: center;
}
.table-scroller {
  contain: strict;
  overflow-y: auto;
  min-height: 16rem;
  height: 100%;
  /* max-height: max(18rem, calc(100vh - 44rem)); */
}
</style>
