<script setup lang="ts">
/**
 * IconButton encapsulates a button with an icon either directly before ("leftIcon") or after ("rightIcon")
 *    the label, or alone on a line before the label ("topIcon") or below ("bottomIcon")
 * Icons are specified via their HTML class, for example:
 *    <IconButton leftIcon="bi-heart-fill">Heart Me!</IconButton>
 * This also allows you to include class-based directives a la bootstrap:
 *    <IconButton leftIcon="bi-heart-fill icon-xl text-primary" rightIcon="bi-balloon-heart text-danger" >Heart Me!</IconButton>
 * The button's bootstrap variant (e.g. "btn-outline-primary") and other classes can be set on the button itself:
 *    <IconButton class="btn-warning mt-2" leftIcon="bi-heart-fill">Heart Me!</IconButton>
 *
 */

const { bottomIcon, leftIcon, rightIcon, topIcon } = defineProps<{
  bottomIcon?: string;
  leftIcon?: string;
  rightIcon?: string;
  topIcon?: string;
}>();

const buttonClass = ["icon-btn", "btn"];
</script>

<template>
  <button :class="buttonClass">
    <i v-show="!!topIcon" :class="['t', topIcon]"></i>
    <i v-show="!!leftIcon" :class="['s', leftIcon]"></i>
    <div class="l"><slot></slot></div>
    <i v-show="!!rightIcon" :class="['e', rightIcon]"></i>
    <i v-show="!!bottomIcon" :class="['b', bottomIcon]"></i>
  </button>
</template>

<style>
.icon-btn {
  display: grid;
  align-content: center;
  gap: 0 0.5em;
  grid-template-areas:
    "t t t"
    "s l e"
    "b b b";
  justify-content: center;
  div.l {
    grid-area: l;
    align-self: center;
  }
  i.t {
    grid-area: t;
  }
  i.s {
    grid-area: s;
  }
  i.e {
    grid-area: e;
  }
  i.b {
    grid-area: b;
  }
}
</style>
