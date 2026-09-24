<script lang="ts" setup>
import { graphProps } from "@/components/graph/graphStyling";
import { useDataStore } from "@/stores/data";
import { useNavigationStore } from "@/stores/nav";
import { useProjectStore } from "@/stores/project";
import { useSelectionStore } from "@/stores/selection";
import { type MID } from "@/types";
import { didFormatter } from "@/util/formatters";
import { areaMetricAverage } from "@/util/metricUtils";
import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  SubTitle,
  TimeScale,
  Title,
  Tooltip,
} from "chart.js";
import annotationPlugin from "chartjs-plugin-annotation";
import zoomPlugin from "chartjs-plugin-zoom";
import { computed } from "vue";
import { Line } from "vue-chartjs";
import VErrorBoundary from "vue-error-boundary";
import { computePayoutStatistics } from "../../util/projectUtils";
import _ from "lodash";

const props = defineProps<{
  class?: string;
  mids: Set<MID>;
  isProject?: boolean;
}>();

export type MetricGraphDataType = (number | null)[];

/* NOTE: ChartJS requires explicit registration of the elements you intend to use, or the page will not load. Wonderful DX. */
ChartJS.register(
  CategoryScale,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  SubTitle,
  TimeScale,
  Title,
  Tooltip,
  annotationPlugin,
  zoomPlugin
);

const dataStore = useDataStore();
const selStore = useSelectionStore();
const navStore = useNavigationStore();

// Configuration for the plot itself, incorporating the data sets created above.
const chartProps = computed(() => {
  const currentTimeBin = selStore.currentTimeBin;
  const filter = navStore.dataFilter();

  const dataFilterKey = filter.key;
  const isDID = props.isProject && filter?.key === "did";
  const outcome = navStore.outcome();
  const { key, metric } = outcome;
  const projectStore = useProjectStore();
  const project = projectStore.project();
  const outcomeKey = (props.isProject ? project?.outcomeKey : key) ?? "soc";

  const metricData: MetricGraphDataType = [];
  const nationalData: MetricGraphDataType = [];

  const timeBins = dataStore.timeBins({ metricKey: metric.key });

  const labels = timeBins.map((b) => b.endDate.toFormat("MMM yyyy"));
  // Need to sum across MIDs for each time bin. Metric is, at least, constant.
  timeBins.forEach((timeBin) => {
    if (isDID) {
      const y = computePayoutStatistics(project, timeBin)?.did;
      // HACK: temp fix to display did data in graph as % to match wizard, ex: -7.62% instead of -0.0762%
      // TODO: Potentially rip out * 100 during ticket OUTCOME_TOOLKIT-591
      metricData.push(!_.isNil(y) ? y * 100 : null);
    } else {
      // HACK: temp fix to display cardio data in graph as % to match wizard, ex: -7.62% instead of -0.0762%
      const nationalY =
        dataStore.nationalAverage({
          dataFilterKey,
          outcomeKey,
          timeBin,
        })?.value ?? null;
      // TODO: rip out * 100 during ticket OUTCOME_TOOLKIT-591
      let nationalYVal = nationalY ?? null;
      if (outcomeKey === "cardio") {
        nationalYVal = !_.isNil(nationalY) ? nationalY * 100 : null;
      }
      nationalData.push(nationalYVal);
      const y = areaMetricAverage({ dataFilterKey, mids: props.mids, outcomeKey, timeBin }).value;
      let yVal = y ?? null;
      if (outcomeKey === "cardio") {
        yVal = !_.isNil(y) ? y * 100 : null;
      }
      metricData.push(yVal);
    }
  });

  return graphProps({
    currentTimeBin,
    isDID,
    outcomeKey,
    labels,
    metricData,
    metricLabel: props.isProject ? "Project geography" : "Selected geography",
    nationalData,
    title: isDID ? "Project Performance (% change relative to national change)" : metric.shortLabel,
    valueFormatter: isDID ? didFormatter : metric.valueFormatter,
  });
});
</script>

<template>
  <VErrorBoundary stop-propagation>
    <div class="graph-parent" :class="props.class">
      <Line :data="chartProps.data" :options="chartProps.options" />
    </div>
  </VErrorBoundary>
</template>

<style scoped>
.graph-parent {
  /* NOTE: This parent must be relative. See <https://www.chartjs.org/docs/latest/configuration/responsive.html> */
  position: relative;
  width: 90%;
  height: min(90%, 25vh);
  margin: auto;
  &.expanded {
    height: min(90%, calc(100vh - 16rem));
  }
}
</style>
