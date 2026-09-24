<script setup lang="ts">
import AreaMap from "@/components/map/AreaMap.vue";
import { useDataStore } from "@/stores/data";
import { useNavigationStore } from "@/stores/nav";
import { useProjectStore } from "@/stores/project";
import { useSelectionStore } from "@/stores/selection";
import { type AreaShapeProps } from "@/types";
import { cyanToPink10, MISSING_COLOR, MISSING_INDEX, redToBlue21 } from "@/util/colorUtils";
import { areaStyleBase, areaStyleIgnored } from "@/util/mapUtils";
import { normalizeDiD } from "@/util/metricUtils";
import _ from "lodash";
import { computed } from "vue";
import { computePayoutStatistics } from "../../util/projectUtils";

const projectStore = useProjectStore();
const project = computed(() => projectStore.project());

const geoStyler = computed<L.StyleFunction<AreaShapeProps>>(() => {
  const dataStore = useDataStore();
  const navStore = useNavigationStore();
  const selStore = useSelectionStore();
  const projectStore = useProjectStore();
  const project = projectStore.project();

  if (!project) {
    return () => areaStyleIgnored;
  }

  // Precompute things that we will close over in the closure below.
  const dataFilterKey = navStore.dataFilter().key;
  const dataIsReady = dataStore.dataIsReady(project.outcomeKey);
  const mids = new Set(project.areas);
  const outcomeKey = project.outcomeKey;
  const timeBin = selStore.currentTimeBin;

  if (!dataIsReady || !timeBin) {
    return () => areaStyleIgnored;
  }

  return (feature) => {
    const mid = feature?.properties?.mid;
    if (_.isNil(mid) || !mids.has(mid)) {
      // Only use color for the areas inside the project
      return areaStyleIgnored;
    }

    let color = MISSING_COLOR;
    if (dataFilterKey === "did") {
      const did = computePayoutStatistics(project, timeBin)?.did;
      const normalized = normalizeDiD(did);
      const rank = _.isNil(normalized) ? MISSING_INDEX : _.floor(20 * normalized);
      color = redToBlue21[rank];
    } else {
      const rank =
        dataStore.overviewDatum({
          dataFilterKey,
          mid,
          outcomeKey,
          timeBin,
        })?.bin_rank ?? MISSING_INDEX;
      color = cyanToPink10[rank];
    }

    return {
      ...areaStyleBase,
      color,
      fillColor: color,
    };
  };
});
</script>

<template>
  <AreaMap
    v-if="project"
    :color-ramp="cyanToPink10"
    :geoStyler="geoStyler"
    :outcomeKey="project.outcomeKey"
    hide-selections />
</template>

<style scoped>
.area-map {
  background-color: var(--brand-cool-gray-10);
}
</style>
