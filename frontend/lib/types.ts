
// Enums
export type RebalanceFrequency = "monthly" | "quarterly" | "half_yearly" | "yearly";

export type PositionSizingMethod = "equal_weighted" | "market_cap_weighted" | "metric_weighted";

export type RankingOrder = "ascending" | "descending";

export type BacktestStatus = "pending" | "running" | "completed" | "failed";

// Request payloads
export interface FilterConfig {
  market_cap_min_cr?: number | null;
  market_cap_max_cr?: number | null;
  roce_min_pct?: number | null;
  pat_positive: boolean;
  debt_to_equity_max?: number | null;
  roe_min_pct?: number | null;
}

export const DEFAULT_FILTERS: FilterConfig = {
  market_cap_min_cr: null,
  market_cap_max_cr: null,
  roce_min_pct: null,
  pat_positive: false,
  debt_to_equity_max: null,
  roe_min_pct: null,
};

export interface RankingMetric {
  metric: string;
  order: RankingOrder;
  weight: number;
}

export interface RankingConfig {
  metrics: RankingMetric[];
}

export interface BacktestConfigRequest {
  name: string;
  start_date: string; // YYYY-MM-DD
  end_date: string; // YYYY-MM-DD
  rebalance_frequency: RebalanceFrequency;
  portfolio_size: number;
  position_sizing: PositionSizingMethod;
  position_sizing_metric?: string | null;
  initial_capital: number;
  filters: FilterConfig;
  ranking: RankingConfig;
  include_benchmark: boolean;
  benchmark_symbol?: string | null;
}

// Response payloads
export interface BacktestRunSummary {
  id: string;
  name: string;
  status: BacktestStatus;
  created_at: string;
  completed_at?: string | null;
  error_message?: string | null;
}

export interface EquityCurvePoint {
  date: string;
  portfolio_value: number;
  benchmark_value?: number | null;
  drawdown_pct: number;
  daily_return_pct: number;
}

export interface HoldingLog {
  rebalance_date: string;
  next_rebalance_date?: string | null;
  symbol: string;
  rank: number;
  ranking_metric_value?: number | null;
  weight_pct: number;
  shares: number;
  entry_price: number;
  exit_price?: number | null;
  return_pct?: number | null;
  contribution_pct?: number | null;
}

export interface PerformanceMetrics {
  total_return_pct: number;
  cagr_pct: number;
  volatility_pct: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown_pct: number;
  calmar_ratio?: number | null;
  win_rate_pct: number;
  best_period_return_pct?: number | null;
  worst_period_return_pct?: number | null;
  benchmark_total_return_pct?: number | null;
  benchmark_cagr_pct?: number | null;
  benchmark_max_drawdown_pct?: number | null;
  alpha_pct?: number | null;
  beta?: number | null;
}

export interface WinnerLoser {
  symbol: string;
  rebalance_date: string;
  return_pct: number;
}

export interface BacktestRunDetail {
  run: BacktestRunSummary;
  config: Record<string, unknown>;
  metrics?: PerformanceMetrics | null;
  equity_curve: EquityCurvePoint[];
  holdings: HoldingLog[];
  top_winners: WinnerLoser[];
  top_losers: WinnerLoser[];
}

export interface CompareRunsResponse {
  runs: BacktestRunSummary[];
  equity_curves: Record<string, EquityCurvePoint[]>;
  metrics: Record<string, PerformanceMetrics>;
}

// Companies / universe
export interface CompanyOut {
  id: string;
  symbol: string;
  trading_symbol: string;
  name: string;
  sector?: string | null;
  industry?: string | null;
  is_benchmark: boolean;
}

export interface UniverseStats {
  total_companies: number;
  total_price_rows: number;
  total_fundamental_rows: number;
  earliest_price_date?: string | null;
  latest_price_date?: string | null;
  sectors: string[];
}

// Metadata
export interface BacktestOptions {
  rebalance_frequencies: RebalanceFrequency[];
  position_sizing_methods: PositionSizingMethod[];
  ranking_orders: RankingOrder[];
  rankable_metrics: string[];
  filterable_metrics: string[];
  benchmark_symbol: string;
  benchmark_name: string;
  data_start_date?: string | null;
  data_end_date?: string | null;
}

// Prebuilt strategies
export interface PrebuiltStrategy {
  key: string;
  config: BacktestConfigRequest;
}

// UI-facing helper labels
export const METRIC_LABELS: Record<string, string> = {
  roe: "ROE",
  roce: "ROCE",
  roa: "ROA",
  pat: "PAT (Net Profit)",
  revenue: "Revenue",
  eps: "EPS",
  book_value_per_share: "Book Value / Share",
  debt_to_equity: "Debt / Equity",
  current_ratio: "Current Ratio",
  operating_margin: "Operating Margin",
  net_margin: "Net Margin",
  free_cash_flow: "Free Cash Flow",
  market_cap: "Market Cap",
  pe_ratio: "P/E Ratio",
  pb_ratio: "P/B Ratio",
};

export const REBALANCE_LABELS: Record<RebalanceFrequency, string> = {
  monthly: "Monthly",
  quarterly: "Quarterly",
  half_yearly: "Half-Yearly",
  yearly: "Yearly",
};

export const SIZING_LABELS: Record<PositionSizingMethod, string> = {
  equal_weighted: "Equal-Weighted",
  market_cap_weighted: "Market-Cap-Weighted",
  metric_weighted: "Metric-Weighted",
};
