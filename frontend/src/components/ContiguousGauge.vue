<script setup lang="ts">
import { useSelectionStore } from "@/stores/selection";
import SimpleTooltip from "@/components/common/SimpleTooltip.vue";

const selStore = useSelectionStore();
</script>

<template>
  <div class="contiguity-gauge" :class="{ valid: selStore.contiguous }">
    <h4>
      <div>Contiguity</div>
      <SimpleTooltip
        hasInfoIcon
        text="Selected areas of interest should be contiguous (connected or touching each other) to meet this requirement."
        data-position="bottom"
        minWidth="32em">
        <i class="bi-question-circle-fill"></i>
      </SimpleTooltip>
    </h4>
    <div v-if="selStore.midSelections.size === 0" class="contiguity-text">
      No selected areas <i class="bi-slash-circle"></i>
    </div>
    <div v-else-if="selStore.contiguous" class="contiguity-text">
      Selected areas are contiguous <i class="bi-check-circle-fill"></i>
    </div>
    <div v-else class="contiguity-text">
      Can't have a gap of more than 3.5 miles <i class="bi-exclamation-triangle-fill"></i>
    </div>
  </div>
</template>

<style scoped>
.contiguity-gauge {
  display: grid;
  align-items: center;
  justify-items: end;
  grid-template-columns: auto 1fr;
  margin-right: 0.25rem;
  gap: 0.5rem;

  h4 {
    display: flex;
    flex-wrap: nowrap;
    gap: 0.25rem;
    margin: 0;
    padding: 0;
    text-wrap: none;
  }
  .contiguity-text {
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
    gap: 0.5em;
    justify-items: end;
    margin: 0;
    text-align: right;

    & i {
      color: var(--brand-cool-gray-50);
      font-size: 1.5rem;
    }
  }
  &.valid {
    :is(label, i) {
      color: var(--brand-violet);
    }
  }
}
</style>
