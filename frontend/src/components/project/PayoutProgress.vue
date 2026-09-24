<script setup lang="ts">
import { useDataStore } from "@/stores/data";
import { useProjectStore } from "@/stores/project";
import { PAYOUT_INTERVALS } from "@/types";
import { payoutFormatter } from "@/util/formatters";
import { computePayoutStatistics } from "@/util/projectUtils";
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  SubTitle,
  Title,
  Tooltip,
  type ChartData,
} from "chart.js";
import annotationPlugin from "chartjs-plugin-annotation";
import zoomPlugin from "chartjs-plugin-zoom";
import _ from "lodash";
import { computed } from "vue";
import { Bar, type ChartProps } from "vue-chartjs";
import VErrorBoundary from "vue-error-boundary";

const PredictedPayoutBarStyle: Partial<ChartData<"bar">["datasets"][number]> = {
  backgroundColor: "#b8b2e4", // Brand Violet-Light
  borderWidth: 4,
  borderColor: "transparent",
};
const ActualPayoutBarStyle: Partial<ChartData<"bar">["datasets"][number]> = {
  backgroundColor: "#5842d2", // Brand Violet
  borderWidth: 4,
  borderColor: "transparent",
};
const MaxPayoutBarStyle: Partial<ChartData<"bar">["datasets"][number]> = {
  backgroundColor: "#f3f5f8", // Cool gray 5
  borderWidth: 4,
  borderColor: "black", // or dark-blue?
};

/* NOTE: ChartJS requires explicit registration of the elements you intend to use, or the page will not load. Wonderful DX. */
ChartJS.register(
  BarElement,
  CategoryScale,
  Legend,
  LinearScale,
  SubTitle,
  Title,
  Tooltip,
  annotationPlugin,
  zoomPlugin
);

/**
 * Data needed:
 *
 * metric data for each period
 * computed ("predicted") payout
 * which time period is currently selected/active
 * the name of the metric and outcome
 */

const dataStore = useDataStore();
const projectStore = useProjectStore();
const project = computed(() => projectStore.project());

const stats = computed(() => computePayoutStatistics(project.value));

const chartProps = computed(() => {
  const intervalsToShow = PAYOUT_INTERVALS.filter((s) => !["total", "baseline"].includes(s));
  const outcomeKey = project?.value?.outcomeKey;

  const out: ChartProps<"bar"> = {
    type: "bar",
    data: {
      datasets: [
        {
          ...MaxPayoutBarStyle,
          data: outcomeKey
            ? intervalsToShow.map((m) => dataStore.targetPayout(outcomeKey, m)?.maximumPayout ?? 0)
            : [],
          label: "Maximum payout",
          order: 2,
        },
      ],
    },
    options: {
      indexAxis: "x",
      responsive: true,
      plugins: {
        tooltip: {
          callbacks: {
            label: ({ dataset, parsed }) => `${dataset.label}: ${payoutFormatter(parsed.y)}`,
          },
          mode: "index",
        },
      },
      scales: {
        x: {
          labels: intervalsToShow.map((k) => `Month ${k}`),
          stacked: true,
        },
        y: {
          ticks: {
            callback: (val) => (_.isNumber(val) ? `$${val / 1e6}M` : val),
          },
          min: 0,
          max: 15_000_000,
        },
      },
    },
  };

  const s = stats.value; // So we can close over it below.

  if (_.isNil(s)) {
    return out;
  }

  const actualPayouts: (number | null)[] = intervalsToShow.map((m) =>
    s.period === m ? null : (s.project.projectMeasurements[m]?.payout ?? 0)
  );
  // Only ever one of these, for the "current" period.
  const predictedPayout: (number | null)[] = intervalsToShow.map((m) =>
    s.period === m ? (s.estimatedPayout ?? null) : null
  );

  out.data.datasets.push({
    ...ActualPayoutBarStyle,
    label: "Actual Payout",
    data: actualPayouts,
    order: 0,
  });
  out.data.datasets.push({
    ...PredictedPayoutBarStyle,
    label: "Predicted Payout",
    data: predictedPayout,
    order: 1,
  });
  return out;
});
</script>

<template>
  <main class="payout-progress card">
    <h3 class="card-header">Payout Progress</h3>
    <VErrorBoundary stop-propagation>
      <div class="payout-progress-chart-parent">
        <Bar :data="chartProps.data" :options="chartProps.options" />
      </div>
    </VErrorBoundary>
  </main>
</template>

<style scoped>
.payout-progress-chart-parent {
  /* NOTE: This parent must be relative. See <https://www.chartjs.org/docs/latest/configuration/responsive.html> */
  position: relative;
  height: 90%;
  width: 90%;
  margin: 5%;
}
</style>
