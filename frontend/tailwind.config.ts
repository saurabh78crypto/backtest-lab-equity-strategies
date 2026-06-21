import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0B0E14",
        surface: {
          DEFAULT: "#121723",
          hover: "#19202E",
          raised: "#1B2230",
        },
        border: {
          DEFAULT: "#232A39",
          subtle: "#1A202C",
        },
        ink: {
          primary: "#E9EBF1",
          secondary: "#97A0B5",
          muted: "#5C6378",
        },
        accent: {
          DEFAULT: "#D4A24E",
          soft: "#2E2615",
          strong: "#E9C078",
        },
        positive: {
          DEFAULT: "#34C77B",
          soft: "#122A1E",
        },
        negative: {
          DEFAULT: "#E5615A",
          soft: "#2E1717",
        },
        benchmark: "#6C8EEF",
      },
      fontFamily: {
        display: ["var(--font-display)", "system-ui", "sans-serif"],
        body: ["var(--font-body)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      borderRadius: {
        sm: "4px",
        DEFAULT: "6px",
        md: "8px",
        lg: "10px",
      },
      boxShadow: {
        panel: "0 1px 2px rgba(0,0,0,0.4)",
      },
      fontSize: {
        "2xs": ["0.6875rem", { lineHeight: "1rem" }],
      },
    },
  },
  plugins: [],
};

export default config;
