<script setup lang="ts">
import { useRouter } from "vue-router";
import { useNavigationStore } from "@/stores/nav";
import { OUTCOME_DATA } from "@/stores/OUTCOME_DATA";
import PaymentRateTable from "@/components/common/PaymentRateTable.vue";
import { computed } from "vue";
import { useDataStore } from "@/stores/data";
import { payoutFormatter, payoutPercentFormatter } from "@/util/formatters";

const router = useRouter();
const navStore = useNavigationStore();
const dataStore = useDataStore();
const payoutTarget = computed(() => dataStore.targetPayout(navStore.outcome().key, "18"));
</script>

<template>
  <div class="payment-rates-view container-fluid d-flex">
    <div class="card about">
      <h1 class="card-header d-flex align-items-center gap-4">
        <span>Payment Rates</span>
        <button class="btn btn-secondary" aria-label="Back button" @click="router.go(-1)">
          <i class="bi-chevron-double-left"></i>
          Back
        </button>
      </h1>
      <div class="card-body flex-wrap">
        <div class="px-5">
          <p>
            The Outcome Toolkit Program aims to improve specific health outcomes in regions selected
            by Health Accelerators (HA). For each of the health outcomes, the targeted value of
            societal benefit and thereby the program's expectation of success is defined by tracking
            metrics outlined in the chart below. HA performance in their selected outcome is
            measured against defined targets at 6-month intervals, for the 36-month duration of the
            period of performance.
          </p>
          <p>
            During the three-year program performance period, each HA is reviewed at 6-month
            intervals to evaluate progress in achieving the targeted reduction in the selected
            adverse health outcome. HA performance will then determine the amount of additional
            award the HA will receive from the program and participating Outcome Buyers for each
            6-month period. Achievement of the target reduction (or greater) will result in the
            maximum award payment, and partial achievement of a target will result in partial award
            of the available maximum.
          </p>
          <p>
            The tables below represent the rate card used to display a HA's recorded performance in
            the Outcome Toolkit. Performance targets for each outcome are listed for each 6-month
            period of the program, along with the maximum outcome-based payment a HA is eligible to
            receive based on meeting their goals.
          </p>
        </div>
      </div>
      <nav class="d-grid col justify-content-center my-5">
        <div class="d-flex justify-content-center nav nav-pills" id="nav-tab" role="tablist">
          <button
            v-for="{ key, icon, label } in OUTCOME_DATA"
            :aria-controls="`nav-${key}`"
            aria-selected="false"
            :aria-label="`${label}`"
            :class="{ active: navStore.outcome().key === key }"
            :data-bs-target="`#nav-${key}`"
            :id="`nav-${key}-tab`"
            :key="key"
            @click="navStore.setOutcome(key)"
            class="btn btm-primary outcome-btn"
            role="tab">
            <img class="outcome-icon" :src="icon" alt="" />
            <strong class="outcome-label">{{ label }}</strong>
          </button>
        </div>
      </nav>
      <div class="px-5">
        <h2>Rate Card</h2>
        <PaymentRateTable showCaption :outcomeKey="navStore.outcome().key" />
        <p>
          <strong>Percent (%) Improvement</strong> from baseline is determined by calculating the
          improvement from their baselines (difference in differences) at the Program's start.
        </p>
        <p>
          <strong>Payouts</strong> are contingent on achieving certain improvements. These
          improvements vary based on which outcome is being addressed. Meeting the target
          improvement will result in full payout for that period.
        </p>
        <p>
          If a <strong>partial reduction</strong> is achieved, payout will be prorated according to
          the reduction achieved.
          <template v-if="payoutTarget">
            For example, if a {{ payoutPercentFormatter(payoutTarget.targetRate / 2) }} improvement
            is achieved at the 18-month period, the payout would be
            {{ payoutFormatter(payoutTarget.maximumPayout / 2) }}.
          </template>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.payment-rates-view {
  .about {
    background-color: var(--brand-cool-gray-5);
  }

  .tab-pane {
    background-color: var(--brand-cool-gray-5);
    padding-top: 1em;
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
}
</style>
