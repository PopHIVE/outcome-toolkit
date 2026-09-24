<script setup lang="ts">
/**
 * A tiny template to help visualize during development what Bootstrap break point you are at.
 */
</script>

<template>
  <button
    class="widther btn btn-sm btn-success d-flex gap-2 position-fixed bottom-0 end-0 m-2 shadow"
    :style="{ zIndex: 10000 }">
    CURRENT PAGE WIDTH:
    <span class="d-block d-sm-none">&lt;sm</span>
    <span class="d-none d-sm-block d-md-none">sm</span>
    <span class="d-none d-md-block d-lg-none">md</span>
    <span class="d-none d-lg-block d-xl-none">lg</span>
    <span class="d-none d-xl-block d-xxl-none">xl</span>
    <span class="d-none d-xxl-block">xxl</span>
  </button>
</template>
