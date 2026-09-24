<script setup lang="ts">
import { useRouter } from "vue-router";
import { ref } from "vue";

const router = useRouter();

// Reference objects
const aboutBtn = ref();
const metricsBtn = ref();
const areasBtn = ref();
const faqs = ref();
const aboutFAQs = ref();
const metricsFAQs = ref();
const areasFAQs = ref();

/**
 * Method to scroll the faqs div to the faq section specified by the input parameter
 * @param faq string indicating the faq section to scroll
 */
function scrollTo(faq: string) {
  if (faq === "about") {
    faqs.value.scrollTop = aboutFAQs.value.scrollTop;
    aboutBtn.value.style.textDecoration = "underline";
    aboutBtn.value.style.textDecorationColor = "var(--brand-cyan)";
    metricsBtn.value.style.textDecoration = "";
    areasBtn.value.style.textDecoration = "";
  } else if (faq === "metrics") {
    faqs.value.scrollTop = aboutFAQs.value.scrollTop + aboutFAQs.value.scrollHeight;
    aboutBtn.value.style.textDecoration = "";
    metricsBtn.value.style.textDecoration = "underline";
    metricsBtn.value.style.textDecorationColor = "var(--brand-cyan)";
    areasBtn.value.style.textDecoration = "";
  } else if (faq === "areas") {
    faqs.value.scrollTop =
      aboutFAQs.value.scrollTop + aboutFAQs.value.scrollHeight + metricsFAQs.value.scrollHeight;
    aboutBtn.value.style.textDecoration = "";
    metricsBtn.value.style.textDecoration = "";
    areasBtn.value.style.textDecoration = "underline";
    areasBtn.value.style.textDecorationColor = "var(--brand-cyan)";
  }
}

/**
 * Method to update the faq nav buttons to be underlined when the faqs div is scrolled
 * to the corresponding faq section
 * <div class="col-10 faqs" ref="faqs" @scroll="handleScroll">
 */
function handleScroll() {
  if (faqs.value.scrollTop < aboutFAQs.value.scrollHeight * 0.9) {
    aboutBtn.value.style.textDecoration = "underline";
    aboutBtn.value.style.textDecorationColor = "var(--brand-cyan)";
    metricsBtn.value.style.textDecoration = "";
    areasBtn.value.style.textDecoration = "";
  }
  if (
    faqs.value.scrollTop > aboutFAQs.value.scrollHeight * 0.9 &&
    faqs.value.scrollTop < (aboutFAQs.value.scrollHeight + metricsFAQs.value.scrollHeight) * 0.9
  ) {
    aboutBtn.value.style.textDecoration = "";
    metricsBtn.value.style.textDecoration = "underline";
    metricsBtn.value.style.textDecorationColor = "var(--brand-cyan)";
    areasBtn.value.style.textDecoration = "";
  }
  if (faqs.value.scrollHeight - faqs.value.scrollTop === faqs.value.clientHeight) {
    aboutBtn.value.style.textDecoration = "";
    metricsBtn.value.style.textDecoration = "";
    areasBtn.value.style.textDecoration = "underline";
    areasBtn.value.style.textDecorationColor = "var(--brand-cyan)";
  }
}
</script>

<template>
  <main class="card faq-page">
    <h2 class="card-header d-flex align-items-center gap-4">
      <span>Frequently Asked Questions</span>
      <button class="btn btn-secondary" aria-label="Back button" @click="router.go(-1)">
        <i class="bi-chevron-double-left"></i>
        Back
      </button>
    </h2>
    <div class="card-body row">
      <div class="col-2">
        <ul class="nav flex-column">
          <li class="nav-item">
            <button
              class="btn faq-nav"
              ref="aboutBtn"
              aria-label="About The Program navigation button"
              @click="scrollTo('about')"
              :style="{ textDecoration: 'underline', textDecorationColor: 'var(--brand-cyan)' }">
              About The Program
            </button>
          </li>
          <li class="nav-item">
            <button
              class="btn faq-nav"
              ref="metricsBtn"
              aria-label="Metrics navigation button"
              @click="scrollTo('metrics')"
              :style="{ textDecorationColor: 'var(--brand-cyan)' }">
              Metrics
            </button>
          </li>
          <li class="nav-item">
            <button
              class="btn faq-nav"
              ref="areasBtn"
              aria-label="Selecting Areas For Intervention navigation button"
              @click="scrollTo('areas')"
              :style="{ textDecorationColor: 'var(--brand-cyan)' }">
              Selecting Areas For Intervention
            </button>
          </li>
        </ul>
      </div>
      <div class="col-10 faqs" ref="faqs" @scroll="handleScroll">
        <div ref="aboutFAQs" id="about-faq" class="mb-5">
          <h2><strong>About The Program</strong></h2>
          <details>
            <summary>What is the Outcome Toolkit program?</summary>
            <p>
              The Outcome Toolkit Program provides organizations with tools and technical support to
              improve health care in large, geographically defined populations through new
              technologies and strategies. The program will track changes in health outcomes using
              select metrics and offer economic rewards for improvements. The incentives, or
              outcomes payments, will be paid to Outcome Toolkit Program participants (Health
              Accelerators) via a pre-specified rate card for improving the selected health outcome.
            </p>
          </details>
          <details>
            <summary>What is the Outcome Toolkit?</summary>
            <p>
              The Outcome Toolkit is an interactive website for the Outcome Toolkit Program that
              displays data geographically for select health outcomes across the United States. It
              is a resource for Health Accelerators and/or the public to explore, measure, or track
              specific health outcomes in various geographic regions.
            </p>
          </details>
          <details>
            <summary>
              Do you have to be a Health Accelerator or Outcome Toolkit Program participant to use
              the Outcome Toolkit?
            </summary>
            <p>No, the toolkit is available to anyone who would like to use it.</p>
          </details>
          <details>
            <summary>
              How is a Health Accelerator’s performance in achieving improvements in their
              benchmarks for their selected outcome assessed?
            </summary>
            <p>
              The program uses a difference in difference approach to calculate a Health
              Accelerator’s performance. Performance will be adjusted based on the national trend
              for the selected outcome. The payment schedule will follow a predetermined rate card
              for each outcome. Performance will be assessed every 6 months.
            </p>
          </details>
        </div>
        <div ref="metricsFAQs" id="metrics-faq" class="mb-5">
          <h2><strong>Metrics</strong></h2>
          <details>
            <summary>
              Can I use a different dataset to track the outcomes of my intervention?
            </summary>
            <p>
              The toolkit is the method that all health accelerators will be required to use to
              track their progress towards reaching their goal for their selected health outcome.
            </p>
          </details>
          <details>
            <summary>
              What is the electronic clinical quality measure (eCQM) for Severe Obstetric
              Complications (ePC-07)?
            </summary>
            <p>
              The ePC-07 measure identifies patients with severe obstetric complications that occur
              during inpatient delivery hospitalization. The measure follows the Centers for Disease
              Control’s guidance in identifying 21 factors that classify as severe obstetric
              complications, including sepsis, blood transfusion, ventilation, and more. You can
              learn more about this measure in the Severe Obstetric Complications Electronic
              Clinical Quality Measure (eCQM) Methodology Report or the eCQI Resource Center.
            </p>
          </details>
          <details>
            <summary>Can I download the raw data from the Outcome Toolkit?</summary>
            <p>No, the raw data are not available for download.</p>
          </details>
          <details>
            <summary>What is NEMSIS?</summary>
            <p>
              NEMSIS (National Emergency Medical Services Information System) collects emergency
              medical service (EMS) data from U.S. states/territories to provide a national system
              that not only standardizes the collection, storage, and use of data but also can
              inform ways to continuously improve emergency medical services. &nbsp;
            </p>
          </details>
        </div>
        <div ref="areasFAQs" id="areas-faq" class="mb-5">
          <h1><strong>Selecting Areas For Intervention</strong></h1>
          <details>
            <summary>How do I define a target area?</summary>
            <p>
              The target area should reach the designated number of individuals, which is driven by
              the chosen health outcome. Priority will be given to applications where selected areas
              of interest are contiguous.
            </p>
          </details>
          <details>
            <summary>What is a “target area”?</summary>
            <p>
              The target area is the geographic area in which the intervention will be implemented.
            </p>
          </details>
          <details>
            <summary>What does “area of suitability” mean?</summary>
            <p>
              The “area of suitability” is the minimum population size and health outcome rate
              required for a selected geographic area of interest to be eligible for the Outcome
              Toolkit Program.
            </p>
          </details>
          <details>
            <summary>What does ZCTA3 mean?</summary>
            <p mb-6>
              Each county on the map is listed by its ZCTA3 (zip code tabulation area), which is the
              first three numbers of the area's zip code. The information provided also includes the
              county's population size.
            </p>
          </details>
        </div>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
      </div>
    </div>
  </main>
</template>

<style scoped>
.faq-nav {
  font-size: 1rem;
  justify-content: start;
  text-align: left;
}
.faqs {
  overflow-y: scroll;
  height: 100vh;
}
summary {
  font-size: 1.15rem;
  font-weight: bold;
  cursor: pointer;
  padding: 0.75rem;
  background-color: var(--brand-cool-gray-0);
}

details > p {
  padding: 0.4rem;
  font-size: 1rem;
  font-weight: bold;
  border: 1.5rem;
}

summary:focus,
summary:hover {
  background-color: var(--brand-cool-gray-10);
}
</style>
