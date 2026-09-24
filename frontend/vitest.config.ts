import { fileURLToPath } from "node:url";
import { mergeConfig, defineConfig, configDefaults } from "vitest/config";
import viteConfig from "./vite.config.js";

export default defineConfig((configEnv) =>
  mergeConfig(
    viteConfig(configEnv),
    defineConfig({
      test: {
        globals: true,
        mockReset: true,
        environment: "happy-dom",
        exclude: [...configDefaults.exclude, "**/e2e/**"],
        root: fileURLToPath(new URL("./")),
      },
    })
  )
);
