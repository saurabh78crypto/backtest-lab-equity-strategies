export const CHART_COLORS = {
  portfolio: "#D4A24E",
  portfolioFill: "rgba(212, 162, 78, 0.16)",
  benchmark: "#6C8EEF",
  positive: "#34C77B",
  negative: "#E5615A",
  grid: "#232A39",
  axis: "#5C6378",
} as const;

export const NAV_ITEMS = [
  { href: "/", label: "New Backtest" },
  { href: "/runs", label: "Run History" },
  { href: "/strategies", label: "Prebuilt Strategies" },
  { href: "/compare", label: "Compare Runs" },
] as const;

export const COMPARE_COLORS = ["#D4A24E", "#6C8EEF", "#34C77B", "#C77DD4", "#E5915A"] as const;
