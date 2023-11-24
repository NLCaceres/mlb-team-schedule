import { defineConfig } from "vitest/config";
import { svelte, vitePreprocess } from "@sveltejs/vite-plugin-svelte";

export default defineConfig({
  plugins: [
    svelte({ hot: !process.env.VITEST,  preprocess: vitePreprocess() })
  ],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "client/setupTest.ts"
  },
});
