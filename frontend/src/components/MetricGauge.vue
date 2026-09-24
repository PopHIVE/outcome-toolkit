<script setup lang="ts">
import { compactNumber } from "@/util/formatters";
import _ from "lodash";
import { computed } from "vue";
import SimpleTooltip from "@/components/common/SimpleTooltip.vue";

const props = defineProps<{
  actual: number;
  details?: string;
  label: string;
  labelIcon: string;
  rangeMax?: number;
  rangeMin?: number;
  targetLabel: string;
  targetMax?: number;
  targetMin?: number;
  valid: boolean;
  valueFormatter?: (n: number) => string;
}>();

const valueFormatter = props.valueFormatter ?? ((n) => compactNumber(n));

// Clip the actual value to [rangeMin, rangeMax] when appropriate
const safeActual = computed(() =>
  !_.isNil(props.actual) && isFinite(props.actual)
    ? Math.min(props.rangeMax ?? Infinity, Math.max(props.rangeMin ?? 0, props.actual))
    : (props.rangeMin ?? 0)
);

// If a range max wasn't specified, compute one based on leaving enough headroom.
const thermDataWidth = computed(
  () =>
    props.rangeMax ??
    1.2 * Math.max((props.targetMin ?? 0) * 2, props.targetMax ?? 0, safeActual.value)
);

/* Used to manufacture the dynamic CSS that computes the width of the thermometer.  */
const dataToPct = (d: number) => `${100 * (d / thermDataWidth.value)}%`;
</script>

<template>
  <div class="metric-gauge" :class="{ valid: props.valid }">
    <h4 class="metric-gauge-title">
      <SimpleTooltip
        hasInfoIcon
        :content="label"
        :text="props.details"
        data-position="bottom"
        minWidth="32em" />
    </h4>
    <div class="gauge-guide">Threshold: {{ props.targetLabel }}</div>
    <div class="gauge-holder">
      <div class="gauge-bg"></div>
      <div
        class="gauge-range"
        :title="`Target range: ${targetLabel}`"
        :style="{
          left: dataToPct(props.targetMin ?? 0),
          right: props.targetMax ? dataToPct(thermDataWidth - (props.targetMax ?? 0)) : 0,
        }"></div>

      <div
        class="actual-line"
        :style="{ width: dataToPct(safeActual) }"
        :title="`Selected: ${safeActual}`"></div>
    </div>
    <div class="actual-label" :title="`Selected: ${actual}`">
      <div class="text-dark">Selected:</div>
      <div>{{ valueFormatter(safeActual) }}</div>
      <div>
        <i
          class="fs-3"
          :class="{
            [props.valid ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill']: true,
          }"></i>
      </div>
    </div>
  </div>
</template>

<style scoped>
.metric-gauge {
  display: grid;

  column-gap: 0.5rem;
  grid-template-areas:
    "gauge-guide gauge-guide"
    "title gauge-holder"
    "actual-label actual-label";
  grid-template-columns: auto 20rem;
  grid-template-rows: auto 1.75rem auto;
}

.metric-gauge-title {
  grid-area: title;
  height: 2rem; /* Make it line up with the bar */
  margin: 0;
}

.actual-label {
  align-items: center;
  color: var(--brand-cool-gray-70);
  display: flex;
  font-size: 1.1rem;
  font-weight: bold;
  gap: 0.5rem;
  grid-area: actual-label;
  justify-self: end;
  text-align: end;
}
.actual-line {
  position: absolute;
  text-align: right;
  height: 2rem;
  top: 0rem;
  left: 0rem;
  border-right: 5px solid var(--brand-cool-gray-50);
  background-color: transparent;
}
.gauge-bg {
  position: absolute;
  background-color: #ddd;
  box-sizing: border-box;
  height: 0.75rem;
  top: 0.625rem;
  left: 0rem;
  width: 100%;
}
.gauge-guide {
  grid-area: gauge-guide;
  font-size: 0.85rem;
  text-align: right;
  margin-block-end: 0.25rem;
}

.gauge-holder {
  grid-area: gauge-holder;
  container-name: gauge-container; /* To allow pieces to be positioned absolutely. */
  container-type: size;
  contain: layout;
}
.gauge-range {
  position: absolute;
  box-sizing: border-box;
  height: 0.75rem;
  min-width: 2rem;
  top: 0.625rem;
  left: 0rem;
  background-color: var(--brand-cool-gray-50);
}

.valid {
  .actual-label {
    color: var(--brand-violet);
  }
  .actual-line {
    border-right-color: var(--brand-violet-light);
  }
  .gauge-range {
    background-color: var(--brand-violet);
  }
}
</style>
