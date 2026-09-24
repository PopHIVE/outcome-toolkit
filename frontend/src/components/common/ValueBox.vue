<script lang="ts" setup>
import SimpleTooltip from "@/components/common/SimpleTooltip.vue";
import _ from "lodash";
import { computed } from "vue";

/** Tiny component to encapsulate showing an abbreviated metric value or string value,
 * with a popover for the complete value. If both string and metric value are given, it will
 * show string value over the metric value.
 *
 * Usage:
 *   <ValueBox
 *      :metricValue="bin.min"
 *      popover-label="Bin minimum:"
 *      :value-formatter="navStore.metric().valueFormatter" />
 * or
 * <ValueBox
 *      :stringValue="bin.min"
 *      popover-label="Bin minimum:" />
 */

export type ValueBoxProps = {
  /** The value to be shown. */
  metricValue?: number | null | undefined;
  /** Text to be shown */
  stringValue?: string | null | undefined;
  /** What to show if the metricValue is not a number. Defaults to "N/A". */
  labelIfBlank?: string;
  /** How the value will be formatted in the element.
   *  Defaults to toString(). */
  valueFormatter?: (n: number) => string;
  /** The label to show before the metric in the popover.
   *  Defaults to empty. */
  popoverPrefix?: string;
  /** How the value will be formatted in the popover.
   *  Defaults to using `toString()`, i.e., no abbreviation. */
  popoverValueFormatter?: (n: number) => string;
};

const {
  metricValue,
  stringValue,
  labelIfBlank = "N/A",
  valueFormatter = (d) => d.toString(),
  popoverPrefix = "",
  popoverValueFormatter = (d) => d.toString(),
} = defineProps<ValueBoxProps>();

const tooltipText = computed(() => {
  if (stringValue) {
    return `${popoverPrefix} ${stringValue}`;
  } else if (_.isNil(metricValue)) {
    return `${popoverPrefix} ${labelIfBlank}`;
  } else {
    return `${popoverPrefix} ${popoverValueFormatter(metricValue)}`;
  }
});

const content = computed(() => {
  if (stringValue) {
    return stringValue;
  } else if (valueFormatter) {
    if (_.isNumber(metricValue)) {
      return valueFormatter(metricValue);
    }
  }
  return labelIfBlank;
});
</script>

<template>
  <SimpleTooltip class="value-box" :content="content" :text="tooltipText" minWidth="15em" />
</template>

<style scoped>
.value-box {
  display: inline-block;
  position: relative; /* Float the tooltip, below. */
  border: none;
  border-radius: 0;
  font-family: var(--bs-font-monospace) !important;
  padding: 0 0.25em;
  margin: 2px;
  text-align: end;
  cursor: default;
  background-color: var(--brand-cool-gray-10);
}
</style>
