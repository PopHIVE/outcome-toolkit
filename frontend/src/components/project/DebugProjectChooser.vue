<script lang="ts" setup>
import { useProjectStore } from "@/stores/project";
import { api2Project, APIProjectsRouteSpec, type ProjectID } from "@/types";
import _ from "lodash";
import { onMounted, ref } from "vue";
import { useNavigationStore } from "@/stores/nav";
import { LOADING_STRING } from "@/util/Consts";
import { DateTime } from "luxon";
import { useRoute } from "vue-router";

const route = useRoute();

const navStore = useNavigationStore();
const projectStore = useProjectStore();
// For debug, use user from environment
const prpEmail = import.meta.env.VITE_PRP_EMAIL ?? "";
const headers = new Headers({
  "prp-email": prpEmail,
  "Content-Type": "application/json",
});

const state = ref<"initial" | "fetching" | "error" | "ready">("initial");
const selectProject = (id: ProjectID) => {
  projectStore.setProject(id);
  const p = projectStore.project();
  if (p) {
    navStore.setOutcome(p.outcomeKey);
  }
};
function fetchProjects() {
  state.value = "fetching";

  const apiEndpoint =
    route.name === "protected-project" ? "/protected/api/v2/projects/all" : "/api/v2/projects/all";

  fetch(apiEndpoint, {
    method: "GET",
    headers,
    cache: "no-cache",
  })
    .then((res) => res.json())
    .then(APIProjectsRouteSpec.check)
    .then((res) => {
      const ps = res.projects.map(api2Project).map(
        // FIXME REMOVE date overrides when test data is correct!
        (p) => ({
          ...p,
          performancePeriodFrom: DateTime.fromObject({ year: 2024, month: 1 }),
          performancePeriodTo: DateTime.fromObject({ year: 2027, month: 1 }),
        })
      );
      projectStore._projects = _.keyBy(ps, (p) => p.id);
      selectProject(ps?.[0]?.id);
      state.value = "ready";
    })
    .catch((e) => {
      console.error("ERROR:", e);
      state.value = "error";
    });
}
onMounted(fetchProjects);
</script>

<template>
  <div class="btn-group project-selector">
    <div class="dropdown">
      <button disabled v-if="state === 'initial'" class="btn btn-danger dropdown-toggle">
        {{ LOADING_STRING }}
      </button>
      <button disabled v-else-if="state === 'error'" class="btn btn-warning dropdown-toggle">
        Could not load projects at all. Are you signed in?
      </button>
      <template v-else>
        <button
          class="btn btn-danger dropdown-toggle"
          :disabled="state === 'fetching'"
          data-bs-toggle="dropdown">
          {{ state === "fetching" ? LOADING_STRING : "Choose demo project" }}
        </button>
        <ul class="dropdown-menu">
          <li v-for="p of projectStore._projects" :key="p.id" class="dropdown-item">
            <button
              :active="projectStore._currentProject === p.id"
              class="btn btn-sm btn-link"
              @click="selectProject(p.id)">
              {{ p.projectName }} (ID: {{ p.id }})
            </button>
          </li>
        </ul>
      </template>
    </div>
    <button class="btn btn-danger ms-1" @click="fetchProjects" :disabled="!state">↺</button>
  </div>
</template>

<style scoped>
.project-selector {
  position: fixed;
  left: 2px;
  top: 2px;
  z-index: 999999;
  box-shadow: 4px 4px #444;
}
</style>
