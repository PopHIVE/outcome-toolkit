import "bootstrap";

import "bootstrap-icons/font/bootstrap-icons.scss";
import "bootstrap/dist/css/bootstrap.min.css";
import "@fontsource/poppins";
import "@fontsource/public-sans";

// Add our custom styling and colors
import "@/theme.css";

import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "@/App.vue";
import router from "@/router";
import { doFetches } from "@/stores/fetching";

const app = createApp(App);

app.use(createPinia());
app.use(router);

app.mount("#app");
doFetches();
