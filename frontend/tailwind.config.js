/** Author: Codex | Modified: 2026-11-21 15:00:00 +08:00 | Motion Studio workspace refresh. */
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        "ms-bg": "#F7F7F9",
        "ms-panel": "#FFFFFF",
        "ms-border": "#E7E7EC",
        "ms-accent": "#8554E8",
        "ms-accent2": "#7042CC",
        "ms-muted": "#777781",
      },
    },
  },
  plugins: [],
};
