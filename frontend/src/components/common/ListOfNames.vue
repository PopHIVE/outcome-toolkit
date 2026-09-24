<script lang="ts" setup>
import { ref } from "vue";

const props = defineProps<{ names: string[]; postText?: string; preText?: string }>();
const open = ref(false);
const toggle = () => {
  open.value = !open.value;
};
</script>

<template>
  <div v-if="props.names.length < 6" class="list-of-areas">
    <template v-if="props.preText">{{ props.preText }}</template>
    {{ props.names.join(", ") }}
    <template v-if="props.postText">{{ props.postText }}</template>
  </div>
  <div v-else class="list-of-names">
    <template v-if="props.preText">{{ props.preText }}</template>
    <template v-if="open">
      {{ props.names.join(", ") }}

      <button @click="toggle" class="btn btn-link">(collapse)</button>
    </template>
    <template v-else>
      {{ props.names.slice(0, 4).join(", ") }}, and
      <button @click="toggle" class="btn btn-link">{{ props.names.length - 4 }} more</button>
    </template>
    <template v-if="props.postText">{{ props.postText }}</template>
  </div>
</template>
<style scoped>
.list-of-names {
  display: inline-flex;
  align-items: first baseline;
  button {
    padding-left: 0.25em;
  }
}
</style>
