<script setup lang="ts">
import { useDataStore } from "@/stores/data";
import { type OutcomeKeyType } from "@/types";
import { compactPercent, payoutFormatter, pln } from "@/util/formatters";
import _ from "lodash";
import { computed } from "vue";
import { key2outcome } from "@/util/metricUtils";

const props = defineProps<{
  outcomeKey: OutcomeKeyType;
  showCaption?: boolean;
}>();

const dataStore = useDataStore();
const payouts = computed(() => _.omit(dataStore.targetPayouts(props.outcomeKey), "baseline"));
</script>

<template>
  <table class="table table-bordered caption-top responsive-table">
    <caption v-if="showCaption">
      The example below assumes a $15M program and $30M additional Outcome Buyers reward pool (2:1
      match).
    </caption>
    <thead>
      <tr>
        <th aria-disabled="true" scope="col">&nbsp;</th>
        <th scope="col" v-for="{ period } in payouts" :key="period" class="text-nowrap">
          {{ period === "total" ? "Overall" : `${period} months` }}
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th class="row-header" scope="row">Maximum Payout for Period</th>
        <td v-for="{ period, maximumPayout } in payouts" :key="period">
          {{ payoutFormatter(maximumPayout, { precision: 2 }) }}
        </td>
      </tr>
      <tr>
        <th class="row-header" scope="row">Target Performance</th>
        <td v-for="{ period, targetRate } in payouts" :key="period">
          <span v-if="outcomeKey === 'cardio'">{{ pln(targetRate, "percentage point") }}</span>
          <span v-else>{{ compactPercent(targetRate) }}</span>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
.row-header {
  background-color: var(--brand-white);
  text-align: left;
  width: 7em;
  text-wrap: balance;
}

th {
  background-color: var(--brand-cool-gray-10);
  text-align: center;
  vertical-align: middle;
  width: 3em;
}

td {
  background-color: var(--brand-white);
  text-align: center;
  vertical-align: middle;
  width: 3em;
}

/* Responsive styling */
.responsive-table {
  width: 100%;
  border-collapse: collapse;
}

@media (max-width: 50rem) {
  .responsive-table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
}
caption {
  font-style: italic;
  text-align: center;
  text-wrap: balance;
}
</style>
