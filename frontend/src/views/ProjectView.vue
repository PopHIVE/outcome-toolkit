<script setup lang="ts">
import PayoutDashboard from "@/components/project/PayoutDashboard.vue";
import PayoutProgress from "@/components/project/PayoutProgress.vue";
import ProjectInfo from "@/components/project/ProjectInfo.vue";
import ProjectMap from "@/components/project/ProjectMap.vue";
import MetricHistoryGraph from "@/components/graph/MetricHistoryGraph.vue";
import { useProjectStore } from "@/stores/project";
import { computed } from "vue";
import DebugProjectChooser from "@/components/project/DebugProjectChooser.vue";

const projectStore = useProjectStore();
const project = computed(() => projectStore.project());
const mids = computed(() => new Set(project.value?.areas ?? []));
</script>

<template>
  <section v-if="!project" class="project-page card m-2 text-danger">
    No project selected. Are you logged in?
  </section>
  <section v-else class="project-page card-body">
    <DebugProjectChooser />
    <ProjectInfo class="span-all" />
    <ProjectMap />
    <MetricHistoryGraph class="expanded" :mids="mids" is-project />

    <PayoutDashboard />
    <PayoutProgress />
    <footer class="page-footer span-all">
      <p>
        In accordance with Article 7, Data Rights, of the applicable Other Transaction Agreement,
        the Government has the right to use, modify, reproduce, perform, display, release, or
        disclose in whole or in part and in any manner, for Government purposes only, the displayed
        Performance Data and to have or permit others to do so for Government purposes only.
      </p>
    </footer>
  </section>
</template>

<style scoped>
/* Two-column layout for wide screens */
.project-page {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto 1fr 1fr auto;
  height: 90vh;
}

@media (max-width: 64rem) {
  .project-page {
    grid-template-columns: 1fr;
  }
}

.project-map {
  min-height: 30rem;
}

.span-all {
  grid-column: 1 / -1;
}

.page-footer {
  font-size: 80%;
  margin: auto;
  padding: 0.5rem 1rem;
  text-align: center;
  text-wrap: balance;

  p {
    margin: 0;
  }

  p + p {
    margin-top: 0.5em;
  }
}
</style>
