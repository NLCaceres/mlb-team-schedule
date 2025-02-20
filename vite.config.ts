import { defineConfig } from "vite";
import { svelte, vitePreprocess } from "@sveltejs/vite-plugin-svelte";

export default defineConfig({
  plugins: [svelte({
    preprocess: vitePreprocess()
  })],
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    rollupOptions: {
      output: { // Outputs to "/dist", as "/dist/assets/..."
        assetFileNames: "assets/[name][extname]",
        entryFileNames: "assets/[name].js"
      }
    }
  }
});
