<script setup lang="ts">
import ValueBox from "@/components/common/ValueBox.vue";
import { useDataStore, type DatumProps } from "@/stores/data";
import type { MetricBin } from "@/types";
import {
  cyanToPink10,
  MISSING_BIN,
  MISSING_COLOR,
  MISSING_INDEX,
  SELECTED_BIN,
  SELECTED_INDEX,
} from "@/util/colorUtils";
import { computed } from "vue";
import { key2outcome } from "@/util/metricUtils";

const {
  binRank,
  datumProps,
  showFullText = false,
} = defineProps<{
  binRank: number | null | undefined;
  datumProps: DatumProps;
  showFullText?: boolean;
}>();

const dataStore = useDataStore();
const metricValueFormatter = computed(
  () => key2outcome(datumProps.outcomeKey).metric.valueFormatter
);

const bin = computed<MetricBin | undefined>(() => {
  if (binRank === SELECTED_INDEX) {
    return SELECTED_BIN;
  } else if (binRank === MISSING_INDEX) {
    return MISSING_BIN;
  } else if (datumProps) {
    return dataStore.metricBinByRank({
      ...datumProps,
      metricRank: binRank,
    });
  }
  return undefined;
});
</script>
<template>
  <div class="legend-bin-row" v-if="bin">
    <div>
      <i class="bi-square-fill" :style="`color: ${cyanToPink10[bin.rank] ?? MISSING_COLOR}`"></i>
      {{ showFullText ? bin.rank_value : bin.rank_value.replace(/ *than national average/i, "") }}
    </div>
    <template v-if="!isNaN(bin.min) && bin.rank === 9">
      <ValueBox
        :metricValue="bin.min"
        popoverPrefix="Bin value (and up):"
        :value-formatter="metricValueFormatter" />
      <div class="single-bin">and up</div>
    </template>
    <template v-else-if="!isNaN(bin.min)">
      <ValueBox
        :metricValue="bin.min"
        popoverPrefix="Bin minimum:"
        :value-formatter="metricValueFormatter" />
      <div>to</div>
      <ValueBox
        :metricValue="bin.max"
        popoverPrefix="Bin maximum:"
        :value-formatter="metricValueFormatter" />
    </template>
  </div>
</template>

<style>
.legend-bin-row {
  display: grid;
  grid-column: 1 / span 4;
  grid-template-columns: subgrid;
  align-items: center;
  gap: 0.5em;
  & > div {
    text-wrap: nowrap;
    min-width: max-content;
  }
  & > .single-bin {
    grid-column: 3 / 5;
  }
}
</style>
