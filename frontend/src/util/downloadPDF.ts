import * as pdfMake from "pdfmake/build/pdfmake";
// @ts-ignore
import { vfs } from "@/util/vfs_fonts";

import { useDataStore } from "@/stores/data";
import { useNavigationStore } from "@/stores/nav";
import { useSelectionStore } from "@/stores/selection";
import { SPATIAL_GRANULARITY_DATA } from "@/stores/SPATIAL_GRANULARITY_DATA";
import { areaMetricAverage } from "@/util/metricUtils";
import _ from "lodash";
import { DateTime } from "luxon";

export async function downloadPDF() {
  const selStore = useSelectionStore();
  const navStore = useNavigationStore();
  const dataStore = useDataStore();
  const problem = navStore.outcome().searchProblem;
  const metric = navStore.metric().label;
  const population_target = navStore.outcome().populationTarget.toLocaleString();
  const rateType = navStore.outcome().searchTitle;
  const tableTitle = SPATIAL_GRANULARITY_DATA[navStore.outcome().spatialGranularity].plural;
  const selectedOutcome = navStore.outcome().label;
  const selectionCount = selStore.midSelections.size;
  const dataFilterKey = navStore.dataFilter().key;
  const outcomeKey = navStore.outcome().key;
  const timeBin = selStore.currentTimeBin;

  let population = 0;
  const contiguous = `The selected areas are ${selStore.contiguous ? "" : "not "}contiguous`;
  const nationalAverage = dataStore.nationalAverage({ dataFilterKey, outcomeKey, timeBin });

  const metricBins = dataStore.metricBins({
    dataFilterKey,
    outcomeKey,
    timeBin,
  });

  // Used for the table rows below
  const rankValueFormatter = (rank: number): string => {
    const metricBin = metricBins.find((bin) => bin.rank === rank);
    if (!metricBin) {
      console.error("Couldn't find bin for rank", rank);
      return "no data";
    }
    return metricBin.rank_value;
  };

  // Construct the legend (TODO: Replace this with a version of the MapLegend.vue object)
  const legendRows = [];
  // Format the header for the legend table
  const legendHeader = [
    {
      text: "Legend",
      color: "#052b4e",
      fillColor: "#9BD7EE",
      style: "subheader",
      colSpan: 2,
      alignment: "center",
    },
    {},
  ];
  legendRows.push(legendHeader);
  //Adding rows with legend data
  for (const bin of metricBins) {
    const legendRow = [];
    const rank = bin.rank_value.replace(/ *than national average/i, "");
    legendRow.push({ text: rank });
    legendRow.push({
      text: `${navStore.metric().valueFormatter(bin.min)} to ${navStore.metric().valueFormatter(bin.max)}`,
    });

    legendRows.push(legendRow);
  }

  // Fill the table
  const tableRows = [];
  let tableHeader;
  let numOfColumns; // Number of columns need to be established when designing table
  // Formatting Header row
  // If County format
  if (navStore.outcome().key === "alcohol" || navStore.outcome().key === "opioid") {
    numOfColumns = ["*", 100, 100];
    tableHeader = [
      {
        text: tableTitle,
        style: "subheader",
        fillColor: "#9BD7EE",
        alignment: "center",
        color: "#052b4e",
      },
      {
        text: [
          { text: "Total Population\n", style: "subheader" },
          { text: "(Census Data)", style: ["quote", "small"] },
        ], //TODO: Style does not reflect on pdf
        style: "subheader",
        fillColor: "#9BD7EE",
        alignment: "center",
        color: "#052b4e",
      },
      {
        text: "Rate in comparison to National Average",
        style: "subheader",
        fillColor: "#9BD7EE",
        alignment: "center",
        color: "#052b4e",
      },
    ];
  }
  // Else if Zip3 format
  else {
    numOfColumns = [100, 100, 100, "*"]; //additional column for ZCTA3s
    tableHeader = [
      {
        text: tableTitle,
        style: "subheader",
        fillColor: "#9BD7EE",
        alignment: "center",
        color: "#052b4e",
      },
      {
        text: [
          { text: "Total Population\n", style: "subheader" },
          { text: "(Census Data)", style: ["quote", "small"] },
        ], //TODO: Style does not reflect on pdf
        style: "subheader",
        fillColor: "#9BD7EE",
        alignment: "center",
        color: "#052b4e",
      },
      {
        text: timeBin ? `6-Month Rate for ${timeBin.asString}` : "6-Month Rate",
        style: "subheader",
        fillColor: "#9BD7EE",
        alignment: "center",
        color: "#052b4e",
      },
      {
        text: "Counties overlapping the ZCTA3 Region",
        style: "subheader",
        fillColor: "#9BD7EE",
        alignment: "center",
        color: "#052b4e",
      },
    ];
  }
  tableRows.push(tableHeader);

  const valueFormatter = navStore.metric().valueFormatter;

  // Fill in the table rows for every selection
  for (const mid of selStore.midSelections.values()) {
    const tableRow = [];

    tableRow.push({ text: dataStore.areaName(mid), style: "table" });
    tableRow.push({
      text: dataStore.population(mid).toLocaleString(),
      style: "table",
      alignment: "right",
    });
    population += dataStore.population(mid);

    // If overviewDatum() returns false, we assume we have no data for this MID.
    const datum = dataStore.overviewDatum({ mid, dataFilterKey, outcomeKey, timeBin });
    if (!_.isNil(datum)) {
      const rate = datum.value;

      const rateString = rankValueFormatter(datum.bin_rank!); // (i.e "Higher than national average")
      const slicedRateString = rateString.split(" than ")[0]; // Cropping string to remove "than national average" (i.e we are left with "Higher")
      // If the value is null or otherwise not found, we only print the bin text.
      if (rate === null) {
        tableRow.push({
          text: slicedRateString,
          style: "table",
        });
      }
      // Otherwise, print the formatted value and the bin text in parenthesis.
      else {
        tableRow.push({
          text: `${valueFormatter(rate)}\n(${slicedRateString})`,
          style: "table",
        });
      }
    } else {
      // Final case, if we have no data at all we represent it as such.
      tableRow.push({
        text: "No Data",
        style: "table",
      });
    }

    //If ZIP3 format, add an extra row for the Counties within the ZIP3.
    if (navStore.outcome().spatialGranularity === "ZCTA3") {
      const countyNames = dataStore
        .areaIntersects(mid, "COUNTY")
        .map((m) => dataStore.areaName(m))
        .sort();

      tableRow.push({ text: countyNames.join("; "), style: "table" });
    }
    tableRows.push(tableRow);
  }

  const metricAverage = areaMetricAverage({
    mids: selStore.midSelections,
    dataFilterKey,
    outcomeKey,
    timeBin,
  });

  const docDefinition = {
    content: [
      {
        columns: [
          {
            width: "auto",
            text: [{ text: "Outcome Toolkit\n", style: "header" }],
          },
        ],
      },
      "\n",
      {
        style: "tableExample",
        table: {
          headerRows: 1,
          widths: ["*"],
          body: [
            [
              {
                text: [{ text: "(1) Selected Outcome: " }, { text: selectedOutcome }],
                color: "white",
                fillColor: "#052b4e",
                style: "tableHeader",
              },
            ],
            [
              {
                border: [false, false, false, false],
                fillColor: "#eeeeee",
                text: [
                  { text: "Problem\n", style: "subheader" },
                  { text: problem },
                  "\n",
                  { text: "\nMetric\n", style: "subheader" },
                  { text: metric },
                  { text: "\n6-Month National Average Rate: ", underline: true },
                  {
                    text: nationalAverage?.value
                      ? navStore.metric().valueFormatter(nationalAverage.value)
                      : "n/a",
                  },

                  { text: "\n\nSelection Constraints\n", style: "subheader" },
                  { text: "Applications will be given priority if they cover more than " },
                  { text: population_target },
                  {
                    text: " people, are contiguous, and the outcome rate is worse than the national average.",
                  },
                ],
              },
            ],
          ],
        },
      },
      "\n",
      {
        style: "tableExample",
        table: {
          headerRows: 1,
          widths: ["*"],
          body: [
            [
              {
                text: "(2) Suitability",
                color: "white",
                fillColor: "#052b4e",
                style: "tableHeader",
              },
            ],
            [
              {
                border: [false, false, false, false],
                fillColor: "#eeeeee",
                text: [
                  {
                    text: "Priority will be given to applications where the selected area(s) meet the requirements below. : ",
                  },
                  { text: "\n\nContiguity: ", style: "subheader" },
                  { text: contiguous, italics: "true" },
                  { text: "\nPopulation: ", style: "subheader" },
                  { text: population.toLocaleString(), italics: "true" },
                  {
                    text:
                      " (Threshold is " +
                      population_target.toLocaleString() +
                      " or an entire US State/Territory)\n",
                    style: ["quote", "small"],
                  },
                  { text: rateType + ": ", style: "subheader" },
                  {
                    text:
                      navStore.metric().valueFormatter(metricAverage.value ?? 0) +
                      " (" +
                      rankValueFormatter(metricAverage.bin_rank ?? 0) +
                      ")",
                    italics: "true",
                  },
                  {
                    text: " (Threshold is worse than national average)\n", //TODO: update hardcoded text
                    style: ["quote", "small"],
                  },
                ],
              },
            ],
          ],
        },
      },
      "\n",
      {
        style: "tableExample",
        table: {
          headerRows: 1,
          widths: ["*"],
          body: [
            [
              {
                text: [
                  { text: "(3) Selected " },
                  { text: tableTitle },
                  { text: " for Intervention" },
                ],
                color: "white",
                fillColor: "#052b4e",
                style: "tableHeader",
              },
            ],
            [
              {
                border: [false, false, false, false],
                fillColor: "#eeeeee",
                text: [
                  "Number of ",
                  { text: tableTitle },
                  " Selected: ",
                  { text: selectionCount },
                  "\n\n",
                ],
              },
            ],
          ],
        },
      },
      // "\n",
      // "\n",
      {
        style: "tableExample",
        table: {
          headerRows: 1,
          widths: numOfColumns,
          body: tableRows,
        },
        layout: {
          fillColor: "#eeeeee",
        },
      },
      "\n",
      {
        style: "tableExample",
        table: {
          headerRows: 1,
          widths: ["*", "*"],
          body: legendRows,
        },
        layout: {
          fillColor: "#eeeeee",
        },
      },
    ],
    styles: {
      header: {
        fontSize: 15,
        bold: true,
      },
      link: {
        decoration: "underline" as any,
        color: "#5842d2",
      },
      subheader: {
        fontSize: 13,
        bold: true,
      },
      table: {
        fontSize: 12,
        color: "black",
      },
      tableHeader: {
        bold: true,
        fontSize: 14,
        color: "black",
      },
      quote: {
        italics: true,
      },
      small: {
        fontSize: 10,
      },
    },
    defaultStyle: {
      font: "Roboto",
    },
  };

  pdfMake
    .createPdf(docDefinition, undefined, undefined, vfs)
    .download(`outcome-toolkit-${DateTime.now().toISODate()}.pdf`);
}
