<script setup lang="ts">
import { APIV2VersionSpec, type APIV2VersionType } from "@/types";
import { DATA_SOURCE } from "@/util/Consts";
import { useFetch } from "@vueuse/core";
import { onMounted, ref } from "vue";

// The static (Ingest) build has no backend, so skip the version, login, and project features.
const hasBackend = DATA_SOURCE === "api";

const { data: version_data } = useFetch("/version", {
  immediate: hasBackend,
  onFetchError: (ctx) => {
    console.error("Couldn't load application version data.");
    return ctx;
  },
  afterFetch: (ctx) => ({ ...ctx, data: APIV2VersionSpec.check(ctx.data) }),
}).json<APIV2VersionType>();

const isUserLoggedIn = ref(false);
const user = import.meta.env.VITE_PRP_EMAIL;
const headers = new Headers();

// check if user is logged in, if logged in, show projects
function getLoginInfo() {
  // if deployed, header will already have user so we wont need to add it in, for local dev we add in here
  if (user) {
    headers.append("prp-email", user);
  }
  fetch("/protected/api/v2/user", {
    method: "GET",
    headers: headers,
  })
    .then((res) => {
      if (res.status === 401) {
        isUserLoggedIn.value = false;
        return null;
      }
      if (!res.ok) {
        throw res.status + " " + res.statusText;
      }
      return res.json();
    })
    .then((json) => {
      // the user is logged in
      isUserLoggedIn.value = json?.id ? true : false;
    })
    .catch((error) => {
      console.error("Error checking if user is logged in: ", error);
    });
}

onMounted(() => {
  if (hasBackend) getLoginInfo();
});
</script>

<template>
  <nav class="navbar navbar-expand-lg">
    <RouterLink class="nav-item logo" to="/">
      <span class="logo-text" title="Outcome Toolkit Home">Outcome Toolkit</span>
      <label class="screen-reader-only">Home</label>
    </RouterLink>
    <button
      aria-controls="navbarNavContent"
      aria-expanded="false"
      aria-label="Show/hide Navigation"
      class="navbar-toggler"
      data-bs-target="#navbarNavContent"
      data-bs-toggle="collapse"
      type="button">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div
      v-if="version_data"
      class="app-version"
      :title="`v${version_data.version} (#${version_data.tag})\nData: ${version_data.dataVersion}`">
      v{{ version_data.version }}
    </div>
    <div class="collapse navbar-collapse navbar-links" id="navbarNavContent">
      <div class="nav-item">
        <RouterLink to="/">Home</RouterLink>
      </div>
      <div class="nav-item dropdown">
        <a
          class="dropdown-toggle"
          href="#"
          id="aboutDropdown"
          role="button"
          data-bs-toggle="dropdown"
          aria-expanded="false">
          About
        </a>
        <ul class="dropdown-menu" aria-labelledby="aboutDropdown">
          <li class="dropdown-item"><RouterLink to="/about">About Outcome Toolkit</RouterLink></li>
          <li class="dropdown-item"><RouterLink to="/userguide">User Guide</RouterLink></li>
          <li class="dropdown-item"><RouterLink to="/faq">FAQ</RouterLink></li>
          <li class="dropdown-item"><RouterLink to="/aboutdata">About The Data</RouterLink></li>
        </ul>
      </div>
      <div class="nav-item">
        <RouterLink to="/search">Search</RouterLink>
      </div>
      <div class="nav-item">
        <RouterLink to="/results">Results</RouterLink>
      </div>
      <div class="nav-item">
        <RouterLink to="/paymentrates">Payment Rates</RouterLink>
      </div>
      <div class="nav-item">
        <RouterLink to="/healthoutcomes">Health Outcomes</RouterLink>
      </div>

      <div v-if="hasBackend" class="nav-item dropdown">
        <a
          class="dropdown-toggle"
          href="#"
          id="projectDropdown"
          role="button"
          data-bs-toggle="dropdown"
          aria-expanded="false">
          Projects
        </a>
        <ul class="dropdown-menu last" aria-labelledby="aboutDropdown">
          <li class="dropdown-item">
            <RouterLink to="/protected/projects">
              {{ isUserLoggedIn ? "My Projects" : "Log In" }}</RouterLink
            >
          </li>
          <!-- TODO: Move the invite team members to project page after updating with 269 code -->
          <li class="dropdown-item" v-if="isUserLoggedIn">
            <RouterLink to="/invitemember">Invite Team Members</RouterLink>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  background-color: white;
  padding: 0.5rem;
  z-index: 999999;
  box-shadow: 0 2px 2px gray;
}

.navbar-links {
  justify-content: end;
  justify-items: end;
  .nav-item {
    padding: 0.25rem 0.5rem;
    text-wrap: nowrap;
  }
}
@media (min-width: 992px) {
  .nav-item {
    padding: 0rem 1rem;
    &:not(:first-of-type) {
      border-inline-start: 1px solid black;
    }
  }
}
.ws-nowrap {
  white-space: nowrap;
}

.logo-text {
  font-weight: bold;
  font-size: 1.1em;
  white-space: nowrap;
}

.app-version {
  color: var(--brand-cool-gray-70);
  cursor: default;
  font-size: 0.75em;
  padding: 0.25em 1em;
  position: absolute;
  right: 0em;
  top: 0em;
  &:hover {
    color: var(--brand-indigo-light);
  }
}

.last {
  right: 0.5em;
  left: auto;
}

.disabled {
  pointer-events: none; /* Prevent click events */
  opacity: 0.5; /* Make it look disabled */
  cursor: not-allowed; /* Change cursor to indicate disabled state */
}

.errorItem {
  pointer-events: none; /* Prevent click events */
  color: var(--brand-pink);
  cursor: not-allowed; /* Change cursor to indicate disabled state */
  font-style: italic;
}
</style>
