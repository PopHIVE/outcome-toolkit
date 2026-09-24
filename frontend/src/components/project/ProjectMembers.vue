<script setup lang="ts">
import { useProjectStore } from "@/stores/project";
import { pln } from "@/util/formatters";
import _ from "lodash";

const projectStore = useProjectStore();
const project = projectStore.project();
</script>

<template>
  <div v-if="!project" class="project-members dropdown">
    <ul class="dropdown-menu project-member-dropdown">
      <li class="dropdown-item" disabled>No project</li>
    </ul>
  </div>
  <div v-else class="project-members dropdown">
    <button
      aria-expanded="false"
      class="dropdown-toggle btn btn-sm btn-primary"
      data-bs-toggle="dropdown"
      id="project-members-toggle"
      title="Project members">
      {{ pln(_.size(project.users), "project member") }}
    </button>

    <ul class="dropdown-menu project-member-dropdown">
      <li v-if="project.users.length === 0" class="dropdown-item disabled">No members found</li>
      <li v-for="m in project.users" :key="m.id">{{ m.first_name }} {{ m.last_name }}</li>
      <!-- <li class="dropdown-header">Health Accelerators:</li>
      <li
        class="dropdown-item"
        v-for="m in project.users.filter((u) => u.role === 'Health Accelerator')"
        :key="m.id">
        {{ m.first_name }} {{ m.last_name }}
      </li>

      <li class="dropdown-header">Outcome Buyers:</li>
      <li
        class="dropdown-item"
        v-for="m in project.users.filter((u) => u.role === 'Outcome Buyer')"
        :key="m.id">
        {{ m.first_name }} {{ m.last_name }}
      </li> -->
    </ul>
  </div>
</template>
