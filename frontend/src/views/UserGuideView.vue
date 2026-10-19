<script setup lang="ts">
import { publicPath } from "@/util/Consts";
import { useRouter } from "vue-router";

const router = useRouter();
</script>

<template>
  <main class="card userguide-page">
    <h2 class="card-header d-flex align-items-center gap-4">
      <span>Outcome Toolkit User Guide</span>
      <button class="btn btn-secondary" aria-label="Back button" @click="router.go(-1)">
        <i class="bi-chevron-double-left"></i>
        Back
      </button>
    </h2>
    <div class="card-body">
      <div class="row">
        <div class="col-12">
          <p>
            The Outcome Toolkit can be used by anyone. However, the following information is
            targeted to Health Accelerators to guide them on how to use and navigate the Outcome
            Toolkit for their community-based intervention.
          </p>
          <h3>Step 1: Establishing a baseline.</h3>
          <p>
            As a Health Accelerator, there are four steps you must complete to establish a baseline
            for your intervention in the Outcome Toolkit program:
          </p>
          <ol>
            <li>Select an outcome</li>
            <li>Define a target area</li>
            <li>Evaluate area suitability for the program</li>
            <li>Optionally, export a report about your defined target area.</li>
          </ol>
          <p>Select the “Get Started” button to go to the next page.</p>
          <img
            class="mb-3 ug-image"
            :src="publicPath('outcome_toolkit_ug1.png')"
            alt="User guide Home page image with Get Started button to go to the Search page"
            aria-hidden />
          <h3>Step 2: Select a health outcome.</h3>
          <p>
            Select the health outcome that you want to explore. Once you select the health outcome,
            more information on the topic will appear below. In the example below, we have picked
            Opioid Overdose.
          </p>
          <p>
            Click on the “Proceed with selecting a region” button to advance to the next screen.
          </p>
          <img
            class="mb-3 ug-image"
            :src="publicPath('outcome_toolkit_ug2.png')"
            alt="User guide Search page image with Outcome buttons and Proceed button to go to the Results page"
            aria-hidden />
          <h3>Step 3: Define the target area.</h3>
          <p>
            Next, select the state where you want to conduct the intervention by clicking the “Add
            all” button next it.
          </p>
          <img
            class="mb-3 ug-image"
            :src="publicPath('outcome_toolkit_ug3.png')"
            alt="User guide Results page image indicating the ability to select the state to evaluate"
            aria-hidden />
          <h3>Step 4: Evaluate area suitability.</h3>
          <p>
            Select an area by counties or by the entire state. Priority will be given to
            applications which meet the minimum requirements for both population and the rate of the
            outcome.
          </p>
          <ol>
            <li>
              You can add counties by selecting from the list in the gray box or by clicking on “Add
              All” for the entire state.
            </li>
            <li>
              As an option, you can select additional areas of interest by clicking on the map and
              adding counties that are next to each other until you reach the required population
              and outcome rate in the graphs to the right.
            </li>
            <li>
              Once the bar changes color and you see the check mark below the bar, you will have met
              the requirements for population or outcome rate.
            </li>
            <li>
              You can expand the trended data visualization for the selected area by clicking the
              arrows icon in the trended data visualization graph.
            </li>
          </ol>
          <p>
            <i>
              *Note: A gray bar and a triangle warning sign indicate that you have not met the
              minimum requirements for population or outcome rate.
            </i>
          </p>
          <img
            class="mb-3 ug-image"
            :src="publicPath('outcome_toolkit_ug4.png')"
            alt="User guide Results page image indicating the ability to select the area using the list or the map"
            aria-hidden />
          <br />
          <img
            class="mb-3 ug-image"
            :src="publicPath('outcome_toolkit_ug5.png')"
            alt="User guide Results page image indicating that metrics are displayed when an area is selected"
            aria-hidden />
          <p>
            Click the arrows in the trended data visualization graph to expand and collapse the
            trended data visualization for the selected area.
          </p>
          <img
            class="mb-3 ug-image"
            :src="publicPath('outcome_toolkit_ug6.png')"
            alt="User guide Results page image indicating the ability to select the state to evaluate"
            aria-hidden />
          <h3>Step 5: Export report on defined target area.</h3>
          <p>
            In this last step, you can export your data as a CSV file or PDF by clicking on the
            appropriate button.
          </p>
          <img
            class="mb-3 ug-image"
            :src="publicPath('outcome_toolkit_ug7.png')"
            alt="User guide Results page image indicating the Export buttons to export the results"
            aria-hidden />
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.ug-image {
  width: 70vw;
  margin: auto;
}
</style>
