<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();
</script>
<template>
  <main class="card about-page">
    <h2 class="card-header d-flex align-items-center gap-4">
      <span>The Outcome Toolkit Program</span>
      <button class="btn btn-secondary" aria-label="Back button" @click="router.go(-1)">
        <i class="bi-chevron-double-left"></i>
        Back
      </button>
    </h2>
    <div class="card-body row">
      <div class="col-12">
        <p>
          The Outcome Toolkit program is a three-year demonstration project that aims to greatly
          improve health outcomes through outcomes-based incentives. The program has three goals:
        </p>
        <ol>
          <li>
            Improve health for large groups of people in specific geographic areas by using new and
            innovative technologies and strategies.
          </li>
          <li>Track changes in health outcomes in real time.</li>
          <li>
            Develop a financial rewards model for improving health outcomes that can be scaled and
            sustained over time.
          </li>
        </ol>
        <p>
          The program will provide payments to Health Accelerators, performers selected to carry out
          strategies and interventions that improve health outcomes. These rewards will depend on
          the Health Accelerator reaching clear and measurable goals that will have a major impact
          on people's health. The Health Accelerator will choose to focus its activities on one of
          two priority health outcomes. The proposed interventions must demonstrate a technical
          approach that is inclusive of diverse populations within the chosen geographic area.
        </p>
        <h3><strong>The Outcome Toolkit</strong></h3>
        <p>
          The Outcome Toolkit is a web-based platform that shows data, provided by the government,
          for specific health outcomes on an interactive map at the national, state, and local
          levels across the United States. The toolkit is tailored to the Health Accelerator’s
          selected health outcome and community providing a method for monitoring and evaluating the
          program.
        </p>
        <p>
          Heat maps within the toolkit will display the selected health metrics by county or ZCTA3,
          which is the census area roughly corresponding to the first three numbers of the zip code.
          Additionally, the toolkit will include population data by geographic area (e.g., total
          residents with breakdown by age, income, and race/ethnicity). Users can choose multiple
          areas and see population demographics and baseline health metrics across the selected
          geographic area. In addition, users can export their reports to track their progress
          towards achieving the selected health outcomes.
        </p>
      </div>
    </div>
  </main>
</template>

<style scoped></style>
