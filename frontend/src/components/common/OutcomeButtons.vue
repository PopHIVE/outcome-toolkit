<script setup lang="ts">
import { OUTCOME_DATA } from "@/stores/OUTCOME_DATA";
import { useNavigationStore } from "@/stores/nav";

const navStore = useNavigationStore();
</script>
<template>
  <div class="outcome-buttons">
    <button
      v-for="{ key, icon, label } in OUTCOME_DATA"
      :key="key"
      class="outcome-button btn border-1 border-black"
      :class="key === navStore.outcome().key ? 'selected btn-info' : 'btn-light'"
      @click="navStore.setOutcome(key)"
      :aria-label="`${label} Outcome button`">
      <img :src="icon" alt="" /><br />
      <strong>{{ label }}</strong>
    </button>
  </div>
</template>
<style>
.outcome-buttons {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr 1fr;
  grid-auto-rows: 1fr;
  justify-items: center;
}
.outcome-button {
  width: 10em;
  height: 10em;
}
</style>
