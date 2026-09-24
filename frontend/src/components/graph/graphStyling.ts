import type { MetricGraphDataType } from "@/components/graph/MetricHistoryGraph.vue";
import { type OutcomeType } from "@/stores/OUTCOME_DATA";
import type { OutcomeKeyType, TimeBin } from "@/types";
import {
  NATIONAL_COLOR,
  NATIONAL_COLOR_PALE,
  SELECTED_COLOR,
  SELECTED_COLOR_FILL,
  SELECTED_COLOR_PALE,
} from "@/util/colorUtils";
import { MONTHS_OF_UNCERTAINTY } from "@/util/Consts";
import type { ChartDataset } from "chart.js";
import _ from "lodash";
import { DateTime } from "luxon";
import type { ChartProps } from "vue-chartjs";

type MetricGraphDataset = ChartDataset<"line", MetricGraphDataType>;

// NOTE: Canvas (which is what ChartJS uses) cannot find CSS vars, so we spell colors out explicitly here
export const RootSeriesStyle: Partial<MetricGraphDataset> = {
  borderWidth: 2,
  clip: 4, // Give indication there is more data off screen
  pointBorderWidth: 1,
  pointHoverRadius: 5,
  pointRadius: 4,
  showLine: true,
  spanGaps: false,
};

// TODO: Conditionalize how many points are shown dashed/faded based on the outcome.
const monthsOfUncertainty = MONTHS_OF_UNCERTAINTY;

export const dateAxisFormat = (t: number | string) =>
  _.isString(t) ? t : DateTime.fromMillis(t).toFormat("M-yyyy");

/** Compute the Graph properties based on what data is selected. */
export function graphProps(props: {
  isDID: boolean;
  outcomeKey: OutcomeKeyType;
  currentTimeBin: TimeBin | undefined;
  metricData: MetricGraphDataType;
  metricLabel: string;
  nationalData: MetricGraphDataType;
  title: string;
  valueFormatter: OutcomeType["metric"]["valueFormatter"];
  labels: string[];
}): ChartProps<"line"> {
  const {
    currentTimeBin,
    isDID,
    outcomeKey,
    labels,
    metricData,
    metricLabel,
    nationalData,
    title,
    valueFormatter,
  } = props;

  const datasets: MetricGraphDataset[] = [];
  if (metricData?.length) {
    if (isDID) {
      datasets.push({
        ...RootSeriesStyle,
        data: metricData,
        label: "Project Performance (% change relative to national change)",
        // Show negative values in another color
        // pointBackgroundColor: (ctx) => (ctx.parsed.y < 0 ? "orange" : "#188478"),
        pointBackgroundColor: "#188478",
        pointStyle: "rect",
        segment: {
          borderColor: "#188478",
        },
      });
    } else {
      const monthOfUncertainty = metricData.length - monthsOfUncertainty;
      // NOTE: intentionally overlap the two series, so line doesn't break
      const certainData = metricData.map((d, idx) => (idx <= monthOfUncertainty ? d : null));
      const uncertainData = metricData.map((d, idx) => (idx >= monthOfUncertainty ? d : null));

      datasets.push({
        ...RootSeriesStyle,
        data: certainData,
        label: metricLabel,

        borderColor: SELECTED_COLOR,
        pointBackgroundColor: SELECTED_COLOR,
        pointBorderColor: SELECTED_COLOR,
        pointStyle: "rect",
      });
      datasets.push({
        ...RootSeriesStyle,
        data: uncertainData,
        label: "Project (provisional data)",

        borderColor: SELECTED_COLOR_PALE,
        borderDash: [4, 4],
        pointBackgroundColor: "white",
        pointBorderColor: SELECTED_COLOR_PALE,
        pointStyle: "rect",
      });
    }
  }
  if (!isDID) {
    const monthOfUncertainty = nationalData.length - monthsOfUncertainty;
    const certainNationalData = nationalData.map((d, idx) =>
      idx <= monthOfUncertainty ? d : null
    );
    const uncertainNationalData = nationalData.map((d, idx) =>
      idx >= monthOfUncertainty ? d : null
    );

    datasets.push({
      ...RootSeriesStyle,
      data: certainNationalData,
      label: "National Average",

      borderColor: NATIONAL_COLOR,
      pointBackgroundColor: NATIONAL_COLOR,
      pointBorderColor: NATIONAL_COLOR,
      pointRadius: 3,
    });
    datasets.push({
      ...RootSeriesStyle,
      data: uncertainNationalData,
      label: "National (provisional data)",

      borderColor: NATIONAL_COLOR_PALE,
      borderDash: [4, 4],
      pointBackgroundColor: "white",
      pointBorderColor: NATIONAL_COLOR_PALE,
      pointRadius: 3,
    });
  }
  const curTime = currentTimeBin?.endDate.toFormat("MMM yyyy");

  return {
    type: "line",
    data: {
      datasets,
      labels,
    },
    options: {
      line: {},
      // Setting this to false lets the graph be as wide as it needs to be
      maintainAspectRatio: false,
      // Adjust graph when user resizes the screen
      responsive: true,
      // Data is sorted and unique
      normalized: true,
      plugins: {
        annotation: {
          annotations: {
            timeBinBox: curTime
              ? {
                  type: "line",
                  borderColor: SELECTED_COLOR_FILL,
                  borderDash: [2, 2],
                  borderWidth: 5,
                  display: true,
                  drawTime: "beforeDraw", // Sink it behind the axes
                  label: {
                    backgroundColor: "#FFFFFFC0",
                    content: ({ chart }) =>
                      chart.width < 300 ? "Map time" : `Shown on map: ${curTime}`,
                    color: SELECTED_COLOR_FILL,
                    display: true,
                    drawTime: "beforeDatasetsDraw",
                    font: {
                      weight: "normal",
                    },
                    position: "start",
                  },
                  xMin: curTime,
                  xMax: curTime,
                }
              : undefined,
          },
        },
        legend: {
          align: "center",
          display: true,
          labels: {
            usePointStyle: true,
          },
        },
        tooltip: {
          backgroundColor: "#d7dee8", // cool-gray-20
          bodyColor: "black",
          borderColor: "black",
          callbacks: {
            /** Alter the label of individual points so we can apply our formatters. */
            // TODO: rip out / 100 during ticket OUTCOME_TOOLKIT-591
            // HACK: for cardio, divide by 100 so value formatter still works -- see MetricHistoryGraph.vue line 105-122
            label: ({ dataset, parsed }) =>
              dataset
                ? ` ${dataset.label}: ${valueFormatter(outcomeKey === "cardio" ? parsed.y / 100 : parsed.y)} ${title}`
                : "",
            /** Show date in before-block, based on datetime of first dataset's value.
             * NOTE: If each data set can have different X coords, this will need to move to the label() callback.
             */
            beforeBody: ([{ label }]) => `As of ${label}:`,
            afterFooter: () =>
              isDID
                ? "Project performance is computed as the difference in differences between project geography and national average."
                : "Note: recent data is incomplete and may be inaccurate.\nThis data is shown in a different style.",
          },
          cornerRadius: 0,
          footerAlign: "center",
          footerColor: "black",
          footerFont: {
            weight: "normal",
            style: "italic",
          },
          mode: "index",
          usePointStyle: true,
          xAlign: "right",
        },
      },
      scales: {
        x: {
          ticks: {
            autoSkip: true,
            autoSkipPadding: 10,
            maxRotation: 0,
          },
        },
        y: {
          title: {
            display: true,
            text: title,
          },
          ticks: {
            autoSkip: true,
            autoSkipPadding: 5,
            // callback: (tickValue) => valueFormatter(Number(tickValue)),
          },
          suggestedMin: isDID ? -1 : 0,
          suggestedMax: isDID ? 1 : undefined,
        },
      },
    },
  };
}
