import { useDataStore } from "@/stores/data";
import { useNavigationStore } from "@/stores/nav";
import { useSelectionStore } from "@/stores/selection";
import { areaMetricAverage } from "@/util/metricUtils";
import { stackDemographics } from "@/util/stackDemographics";

import _ from "lodash";

import { DateTime } from "luxon";

export async function createCSV() {
  const dataStore = useDataStore();
  const navStore = useNavigationStore();
  const selStore = useSelectionStore();

  const dataFilterKey = navStore.dataFilter().key;
  const outcome = navStore.outcome();
  const outcomeKey = navStore.outcome().key;
  const timeBin = selStore.currentTimeBin;

  const mids = [...selStore.midSelections];

  // Create CSV Header row
  const headerRow = [
    "MID",
    "LABEL",
    "POPULATION",
    '"' + "Range for " + outcome.metric.label + '"',
    "Adjacent Areas",
  ];

  // contains totals for selection
  const ageDemos = stackDemographics("age");
  const reDemos = stackDemographics("re");
  const incomeDemos = stackDemographics("income");

  // information stats for totals row
  const totalPopulation = _.sumBy([...selStore.midSelections], (mid) => dataStore.population(mid));
  // TODO: currently has problems with non overlapping bins
  const totalRange = areaMetricAverage({
    mids: selStore.midSelections,
    dataFilterKey,
    outcomeKey,
    timeBin,
  }).bin_rank;

  const totalBin = dataStore.metricBinByRank({
    metricRank: totalRange,
    dataFilterKey,
    outcomeKey,
    timeBin,
  });
  let totalRangeString;

  if (totalBin) {
    const totalBinMin = outcome.metric.valueFormatter(totalBin.min);
    const totalBinMax = outcome.metric.valueFormatter(totalBin.max);
    totalRangeString = `${totalBinMin} to ${totalBinMax} ${totalBin?.rank_value}`;
  } else {
    // Will appear if areaMetricAverage has issue with non overlapping bins
    totalRangeString = "Cannot Calculate Average";
  }

  const totalContiguity = selStore.contiguous ? "All Areas Adjacent" : "Not Adjacent";

  const totalsRow = ["TOTAL", "SUMMARY", totalPopulation, totalRangeString, totalContiguity];

  for (const demo in ageDemos) {
    headerRow.push('"' + "Total Population - " + ageDemos[demo].displayName + '"');
    totalsRow.push(ageDemos[demo].value);
  }

  for (const demo in reDemos) {
    headerRow.push('"' + "Total Population - " + reDemos[demo].displayName + '"');
    totalsRow.push(reDemos[demo].value);
  }

  for (const demo in incomeDemos) {
    // can potentially exclude income since it doesn't come from census data
    headerRow.push('"' + "Total Population - " + incomeDemos[demo].displayName + '"');
    totalsRow.push(incomeDemos[demo].value);
  }

  // data rows for the current selection
  const dataRows = [];

  // MID, area text name, pop, range of rates
  for (const index in mids) {
    const currentRow = [];
    currentRow.push(mids[index]);
    currentRow.push('"' + dataStore.areaName(mids[index]) + '"');
    currentRow.push(dataStore.population(mids[index]));

    const binRank = dataStore.overviewDatum({
      mid: mids[index],
      dataFilterKey,
      outcomeKey,
      timeBin,
    })?.bin_rank;
    const metricBin = dataStore.metricBinByRank({
      metricRank: binRank,
      dataFilterKey,
      outcomeKey,
      timeBin,
    });
    let rateString;
    if (metricBin) {
      const min = outcome.metric.valueFormatter(metricBin.min);
      const max = outcome.metric.valueFormatter(metricBin.max);
      rateString = `${min} to ${max} ${metricBin?.rank_value}`;
    } else {
      rateString = "No Data";
    }

    currentRow.push(rateString);

    //get each demographic
    const areaDemos = dataStore.areaDemographics[mids[index]];
    //adjacency
    currentRow.push('"' + areaDemos["adjacency"]?.toString() + '"');
    for (const demo in ageDemos) {
      currentRow.push(areaDemos[ageDemos[demo].label]);
    }

    for (const demo in reDemos) {
      currentRow.push(areaDemos[reDemos[demo].label]);
    }

    for (const demo in incomeDemos) {
      currentRow.push(areaDemos[incomeDemos[demo].label]);
    }

    dataRows.push(currentRow);
  }

  const dataList = [headerRow, totalsRow, ...dataRows];

  // Create csv strings
  const csv = dataList.map((row) => row.join(",")).join("\n");
  // create blob and blob url
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8," });
  const objUrl = window.URL.createObjectURL(blob);

  // fake link to download
  const downloadLink = document.createElement("a");
  downloadLink.href = objUrl;
  // rename file for ISO date format
  downloadLink.download = `outcome-toolkit-${DateTime.now().toISODate()}.csv`;
  downloadLink.click();

  // cleanup
  downloadLink.remove();
  URL.revokeObjectURL(objUrl);
}
