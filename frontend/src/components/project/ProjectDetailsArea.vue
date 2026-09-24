<script setup lang="ts">
import { key2outcome } from "@/util/metricUtils";

import { useProjectStore } from "@/stores/project";
import { compactPercent, dateFormatter, payoutFormatter } from "@/util/formatters";
import _ from "lodash";
import { computed } from "vue";

const projectStore = useProjectStore();
const project = computed(() => projectStore.project());

const cumulativePayout = computed(() =>
  project.value ? _.sum(_.map(project.value.projectMeasurements, (r) => r?.payout ?? 0)) : 0
);
</script>

<template>
  <section v-if="!project" class="project-details-area d-flex text-center gap-1 py-2">
    No project selected.
  </section>
  <section v-else class="project-details-area d-flex text-center gap-1 py-2">
    <div class="d-flex gap-1">
      <div class="fw-bold text-right">Period of Performance:</div>
      <div class="text-left" v-if="project.performancePeriodFrom && project.performancePeriodTo">
        {{ dateFormatter(project.performancePeriodFrom) }} to
        {{ dateFormatter(project.performancePeriodTo) }}
      </div>
      <div v-else>TBD</div>
    </div>
    <div class="d-flex gap-1">
      <div class="fw-bold text-right">Selected Outcome:</div>
      <div class="text-left">{{ key2outcome(project.outcomeKey).label }}</div>
    </div>
    <div class="d-flex gap-1">
      <div class="fw-bold text-right">Cumulative Payout Earned:</div>
      <div class="text-success" :title="`Cumulative Payout: ${cumulativePayout}`">
        {{ payoutFormatter(cumulativePayout, { precision: 2 }) }}
      </div>
      of $15M available program funds ({{
        compactPercent(cumulativePayout / 15000000, { precision: 2 })
      }})
    </div>
  </section>
</template>

<style scoped>
.project-details-area {
  display: grid;
  align-items: center;
  background: var(--brand-cool-gray-30);
  gap: 1rem;
  justify-content: space-evenly;
}
</style>
