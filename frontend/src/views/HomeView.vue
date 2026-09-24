<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();
</script>

<template>
  <main class="home-main" id="welcome">
    <div class="home-title">
      <h1>Welcome to the Outcome Toolkit</h1>
    </div>
    <h2>Establish a baseline for Outcome Toolkit participation</h2>
    <section>
      <h3>
        <div class="number-badge home-bullet">1</div>
        Select an outcome
      </h3>
      <h3>
        <div class="number-badge home-bullet">2</div>
        Define an area of focus
      </h3>
      <h3>
        <div class="number-badge home-bullet">3</div>
        Evaluate area suitability
      </h3>
      <h3>
        <div class="number-badge home-bullet">4</div>
        Export defined target area
      </h3>
    </section>
    <button class="btn btn-info" aria-label="Get Started button" @click="router.push('/search')">
      Get Started
    </button>
  </main>
</template>

<style scoped>
h1,
h2 {
  text-align: center;
}
.home-main {
  align-items: center;
  background-color: var(--brand-cool-gray-10);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 2em;
  justify-content: center;
  justify-items: center;
  padding: 2em;
  height: calc(100vh - 7rem + 6px);
  width: 100%;
}
.home-title {
  align-items: center;
  background-color: var(--brand-cool-gray-10);
  display: flex;
  flex-direction: row;
  gap: 1em;
  justify-content: center;
  justify-items: center;
}
.home-image {
  height: 7em;
  width: 7.5em;
  justify-content: center;
}
.home-bullet {
  background: var(--brand-violet);
  color: white;
}
</style>
