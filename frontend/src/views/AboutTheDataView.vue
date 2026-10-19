<script setup lang="ts">
import { OUTCOME_DATA } from "@/stores/OUTCOME_DATA";
import { DATA_SOURCE } from "@/util/Consts";
import { useRouter } from "vue-router";
import { onMounted, ref } from "vue";

const router = useRouter();

const dataReleaseNotesHtml = ref("");

onMounted(() => {
  // Release notes are served by the backend; the static (Ingest) build has none.
  if (DATA_SOURCE !== "api") return;
  fetch("/api/v2/data-release-notes")
    .then((res) => {
      return res.json();
    })
    .then((json) => {
      dataReleaseNotesHtml.value = json.html_text;
    });
});

// Reference objects
const generalBtn = ref();
const socBtn = ref();
const cardioBtn = ref();
const opioidBtn = ref();
const alcoholBtn = ref();
const dataReleaseNotesBtn = ref();
const sections = ref();
const generalSection = ref();
const socSection = ref();
const cardioSection = ref();
const opioidSection = ref();
const alcoholSection = ref();
const dataReleaseNotesSection = ref();

/**
 * Method to scroll the sections div to the section section specified by the input parameter
 * @param section string indicating the section section to scroll
 */
function scrollTo(section: string) {
  if (section === "general") {
    sections.value.scrollTop = generalSection.value.scrollTop;
    generalBtn.value.style.textDecoration = "underline";
    generalBtn.value.style.textDecorationColor = "var(--brand-cyan)";
    socBtn.value.style.textDecoration = "";
    cardioBtn.value.style.textDecoration = "";
    opioidBtn.value.style.textDecoration = "";
    alcoholBtn.value.style.textDecoration = "";
    dataReleaseNotesBtn.value.style.textDecoration = "";
  } else if (section === OUTCOME_DATA.soc.key) {
    sections.value.scrollTop = generalSection.value.scrollTop + generalSection.value.scrollHeight;
    generalBtn.value.style.textDecoration = "";
    socBtn.value.style.textDecoration = "underline";
    socBtn.value.style.textDecorationColor = "var(--brand-cyan)";
    cardioBtn.value.style.textDecoration = "";
    opioidBtn.value.style.textDecoration = "";
    alcoholBtn.value.style.textDecoration = "";
    dataReleaseNotesBtn.value.style.textDecoration = "";
  } else if (section === OUTCOME_DATA.cardio.key) {
    sections.value.scrollTop =
      generalSection.value.scrollTop +
      generalSection.value.scrollHeight +
      socSection.value.scrollHeight;
    generalBtn.value.style.textDecoration = "";
    socBtn.value.style.textDecoration = "";
    cardioBtn.value.style.textDecoration = "underline";
    cardioBtn.value.style.textDecorationColor = "var(--brand-cyan)";
    opioidBtn.value.style.textDecoration = "";
    alcoholBtn.value.style.textDecoration = "";
    dataReleaseNotesBtn.value.style.textDecoration = "";
  } else if (section === OUTCOME_DATA.opioid.key) {
    sections.value.scrollTop =
      generalSection.value.scrollTop +
      generalSection.value.scrollHeight +
      socSection.value.scrollHeight +
      cardioSection.value.scrollHeight;
    generalBtn.value.style.textDecoration = "";
    socBtn.value.style.textDecoration = "";
    cardioBtn.value.style.textDecoration = "";
    opioidBtn.value.style.textDecoration = "underline";
    opioidBtn.value.style.textDecorationColor = "var(--brand-cyan)";
    alcoholBtn.value.style.textDecoration = "";
    dataReleaseNotesBtn.value.style.textDecoration = "";
  } else if (section === OUTCOME_DATA.alcohol.key) {
    sections.value.scrollTop =
      generalSection.value.scrollTop +
      generalSection.value.scrollHeight +
      socSection.value.scrollHeight +
      cardioSection.value.scrollHeight +
      opioidSection.value.scrollHeight;
    generalBtn.value.style.textDecoration = "";
    socBtn.value.style.textDecoration = "";
    cardioBtn.value.style.textDecoration = "";
    opioidBtn.value.style.textDecoration = "";
    alcoholBtn.value.style.textDecoration = "underline";
    alcoholBtn.value.style.textDecorationColor = "var(--brand-cyan)";
    dataReleaseNotesBtn.value.style.textDecoration = "";
  } else if (section === "notes") {
    sections.value.scrollTop =
      generalSection.value.scrollTop +
      generalSection.value.scrollHeight +
      socSection.value.scrollHeight +
      cardioSection.value.scrollHeight +
      opioidSection.value.scrollHeight +
      alcoholSection.value.scrollHeight;
    generalBtn.value.style.textDecoration = "";
    socBtn.value.style.textDecoration = "";
    cardioBtn.value.style.textDecoration = "";
    opioidBtn.value.style.textDecoration = "";
    alcoholBtn.value.style.textDecoration = "";
    dataReleaseNotesBtn.value.style.textDecoration = "underline";
    dataReleaseNotesBtn.value.style.textDecorationColor = "var(--brand-cyan)";
  }
}

/**
 * Method to update the section nav buttons to be underlined when the sections div is scrolled
 * to the corresponding section section
 * <div class="col-10 sections" ref="sections" @scroll="handleScroll">
 */
function handleScroll() {
  if (sections.value.scrollTop < generalSection.value.scrollHeight * 0.9) {
    generalBtn.value.style.textDecoration = "underline";
    generalBtn.value.style.textDecorationColor = "var(--brand-cyan)";
    socBtn.value.style.textDecoration = "";
    cardioBtn.value.style.textDecoration = "";
    opioidBtn.value.style.textDecoration = "";
    alcoholBtn.value.style.textDecoration = "";
  }
  if (
    sections.value.scrollTop > generalSection.value.scrollHeight * 0.9 &&
    sections.value.scrollTop <
      (generalSection.value.scrollHeight + socSection.value.scrollHeight) * 0.9
  ) {
    generalBtn.value.style.textDecoration = "";
    socBtn.value.style.textDecoration = "underline";
    socBtn.value.style.textDecorationColor = "var(--brand-cyan)";
    cardioBtn.value.style.textDecoration = "";
    opioidBtn.value.style.textDecoration = "";
    alcoholBtn.value.style.textDecoration = "";
  }
  if (
    sections.value.scrollTop >
      (generalSection.value.scrollHeight + socSection.value.scrollHeight) * 0.9 &&
    sections.value.scrollTop <
      (generalSection.value.scrollHeight +
        socSection.value.scrollHeight +
        cardioSection.value.scrollHeight) *
        0.9
  ) {
    generalBtn.value.style.textDecoration = "";
    socBtn.value.style.textDecoration = "";
    cardioBtn.value.style.textDecoration = "underline";
    cardioBtn.value.style.textDecorationColor = "var(--brand-cyan)";
    opioidBtn.value.style.textDecoration = "";
    alcoholBtn.value.style.textDecoration = "";
  }
  if (
    sections.value.scrollTop >
      (generalSection.value.scrollHeight +
        socSection.value.scrollHeight +
        cardioSection.value.scrollHeight) *
        0.9 &&
    sections.value.scrollTop <
      (generalSection.value.scrollHeight +
        socSection.value.scrollHeight +
        cardioSection.value.scrollHeight +
        opioidSection.value.scrollHeight) *
        0.9
  ) {
    generalBtn.value.style.textDecoration = "";
    socBtn.value.style.textDecoration = "";
    cardioBtn.value.style.textDecoration = "";
    opioidBtn.value.style.textDecoration = "underline";
    opioidBtn.value.style.textDecorationColor = "var(--brand-cyan)";
    alcoholBtn.value.style.textDecoration = "";
  }
  if (
    sections.value.scrollTop >
      (generalSection.value.scrollHeight +
        socSection.value.scrollHeight +
        cardioSection.value.scrollHeight +
        opioidSection.value.scrollHeight) *
        0.9 &&
    sections.value.scrollTop <
      (generalSection.value.scrollHeight +
        socSection.value.scrollHeight +
        cardioSection.value.scrollHeight +
        opioidSection.value.scrollHeight +
        alcoholSection.value.scrollHeight) *
        0.9
  ) {
    generalBtn.value.style.textDecoration = "";
    socBtn.value.style.textDecoration = "";
    cardioBtn.value.style.textDecoration = "";
    opioidBtn.value.style.textDecoration = "";
    alcoholBtn.value.style.textDecoration = "underline";
    alcoholBtn.value.style.textDecorationColor = "var(--brand-cyan)";
  }
  if (sections.value.scrollHeight - sections.value.scrollTop === sections.value.clientHeight) {
    generalBtn.value.style.textDecoration = "";
    socBtn.value.style.textDecoration = "";
    cardioBtn.value.style.textDecoration = "";
    opioidBtn.value.style.textDecoration = "";
    alcoholBtn.value.style.textDecoration = "";
    dataReleaseNotesBtn.value.style.textDecoration = "underline";
    dataReleaseNotesBtn.value.style.textDecorationColor = "var(--brand-cyan)";
  }
}

/**
 * Method to download the measure definition file for the specified outcome
 * @param key key of the outcome
 */
function downloadMeasureDefinition(key: string) {
  let filename = "";
  if (key === OUTCOME_DATA.soc.key) {
    filename = OUTCOME_DATA.soc.metric.definitions;
  } else if (key === OUTCOME_DATA.alcohol.key) {
    filename = OUTCOME_DATA.alcohol.metric.definitions;
  } else if (key === OUTCOME_DATA.cardio.key) {
    filename = OUTCOME_DATA.cardio.metric.definitions;
  } else if (key === OUTCOME_DATA.opioid.key) {
    filename = OUTCOME_DATA.opioid.metric.definitions;
  }
  // fake link to download
  const downloadLink = document.createElement("a");
  downloadLink.setAttribute("hidden", "true");
  downloadLink.href = filename;
  downloadLink.download = filename.split("/").pop() ?? filename;
  downloadLink.click();

  // cleanup
  downloadLink.remove();
}

/**
 * Method to download the Coverage by State file for the specified outcome
 * @param key key of the outcome
 */
function downloadCoverageByState(key: string) {
  let filename = "";
  if (key === OUTCOME_DATA.soc.key) {
    filename = OUTCOME_DATA.soc.metric.coverageByState;
  } else if (key === OUTCOME_DATA.alcohol.key) {
    filename = OUTCOME_DATA.alcohol.metric.coverageByState;
  } else if (key === OUTCOME_DATA.cardio.key) {
    filename = OUTCOME_DATA.cardio.metric.coverageByState;
  } else if (key === OUTCOME_DATA.opioid.key) {
    filename = OUTCOME_DATA.opioid.metric.coverageByState;
  }
  // fake link to download
  const downloadLink = document.createElement("a");
  downloadLink.setAttribute("hidden", "true");
  downloadLink.href = filename;
  downloadLink.download = filename.split("/").pop() ?? filename;
  downloadLink.click();

  // cleanup
  downloadLink.remove();
}
</script>

<template>
  <main class="card section-page">
    <h2 class="card-header d-flex align-items-center gap-4">
      <span>About the Data</span>
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
              class="btn section-nav"
              ref="generalBtn"
              aria-label="General navigation button"
              @click="scrollTo('general')"
              :style="{ textDecoration: 'underline', textDecorationColor: 'var(--brand-cyan)' }">
              General
            </button>
          </li>
          <li class="nav-item">
            <button
              class="btn section-nav"
              ref="socBtn"
              aria-label="Maternal Health navigation button"
              @click="scrollTo(OUTCOME_DATA.soc.key)"
              :style="{ textDecorationColor: 'var(--brand-cyan)' }">
              Maternal Health
            </button>
          </li>
          <li class="nav-item">
            <button
              class="btn section-nav"
              ref="cardioBtn"
              aria-label="Heart Attack and Stroke Risk navigation button"
              @click="scrollTo(OUTCOME_DATA.cardio.key)"
              :style="{ textDecorationColor: 'var(--brand-cyan)' }">
              Heart Attack and Stroke Risk
            </button>
          </li>
          <li class="nav-item">
            <button
              class="btn section-nav"
              ref="opioidBtn"
              aria-label="Opioid Overdose navigation button"
              @click="scrollTo(OUTCOME_DATA.opioid.key)"
              :style="{ textDecorationColor: 'var(--brand-cyan)' }">
              Opioid Overdose
            </button>
          </li>
          <li class="nav-item">
            <button
              class="btn section-nav"
              ref="alcoholBtn"
              aria-label="Alcohol-Related Health Harms navigation button"
              @click="scrollTo(OUTCOME_DATA.alcohol.key)"
              :style="{ textDecorationColor: 'var(--brand-cyan)' }">
              Alcohol-Related Health Harms
            </button>
          </li>
          <li class="nav-item">
            <button
              class="btn section-nav"
              ref="dataReleaseNotesBtn"
              aria-label="Data Release Notes navigation button"
              @click="scrollTo('notes')"
              :style="{ textDecorationColor: 'var(--brand-cyan)' }">
              Data Release Notes
            </button>
          </li>
        </ul>
      </div>
      <div class="col-10 sections" ref="sections" @scroll="handleScroll">
        <div ref="generalSection" id="general-section">
          <h2><strong>General</strong></h2>
          <p>
            The Outcome Toolkit Program highlights four specific health outcomes of interest. These
            outcomes were selected for their continued health burden due to significant morbidity
            and mortality despite the availability of effective evidence-based interventions to
            prevent such circumstances or reduce their severity. The four outcomes are as follows:
          </p>
          <ol>
            <li>
              <strong>Maternal Health:</strong> Reduction in the rate of intrapartum and postpartum
              severe obstetric complications
            </li>
            <li>
              <strong>Heart Attack and Stroke Risk:</strong> Reduction in the aggregate 10-year risk
              of heart attack and stroke for people aged 40-70 years
            </li>
            <li>
              <strong>Opioid Overdose:</strong> Reduction in the rate of emergency medical services
              (EMS) patient encounters for fatal and non-fatal opioid overdoses per 100,000
              population
            </li>
            <li>
              <strong>Alcohol-Related Health Harms:</strong> Reduction in the rate of emergency
              medical services (EMS) patient encounters for alcohol-related emergencies per 100,000
              population
            </li>
          </ol>
          <p>
            These outcomes were chosen following discussions with major federal health authorities
            and rigorous reviews using a rubric that prioritized public health impact, diversity of
            ages and populations, presence of highly effective enabling technologies or practices
            that could be scaled to have impact quickly, well-accepted upstream metrics known to
            affect long-term outcomes, and availability of data at the population level.
          </p>
        </div>
        <div ref="socSection" :id="`${OUTCOME_DATA.soc.key}-section`">
          <h2><strong>Maternal Health</strong></h2>
          <p>
            <strong>Metric:</strong> Rate of intrapartum and postpartum severe obstetric
            complications per 10,000 deliveries (Source: open claims data)
          </p>
          <p>
            The Severe Obstetric Complications (SOC) electronic clinical quality measure (eCQM)
            identifies patients with severe obstetric complications that occur during inpatient
            delivery hospitalizations. The measure was developed by The Joint Commission, the
            Centers for Medicare and Medicaid Services (CMS), and Yale New Haven Health Service
            Corporation/Center for Outcomes Research and Evaluation. It captures 21 indicators (16
            diagnoses and five procedures), as identified by the Centers for Disease Control (CDC),
            for measuring SOCs.
          </p>
          <p>The measure has been modified for the Outcome Toolkit program in two ways:</p>
          <ul>
            <li>
              It captures SOCs during the delivery hospitalization and 60 days post-delivery. NOTE:
              the data shown is for Open Claims only.
            </li>
            <li>
              Certain mental health conditions have been included as SOCs in the metric (e.g.,
              suicide, self-harm, and substance use) if they result in admissions to inpatient
              hospitals, psychiatric centers, or substance use treatment centers in the 60-day
              post-delivery period.
            </li>
          </ul>
          <p>
            While women may experience a less severe outcome if a blood transfusion is their only
            SOC, the Outcome Toolkit program will include the administration of blood transfusions
            during the delivery hospitalization or in the 60 days post-delivery in its SOC rate.
          </p>
          <button
            v-if="OUTCOME_DATA.soc.metric.definitions"
            class="btn btn-outline-secondary big-button mt-2 me-2"
            title="Click to Download SOC Measure Definitions"
            aria-label="Download SOC Measure Definitions button"
            @click="downloadMeasureDefinition(OUTCOME_DATA.soc.key)">
            Download SOC Measure Definitions
          </button>
          <button
            v-if="OUTCOME_DATA.soc.metric.coverageByState"
            class="btn btn-outline-secondary big-button mt-2"
            title="Click to Download SOC Coverage by State"
            aria-label="Download SOC Coverage by State button"
            @click="downloadCoverageByState(OUTCOME_DATA.soc.key)">
            Download SOC Coverage by State
          </button>
          <p my-6>&nbsp;</p>
        </div>
        <div ref="cardioSection" :id="`${OUTCOME_DATA.cardio.key}-section`">
          <h2><strong>Heart Attack and Stroke Risk</strong></h2>
          <p>
            <strong>Metric:</strong> Average risk of heart attack or stroke over the next 10 years
            (percent), averaged using the risk score for all people aged 40-70 years (Source: EHR
            data)
          </p>
          <p>
            The Outcome Toolkit program will not be measuring the actual rates of heart attack and
            stroke, but rather the predicted risk based on a patient's sex, age, race, cholesterol,
            blood pressure, diabetes history, smoking status, and certain medication treatments.
          </p>
          <p>
            Following established standards, the Outcome Toolkit program uses the Longitudinal ASCVD
            Risk Assessment Tool to calculate the 10-year Risk Score, which was previously developed
            and used in the CMS Million Hearts Cardiovascular Risk Reduction Model for Medicare
            patients. The tool predicts baseline 10-year ASCVD risk, projects changes in ASCVD risk
            that would be expected with initiation of and adherence to evidence-based therapies, and
            incorporates individual patient responses to these therapies over time to allow for
            dynamic, longitudinal ASCVD risk prediction.
            (https://doi.org/10.1161/CIR.0000000000000467)
          </p>
          <p>
            The Longitudinal ASCVD Risk Assessment Tool was derived from the ASCVD Risk Estimator,
            which was developed by the American College of Cardiology and American Heart
            Association. (Goff DC, Jr., Lloyd-Jones DM, Bennett G, et al. 2013 ACC/AHA guideline on
            the assessment of cardiovascular risk: a report of the American College of
            Cardiology/American Heart Association Task Force on Practice Guidelines. J Am Coll
            Cardiol 2014;63:2935-59)
          </p>
          <button
            v-if="OUTCOME_DATA.cardio.metric.definitions"
            class="btn btn-outline-secondary big-button"
            title="Click to Download Heart Attack and Stroke Risk Measure Definitions"
            aria-label="Download Heart Attack and Stroke Risk Measure Definitions button"
            @click="downloadMeasureDefinition(OUTCOME_DATA.cardio.key)">
            Download Heart Attack and Stroke Risk Measure Definitions
          </button>
          <p my-6>&nbsp;</p>
        </div>
        <div ref="opioidSection" :id="`${OUTCOME_DATA.opioid.key}-section`">
          <h2><strong>Opioid Overdose</strong></h2>
          <p>
            <strong>Metric:</strong> Rate of emergency medical services (EMS) patient encounters for
            fatal and non-fatal opioid overdoses per 100,000 population (Source: National Emergency
            Medical Services Information System (NEMSIS) data feed)
          </p>
          <p>
            The metric tracks suspected fatal and non-fatal opioid overdose events in the
            pre-hospital care setting based on a set of standardized codes that capture patient
            symptoms and EMS provider impressions.
          </p>
          <p>
            NEMSIS is a national database that collects, stores, and shares EMS data from states and
            territories. NEMSIS is a universal standard for collecting and documenting patient care
            information resulting from emergency 911 encounters. NEMSIS standardizes data collected
            by EMS agencies and provides a framework for collecting and sharing data. It is funded
            by the Office of EMS within the National Highway Traffic Safety Administration.
          </p>
          <button
            v-if="OUTCOME_DATA.opioid.metric.definitions"
            class="btn btn-outline-secondary big-button"
            title="Click to Download Opioid Overdose Measure Definitions"
            aria-label="Download Opioid Overdose Measure Definitions button"
            @click="downloadMeasureDefinition(OUTCOME_DATA.opioid.key)">
            Download Opioid Overdose Measure Definitions
          </button>
          <p my-6>&nbsp;</p>
        </div>
        <div ref="alcoholSection" :id="`${OUTCOME_DATA.alcohol.key}-section`">
          <h2><strong>Alcohol-Related Health Harms</strong></h2>
          <p>
            <strong>Metric:</strong>Rate of emergency medical services (EMS) patient encounters for
            alcohol-related emergencies per 100,000 population (Source: NEMSIS data feed)
          </p>
          <p>
            The metric tracks suspected alcohol-related events in the pre-hospital care setting
            based on a set of standardized codes that capture patient symptoms and EMS provider
            impressions.
          </p>
          <p>
            NEMSIS is a national database that collects, stores, and shares data from states and
            territories. NEMSIS is a universal standard for collecting and documenting patient care
            information resulting from emergency 911 encounters. NEMSIS standardizes data collected
            by EMS agencies and provides a framework for collecting and sharing data. It is funded
            primarily by the Office of EMS within the National Highway Traffic Safety
            Administration.
          </p>
          <button
            v-if="OUTCOME_DATA.alcohol.metric.definitions"
            class="btn btn-outline-secondary big-button"
            title="Click to Download Alcohol-Related Health Harms Measure Definitions"
            aria-label="Download Alcohol-Related Health Harms Measure Definitions button"
            @click="downloadMeasureDefinition(OUTCOME_DATA.alcohol.key)">
            Download Alcohol-Related Health Harms Measure Definitions
          </button>
          <p my-6>&nbsp;</p>
        </div>
        <div ref="dataReleaseNotesSection" id="notesSection">
          <h2><Strong>Data Release Notes</Strong></h2>
          <div v-html="dataReleaseNotesHtml" class="b"></div>
        </div>
        <p my-6>&nbsp;</p>
        <p my-6>&nbsp;</p>
        <p my-6>&nbsp;</p>
        <p my-6>&nbsp;</p>
        <p my-6>&nbsp;</p>
      </div>
    </div>
  </main>
</template>

<style scoped>
.section-nav {
  font-size: 1rem;
  justify-content: start;
  text-align: left;
}
.sections {
  overflow-y: scroll;
  height: 100vh;
}
</style>
