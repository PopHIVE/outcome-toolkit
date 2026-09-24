<script setup lang="ts">
import { LOADING_STRING } from "@/util/Consts";
const props = defineProps<{ label?: string }>();
</script>

<template>
  <button
    aria-disabled
    class="loading btn btn-outline-secondary border-0 d-flex gap-1 align-items-center">
    <div class="spinner-border spinner-border-sm" aria-hidden="true"></div>
    <div>{{ props.label ?? LOADING_STRING }}</div>
  </button>
</template>
