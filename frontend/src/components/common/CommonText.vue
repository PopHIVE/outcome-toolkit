<script setup lang="ts">
/**
 * Tiny util to encapsulate a repeated pattern in the wizard, "initialText [2222] per 10,000 deliveries".
 * Takes all the options of ValueBox, which are used to display the number, plus:
 *  @param outcomeKey which outcome the suffix text should be pulled from and how to format the number.
 *  @param prefixText The text shown before the number.
 */
import { key2outcome } from "@/util/metricUtils";
import ValueBox, { type ValueBoxProps } from "./ValueBox.vue";
import type { OutcomeKeyType } from "../../types";

const props = defineProps<
  ValueBoxProps & {
    initialText?: string;
    outcomeKey: OutcomeKeyType;
    valueFormatter: (n: number) => string;
  }
>();
const { outcomeKey, initialText, valueFormatter, ...valueBoxProps } = props;
</script>

<template>
  <span>
    {{ initialText }}
    <ValueBox v-bind="valueBoxProps" :value-formatter="valueFormatter" />
    {{ key2outcome(outcomeKey).typeAndDenom }}
  </span>
</template>
