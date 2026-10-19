import { fileURLToPath, URL } from "node:url";

import vue from "@vitejs/plugin-vue";
import vueJsx from "@vitejs/plugin-vue-jsx";
import { defineConfig } from "vite";

export default defineConfig(({ mode }) => {
  return {
    // GitHub Pages serves the site from /<repo>/; set VITE_BASE_PATH when building for it.
    base: process.env.VITE_BASE_PATH ?? "/",
    html: {
      cspNonce: "**CSP_NONCE**",
    },
    plugins: [vue(), vueJsx()],
    preview: {
      allowedHosts: [".us-east-1.elb.amazonaws.com"],
    },
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
      },
    },
  };
});
