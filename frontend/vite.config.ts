/** Author: Codex | Modified: 2026-11-21 21:00:00 +08:00 | Shared Remotion runtime deduplication and public assets. */
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  resolve: { dedupe: ["react", "react-dom", "remotion"] },
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/template-assets": "http://127.0.0.1:8000",
      "/media": "http://127.0.0.1:8000",
    },
  },
  build: {
    outDir: "dist",
  },
});
