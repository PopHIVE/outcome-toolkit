<script setup lang="ts">
const { content, hasInfoIcon, text, minWidth } = defineProps<{
  content?: string;
  text?: string;
  hasInfoIcon?: boolean;
  minWidth?: string;
}>();
</script>

<template>
  <div class="tooltip-container">
    <span class="tooltip__text" :style="`min-width: ${minWidth}`">{{ text }}</span>
    <i v-if="hasInfoIcon" class="bi-question-circle-fill"></i>
    <span v-if="content">{{ content }}</span>
  </div>
</template>

<style scoped>
.tooltip-container {
  position: relative;
  display: inline-flex;
  gap: 0.5rem;
}

.tooltip__text {
  background-color: var(--brand-cool-gray-5);
  border-radius: 2px;
  border: 1px solid var(--brand-cool-gray-50);
  box-shadow: 2px 2px 2px #aaaa;
  color: black;
  font-size: 0.6rem;
  padding: 5px;
  position: absolute;
  text-align: center;
  visibility: hidden;
  white-space: normal;
  z-index: 10000;
}

.tooltip-container:hover .tooltip__text {
  visibility: visible;
}

.tooltip-container[data-position="top"] .tooltip__text {
  inset-block-end: 120%;
  inset-inline-start: 50%;
}

.tooltip-container[data-position="left"] .tooltip__text {
  inset-block-end: 0%;
  inset-inline-end: 110%;
}

.tooltip-container[data-position="right"] .tooltip__text {
  inset-block-end: -62%;
  inset-inline-start: 110%;
  width: 30vh;
}
.tooltip-container[data-position="bottom"] .tooltip__text {
  inset-block-start: 100%;
}

.tooltip-container[data-position="bottom-left"] .tooltip__text {
  inset-block-end: -75%;
  inset-inline-end: 100%;
}

.tooltip-container[data-position="left"]::after .tooltip__text {
  border-color: transparent transparent transparent #5e5d5d;
  inset-block-start: 50%;
  inset-inline-start: 100%;
}

.tooltip-container[data-position="right"]::after .tooltip__text {
  border-color: transparent #5e5d5d transparent transparent;
  inset-block-start: 50%;
  inset-inline-end: 100%;
}

.tooltip-container[data-position="top"]::after .tooltip__text {
  border-color: #5e5d5d transparent transparent transparent;
  inset-block-start: 100%;
  inset-inline-start: 50%;
}

.tooltip-container[data-position="bottom"]::after .tooltip__text {
  border-color: transparent transparent #5e5d5d transparent;
  inset-block-end: 100%;
  inset-inline-start: 50%;
}
.tooltip-container[data-position="bottom-left"]::after .tooltip__text {
  border-color: transparent transparent #5e5d5d transparent;
  inset-block-end: 100%;
  inset-inline-start: 50%;
}
</style>
