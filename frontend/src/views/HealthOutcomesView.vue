<script setup lang="ts">
import { useNavigationStore } from "@/stores/nav";
import { OUTCOME_DATA } from "@/stores/OUTCOME_DATA";
import { computed } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const navStore = useNavigationStore();

const outcome = computed(() => navStore.outcome());
</script>

<template>
  <!-- eslint-disable vue/no-v-html // Sourcing HTML from local file, not user -->
  <div class="health-outcome-view container-fluid d-flex">
    <div class="card about">
      <h1 class="card-header d-flex align-items-center gap-4">
        <span>Health Outcomes</span>
        <button class="btn btn-secondary" aria-label="Back button" @click="router.go(-1)">
          <i class="bi-chevron-double-left"></i>
          Back
        </button>
      </h1>
      <div class="card-body flex-wrap">
        <nav class="d-grid col justify-content-center">
          <div class="nav nav-pills" id="nav-tab" role="tablist">
            <button
              v-for="{ key, label } in OUTCOME_DATA"
              :aria-controls="`nav-${key}`"
              :aria-label="`${label}`"
              :class="key === navStore.outcome().key ? 'selected btn btn-info' : 'btn btn-light'"
              :data-bs-target="`#nav-${key}`"
              :id="`nav-${key}-tab`"
              :key="key"
              @click="navStore.setOutcome(key)"
              role="tab">
              {{ label }}
            </button>
          </div>
        </nav>
        <div class="tab-pane">
          <div class="container-fluid">
            <div class="row">
              <div class="col-12">
                <h2>{{ outcome.label }}</h2>
              </div>
            </div>
            <div class="row">
              <div class="col-3"><img class="img-fluid" alt="" :src="`${outcome.image}`" /></div>
              <div class="col-9">
                <h3>Overview</h3>
                <p><span v-html="outcome.aboutOverview"></span></p>
                <h3>The Problem</h3>
                <p><span v-html="outcome.aboutProblem"></span></p>
                <h3>Performance Monitoring</h3>
                <p><span v-html="outcome.aboutMetrics"></span></p>
                <div v-if="outcome.aboutReferences !== ''">
                  <h3>References</h3>
                  <p><span v-html="outcome.aboutReferences"></span></p>
                </div>
                <div>
                  <p>
                    For more information on data sources, limitations, and calculations, please see
                    our
                    <a :href="`/aboutdata/#${outcome.key}-section`">About the Data</a>
                    page.
                  </p>
                  <p my-6>&nbsp;</p>
                  <p my-6>&nbsp;</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.health-outcome-view {
  .about {
    background-color: var(--brand-cool-gray-5);
  }

  .outcome-btn {
    display: grid;
    color: #000;
    background-color: var(--brand-white);
    margin: 0.5em;
    width: 14em;
    grid-template-columns: 20% auto;
  }

  .outcome-icon {
    width: 100%;
    align-self: center;
  }

  .outcome-label {
    width: 100%;
    align-self: center;
  }

  .tab-pane {
    background-color: var(--brand-cool-gray-5);
    padding-top: 1em;
  }
}
</style>
