<script setup lang="ts">
import CommonText from "@/components/common/CommonText.vue";
import PaymentRateTable from "@/components/common/PaymentRateTable.vue";
import ValueBox from "@/components/common/ValueBox.vue";
import { useProjectStore } from "@/stores/project";
import { LOADING_STRING, LOCAL_STORAGE_STEPS_SHOWN, publicPath } from "@/util/Consts";
import {
  compareWords,
  payoutFormatter,
  payoutPercentFormatter,
  tooltipFormatter,
} from "@/util/formatters";
import { key2outcome } from "@/util/metricUtils";
import { computePayoutStatistics } from "@/util/projectUtils";
import { useLocalStorage } from "@vueuse/core";
import _ from "lodash";
import { computed, ref } from "vue";

const projectStore = useProjectStore();
const project = computed(() => projectStore.project());

const stats = computed(() => computePayoutStatistics(project.value));
const outcome = computed(() => key2outcome(stats.value?.outcomeKey ?? "soc"));

const stepsShown = useLocalStorage(LOCAL_STORAGE_STEPS_SHOWN, false);

const metricLabel = computed(() =>
  projectStore.dataIsReady() && outcome.value ? outcome.value.metric.shortLabel : LOADING_STRING
);

const metricValueFormatter = computed(() => outcome.value.metric.valueFormatter);

const cardMap = ["baseline", "trend", "dnd", "payout", "summary"];

const currentIndex = ref(0);

const prevCard = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--;
  }
};

const nextCard = () => {
  if (currentIndex.value < cardMap.length) {
    currentIndex.value++;
  }
};

const skipTo = (index: number) => {
  currentIndex.value = index;
};
</script>

<template>
  <section class="card payout-dashboard">
    <h3 class="card-header">
      Payout Dashboard
      <template v-if="stats">
        ({{ stats.period === "baseline" ? stats.period : "as of month " + stats.period }})
      </template>
    </h3>
    <section class="card-body payout-dashboard-body">
      <div class="big-num-area">
        <div>
          Target Performance
          <ValueBox
            class="explanation-number target-performance"
            :metricValue="stats?.targetRate"
            :valueFormatter="payoutPercentFormatter" />
        </div>
        <div>
          Project Performance
          <ValueBox
            class="explanation-number actual-performance"
            :metricValue="stats?.did"
            :valueFormatter="payoutPercentFormatter" />
        </div>
        <div>
          Maximum Payout
          <ValueBox
            class="explanation-number max-payout"
            :metricValue="stats?.maximumPayout"
            :valueFormatter="payoutFormatter" />
        </div>
        <div>
          Predicted Payout
          <ValueBox
            class="explanation-number predicted-payout"
            :metricValue="stats?.estimatedPayout"
            :valueFormatter="payoutFormatter" />
        </div>
      </div>
      <div class="payout-wizard d-flex flex-column">
        <section v-if="!stats">
          A payout preview is not available as the project does not yet have enough measurements to
          compute it.
        </section>
        <template v-else>
          <section v-if="stepsShown" class="index-card">
            <div v-if="cardMap[currentIndex] === 'baseline'">
              <h6>Step {{ currentIndex + 1 }}: Baselines</h6>
              <div class="d-flex justify-content-between">
                <div class="text-center mx-3">
                  <img
                    v-if="stats"
                    :src="publicPath(`baseline-${stats.outcomeKey}.png`)"
                    class="img-fluid mb-2"
                    width="180"
                    height="180"
                    alt="Baseline Map" />
                  <p>
                    The national baseline at the start of the performance period was
                    <ValueBox
                      :metric-value="stats.nationalBaseline"
                      :valueFormatter="metricValueFormatter"
                      :popoverPrefix="`National baseline ${outcome.typeAndDenom}: `" />
                    {{ outcome.typeAndDenom }}.
                  </p>
                </div>
                <div class="text-center mx-3">
                  <img
                    :src="publicPath(`project-${stats.outcomeKey}.png`)"
                    class="img-fluid mb-2"
                    width="180"
                    height="180"
                    alt="Project Map" />
                  <p>
                    Your project geography baseline at the start of the performance period was
                    <ValueBox
                      :metric-value="stats.projectBaseline"
                      :valueFormatter="metricValueFormatter"
                      :popoverPrefix="`Project geography baseline ${outcome.typeAndDenom}: `" />
                    {{ outcome.typeAndDenom }}.
                  </p>
                </div>
              </div>
              <p class="p-2 text-center">
                How did we create the summary? Click below for a detailed walk through.
              </p>
            </div>

            <div v-if="cardMap[currentIndex] === 'trend'">
              <h6>Step {{ currentIndex + 1 }}: Trend from Baselines</h6>
              <p
                v-if="
                  _.isNil(stats.nationalBaseline) ||
                  _.isNil(stats.nationalRate) ||
                  _.isNil(stats.projectRate) ||
                  stats.period === 'baseline'
                ">
                A trend cannot be shown, as your project does not yet have enough data.
              </p>
              <template v-else>
                <div class="d-grid cols-2-equal">
                  <div class="text-center mx-3">
                    <img
                      :src="publicPath('placeholder.png')"
                      class="img-fluid mb-2"
                      width="180"
                      height="180"
                      alt="Placeholder" />
                    <p>
                      At {{ stats.period }} months, the national rate
                      {{ compareWords(-stats.nationalRate, "increasedOrDecreased") }}
                      from
                      <ValueBox
                        :metric-value="stats.nationalBaseline"
                        :valueFormatter="metricValueFormatter"
                        :popoverPrefix="`National baseline`" />
                      to
                      <ValueBox
                        :metric-value="stats.nationalCurrent"
                        :valueFormatter="metricValueFormatter"
                        :popoverPrefix="`At ${stats.period} months, the national rate: `" />
                      {{ metricLabel }}.
                    </p>
                    <p>
                      This is a
                      <ValueBox
                        :metricValue="Math.abs(stats.nationalRate)"
                        :valueFormatter="payoutPercentFormatter"
                        :popoverPrefix="`Calculation: (${stats.nationalCurrent} minus ${stats.nationalBaseline}) over ${stats.nationalBaseline} =  `"
                        :popoverValueFormatter="tooltipFormatter" />
                      {{ compareWords(stats.nationalRate, "improvementOrWorsening") }}
                      in the {{ outcome.rateLong }}.
                    </p>
                  </div>

                  <div class="text-center mx-3">
                    <img
                      :src="publicPath('placeholder.png')"
                      class="img-fluid mb-2"
                      width="180"
                      height="180"
                      alt="Placeholder" />
                    <p>
                      At {{ stats.period }} months, your project geography rate
                      {{ compareWords(-stats.projectRate, "increasedOrDecreased") }}
                      from
                      <ValueBox
                        :metricValue="stats.projectBaseline"
                        :valueFormatter="metricValueFormatter"
                        :popoverPrefix="`Project geography baseline`" />
                      to
                      <ValueBox
                        :metricValue="stats.projectCurrent"
                        :valueFormatter="metricValueFormatter"
                        :popoverPrefix="`At ${stats.period} months, the project geography rate: `" />
                      {{ metricLabel }}.
                    </p>
                    <p>
                      This is a
                      <ValueBox
                        :metricValue="Math.abs(stats.projectRate)"
                        :valueFormatter="payoutPercentFormatter"
                        :popoverPrefix="`Calculation: (${stats.projectCurrent}-${stats.projectBaseline})/${stats.projectBaseline} =  `"
                        :popoverValueFormatter="tooltipFormatter" />
                      {{ compareWords(stats.projectRate, "improvementOrWorsening") }}
                      in the {{ outcome.rateLong }}.
                    </p>
                  </div>
                </div>
              </template>
            </div>

            <div v-if="cardMap[currentIndex] === 'dnd'" class="text-center">
              <h6>Step {{ currentIndex + 1 }}: Project Performance</h6>

              <p>
                The project performance is computed by subtracting the national rate change from the
                rate change in your project geography.
              </p>
              <p
                v-if="
                  _.isNil(stats.projectRate) ||
                  _.isNil(stats.nationalRate) ||
                  _.isNil(stats.did) ||
                  stats.period === 'baseline'
                ">
                Project performance calculations could not be performed as your project does not
                have enough data yet.
              </p>
              <template v-else>
                <p>
                  <ValueBox
                    :metricValue="stats.projectRate"
                    :valueFormatter="payoutPercentFormatter"
                    :popoverPrefix="`Project geography specific % change: `"
                    :popoverValueFormatter="tooltipFormatter" />
                  minus
                  <ValueBox
                    :metricValue="stats.nationalRate"
                    :valueFormatter="payoutPercentFormatter"
                    :popoverPrefix="`National % change: `"
                    :popoverValueFormatter="tooltipFormatter" />
                  equals
                  <ValueBox
                    :metricValue="stats.did"
                    :valueFormatter="payoutPercentFormatter"
                    :popoverPrefix="`Project performance formula: Geography specific % change minus National % change = `"
                    :popoverValueFormatter="tooltipFormatter" />
                </p>
                <img
                  :src="publicPath('placeholder.png')"
                  class="img-fluid mb-2"
                  width="180"
                  height="180"
                  alt="" />
              </template>
            </div>

            <div v-if="cardMap[currentIndex] === 'payout'">
              <h6>Step {{ currentIndex + 1 }}: Payout calculations</h6>
              <p v-if="_.isNil(stats.period) || _.isNil(stats.did) || stats.period === 'baseline'">
                Payout calculations could not be performed as your project does not have enough data
                yet.
              </p>
              <template v-else>
                <p>
                  The target {{ outcome.rate }} change for month {{ stats.period }} was
                  <ValueBox
                    :metricValue="stats.targetRate ?? 0"
                    :valueFormatter="payoutPercentFormatter"
                    :popoverPrefix="`Target Rate for Month ${stats.period}: `" />
                  relative to the national change. Your project performance was
                  <ValueBox
                    :metricValue="stats ? stats.did : undefined"
                    :valueFormatter="payoutPercentFormatter"
                    popoverPrefix="Project Performance: "
                    :popoverValueFormatter="tooltipFormatter" />
                  relative to the national change.
                </p>
                <p v-if="_.isNil(stats.estimatedPayout)">
                  An estimation of payout could not be computed, due to a lack of data.
                </p>
                <p v-else>
                  You will therefore receive
                  {{
                    stats.estimatedPayout === stats.maximumPayout
                      ? "the maximum payout of"
                      : stats.estimatedPayout > 0
                        ? "the partial payout of"
                        : "no payout."
                  }}
                  <ValueBox
                    v-if="stats.estimatedPayout > 0"
                    :metricValue="stats.estimatedPayout"
                    :valueFormatter="payoutFormatter"
                    :popoverPrefix="'Payout amount to receive: $'"
                    :popoverValueFormatter="payoutFormatter" />
                </p>
                <!-- FIXME: for now adding back in caption until we can update numbers -->
                <PaymentRateTable showCaption :outcomeKey="stats.outcomeKey" />
              </template>
            </div>

            <div v-if="cardMap[currentIndex] === 'summary'">
              <h6>Payout Calculation Summary</h6>
              <p
                v-if="
                  _.isNil(stats.nationalBaseline) ||
                  _.isNil(stats.projectBaseline) ||
                  _.isNil(stats.nationalCurrent) ||
                  _.isNil(stats.projectCurrent) ||
                  stats.period === 'baseline'
                ">
                Payout calculations were not be performed as your project does not have enough data
                yet.
              </p>
              <ol v-else>
                <li>Baseline rates of {{ metricLabel }}:</li>
                <ol type="a">
                  <li>
                    National:
                    <CommonText
                      :metric-value="stats.nationalBaseline"
                      :value-formatter="metricValueFormatter"
                      :outcome-key="outcome.key"
                      popover-prefix="The national baseline measurement for this project: "
                      prefix-text="National:" />
                  </li>
                  <li>
                    Project Geography:
                    <CommonText
                      :metric-value="stats.projectBaseline"
                      :value-formatter="metricValueFormatter"
                      :outcome-key="outcome.key"
                      popover-prefix="The project geography baseline measurement: "
                      prefix-text="Geography specific:" />
                  </li>
                </ol>
                <template
                  v-if="
                    !_.isNil(stats.period) &&
                    !_.isNil(stats.nationalRate) &&
                    !_.isNil(stats.projectRate)
                  ">
                  <li>At {{ stats.period }} months:</li>
                  <ol type="a">
                    <li>
                      National:
                      <CommonText
                        :metric-value="stats.nationalCurrent"
                        :value-formatter="metricValueFormatter"
                        :outcome-key="outcome.key"
                        :popover-prefix="`THe national measurement at ${stats.period} months: `"
                        prefix-text="National:" />
                      (
                      <ValueBox
                        :metricValue="Math.abs(stats.nationalRate)"
                        :valueFormatter="payoutPercentFormatter"
                        :popoverPrefix="`(National measurement at ${stats.period} months - national measurement at baseline)/ national measurement at baseline: `"
                        :popoverValueFormatter="tooltipFormatter" />
                      {{ compareWords(-stats.nationalRate, "increaseOrDecrease") }}, or
                      {{ compareWords(stats.nationalRate, "improvementOrWorsening") }}
                      )
                    </li>
                    <li>
                      Project Geography:
                      <CommonText
                        :metric-value="stats.projectCurrent"
                        :value-formatter="metricValueFormatter"
                        :outcome-key="outcome.key"
                        :popover-prefix="`project geography measurement at ${stats.period} months`"
                        prefix-text="Geography specific:" />
                      (
                      <ValueBox
                        :metricValue="Math.abs(stats.projectRate)"
                        :valueFormatter="payoutPercentFormatter"
                        :popoverPrefix="`(Project geography measurement at ${stats.period} months - project geography measurement at baseline)/ project geography measurement at baseline: `"
                        :popoverValueFormatter="tooltipFormatter" />

                      {{ compareWords(-stats.projectRate, "increaseOrDecrease") }}, or
                      {{ compareWords(stats.projectRate, "improvementOrWorsening") }}

                      )
                    </li>
                  </ol>
                </template>
                <li>Project Performance:</li>
                <p
                  v-if="
                    _.isNil(stats.nationalBaseline) ||
                    _.isNil(stats.nationalRate) ||
                    _.isNil(stats.projectRate) ||
                    _.isNil(stats.did)
                  ">
                  A trend cannot be shown, as your project does not yet have enough data.
                </p>

                <ol v-else type="a">
                  <li>
                    The national {{ outcome.rate }} was
                    {{ compareWords(stats.nationalRate, "improvedByOrWorseBy") }}
                    <ValueBox
                      :metricValue="Math.abs(stats.nationalRate)"
                      :valueFormatter="payoutPercentFormatter"
                      :popoverPrefix="`(National measurement at ${stats.period} months - national measurement at baseline)/ national measurement at baseline: `"
                      :popoverValueFormatter="tooltipFormatter" />
                    and your geography-specific {{ outcome.rate }} was
                    {{ compareWords(stats.projectRate, "improvedByOrWorseBy") }}
                    <ValueBox
                      :metricValue="Math.abs(stats.projectRate)"
                      :valueFormatter="payoutPercentFormatter"
                      :popoverPrefix="`(Project geography measurement at ${stats.period} months - project geography measurement at baseline) / project geography measurement at baseline: `"
                      :popoverValueFormatter="tooltipFormatter" />
                  </li>
                  <li>
                    Your project performance was
                    <ValueBox
                      :metricValue="stats.did"
                      :valueFormatter="payoutPercentFormatter"
                      :popoverPrefix="`Project Performance: ${tooltipFormatter(stats.projectRate)} - ${tooltipFormatter(stats.nationalRate)} = `"
                      :popoverValueFormatter="tooltipFormatter" />
                    relative to the national change
                  </li>
                </ol>

                <li>Payment:</li>
                <p
                  v-if="
                    _.isNil(stats.nationalBaseline) ||
                    _.isNil(stats.nationalRate) ||
                    _.isNil(stats.projectRate) ||
                    _.isNil(stats.did)
                  ">
                  Payment data not shown, as your project does not yet have enough data.
                </p>
                <ol v-else type="a">
                  <li>
                    The target {{ outcome.rate }} change for month
                    {{ stats.period }}
                    was
                    <ValueBox
                      :metricValue="stats.targetRate ?? 0"
                      percentage
                      :valueFormatter="payoutPercentFormatter"
                      :popoverPrefix="`Target Rate for Month ${stats.period}: `"
                      :popoverValueFormatter="payoutPercentFormatter" />
                    relative to the national change
                  </li>
                  <li>
                    Your project performance of
                    <ValueBox
                      :metricValue="stats.did"
                      :valueFormatter="payoutPercentFormatter"
                      :popoverPrefix="`Net change value: `"
                      :popoverValueFormatter="tooltipFormatter" />
                    relative to the national change is
                    {{
                      compareWords(
                        stats.payoutFraction ?? stats.projectRate - stats.targetRate,
                        "greaterOrLess"
                      )
                    }}
                    than the target performance of
                    <ValueBox
                      :metricValue="stats.targetRate ?? 0"
                      :percentage="true"
                      :valueFormatter="payoutPercentFormatter"
                      :popoverPrefix="`Target Rate for Month ${stats.period}: `"
                      :popoverValueFormatter="payoutPercentFormatter" />
                  </li>
                  <li v-if="!_.isNil(stats.estimatedPayout)">
                    You will receive
                    {{
                      stats.estimatedPayout === stats.maximumPayout
                        ? "the maximum payout of"
                        : stats.estimatedPayout > 0
                          ? "a partial payout of"
                          : "no payout."
                    }}
                    <ValueBox
                      v-if="stats.estimatedPayout > 0"
                      :metricValue="stats.estimatedPayout"
                      :valueFormatter="payoutFormatter"
                      :popoverPrefix="'Payout amount to receive:'"
                      :popoverValueFormatter="payoutFormatter" />
                  </li>
                </ol>
              </ol>
            </div>

            <nav class="pagination-buttons" aria-label="Payout calculation navigation">
              <ul class="pagination pagination-sm">
                <li class="page-item" :class="{ disabled: currentIndex === 0 }">
                  <button class="page-link" title="Click for back" @click="prevCard">Back</button>
                </li>
                <li
                  v-for="(_card, index) in cardMap"
                  :key="index"
                  class="page-item"
                  :class="{ active: currentIndex === index }">
                  <button class="page-link" title="Skip to page" @click="skipTo(index)">
                    {{ index + 1 }}
                  </button>
                </li>
                <li class="page-item" :class="{ disabled: currentIndex === cardMap.length - 1 }">
                  <button class="page-link" title="Click for next" @click="nextCard">Next</button>
                </li>
              </ul>
            </nav>
          </section>
          <button
            aria-controls="steps-selection"
            class="btn btn-secondary btn-sm flex-1"
            @click="stepsShown = !stepsShown">
            <i :class="stepsShown ? 'bi-chevron-double-up' : 'bi-chevron-double-down'"></i>
            Calculation Steps
          </button>
        </template>
      </div>
    </section>
  </section>
</template>

<style scoped>
.big-num-area {
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  flex-wrap: nowrap;
  gap: 0.5rem 1rem;
  min-width: min-content;
  padding-bottom: 2rem;
  div {
    display: flex;
    align-items: center;
    font-size: clamp(0.75rem, 1.2cqw, 1.25rem);
    flex-direction: column;
    gap: 0.5rem;
    white-space: nowrap;
  }
  .value-box {
    width: 7rem;
  }
}

.explanation-number {
  background: white;
  border: 6px solid transparent;
  box-sizing: border-box;
  font-family: var(--bs-font-monospace);
  font-size: var(--bs-h4-font-size);
  padding: 0.25rem 0.5rem;
  text-align: center;
  white-space: nowrap;

  &.target-performance {
    border-color: var(--brand-blue-dark);
    color: var(--brand-blue-dark);
  }
  &.actual-performance {
    background-color: var(--brand-blue-dark);
    border-color: var(--brand-blue-dark);
    color: var(--brand-cool-gray-0);
  }
  &.max-payout {
    border-color: var(--brand-turquoise-dark);
  }
  &.predicted-payout {
    background-color: var(--brand-turquoise-dark);
    border-color: var(--brand-turquoise-dark);
    color: var(--brand-cool-gray-0);
  }
}

.reduction-explanation-payout {
  grid-area: reduction-explanation-payout;
  padding: 0.5rem;
}

.payout-wizard {
  font-size: 0.875rem;
  grid-column: span 2;
}
.index-card {
  align-items: center;
  background-color: var(--brand-cool-gray-5);
  border: 1px solid var(--bs-border-color);
  display: flex;
  flex-direction: column;
  max-width: 100%;
  overflow-x: auto;
  padding: 1rem;
}
.cols-2-equal {
  grid-template-columns: 1fr 1fr;
}
h6 {
  font-weight: bold;
  margin-bottom: 1rem;
  text-align: center;
}
</style>
