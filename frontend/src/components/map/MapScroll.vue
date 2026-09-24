<script setup lang="ts">
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { onMounted, onUnmounted, ref } from "vue";
import { makeCustomControl } from "@/components/map/customControl";

const props = defineProps<{
  position?: L.ControlPosition;
  map: L.Map;
}>();

let loadingTimer: ReturnType<typeof setTimeout>;

const mapScrollRef = ref<undefined | HTMLElement>();
let mapScroll: L.Control;
const mapScrollDistance = 200;

function scrollUp() {
  props.map.panBy([0, -mapScrollDistance]);
}

function scrollDown() {
  props.map.panBy([0, mapScrollDistance]);
}

function scrollLeft() {
  props.map.panBy([-mapScrollDistance, 0]);
}

function scrollRight() {
  props.map.panBy([mapScrollDistance, 0]);
}

onMounted(() => {
  setupComponent();
});

onUnmounted(() => {
  clearTimeout(loadingTimer);
});

function setupComponent() {
  if (!props.map || !mapScrollRef.value) {
    loadingTimer = setTimeout(setupComponent, 250);
    return;
  }
  mapScroll = makeCustomControl(mapScrollRef.value, {
    position: props.position,
  });
  mapScroll.addTo(props.map);
}
</script>

<template>
  <div class="pan-buttons" ref="mapScrollRef">
    <button class="btn btn-sm btn-light" title="Up" aria-label="Scroll map up" @click="scrollUp">
      <i class="bi bi-arrow-up" />
    </button>
    <div class="gap-2">
      <button
        class="btn btn-sm btn-light"
        title="Left"
        aria-label="Scroll map left"
        @click="scrollLeft">
        <i class="bi bi-arrow-left" />
      </button>
      <button
        class="btn btn-sm btn-light"
        title="Right"
        aria-label="Scroll map right"
        @click="scrollRight">
        <i class="bi bi-arrow-right" />
      </button>
    </div>
    <button
      class="btn btn-sm btn-light"
      title="Down"
      aria-label="Scroll map down"
      @click="scrollDown">
      <i class="bi bi-arrow-down" />
    </button>
  </div>
</template>

<style scoped>
.pan-buttons {
  display: grid;
  justify-items: center;
  button {
    /* Match button styling for the Zoom in/out buttons*/
    box-shadow: 0 0 0px 2px rgba(0, 0, 0, 0.2);
    background: white;
    border: none;
    border-radius: 2px;
    margin: 3px;
  }
}
</style>
