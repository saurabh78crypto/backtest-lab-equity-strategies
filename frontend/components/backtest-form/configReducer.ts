import { DEFAULT_FILTERS, type BacktestConfigRequest, type FilterConfig, type RankingMetric } from "@/lib/types";

export const createInitialConfig = (): BacktestConfigRequest => ({
  name: "",
  start_date: "",
  end_date: "",
  rebalance_frequency: "quarterly",
  portfolio_size: 20,
  position_sizing: "equal_weighted",
  position_sizing_metric: null,
  initial_capital: 1_000_000,
  filters: { ...DEFAULT_FILTERS },
  ranking: { metrics: [{ metric: "roe", order: "descending", weight: 1 }] },
  include_benchmark: true,
  benchmark_symbol: null,
});

export type ConfigAction =
  | { type: "SET_FIELD"; field: keyof BacktestConfigRequest; value: BacktestConfigRequest[keyof BacktestConfigRequest] }
  | { type: "SET_FILTER"; field: keyof FilterConfig; value: FilterConfig[keyof FilterConfig] }
  | { type: "ADD_RANKING_METRIC" }
  | { type: "REMOVE_RANKING_METRIC"; index: number }
  | { type: "UPDATE_RANKING_METRIC"; index: number; patch: Partial<RankingMetric> }
  | { type: "APPLY_PRESET"; config: BacktestConfigRequest }
  | { type: "RESET" };

export function configReducer(state: BacktestConfigRequest, action: ConfigAction): BacktestConfigRequest {
  switch (action.type) {
    case "SET_FIELD":
      return { ...state, [action.field]: action.value };

    case "SET_FILTER":
      return { ...state, filters: { ...state.filters, [action.field]: action.value } };

    case "ADD_RANKING_METRIC":
      return {
        ...state,
        ranking: {
          metrics: [...state.ranking.metrics, { metric: "roce", order: "descending", weight: 1 }],
        },
      };

    case "REMOVE_RANKING_METRIC":
      return {
        ...state,
        ranking: { metrics: state.ranking.metrics.filter((_, i) => i !== action.index) },
      };

    case "UPDATE_RANKING_METRIC":
      return {
        ...state,
        ranking: {
          metrics: state.ranking.metrics.map((m, i) => (i === action.index ? { ...m, ...action.patch } : m)),
        },
      };

    case "APPLY_PRESET":
      return action.config;

    case "RESET":
      return createInitialConfig();

    default:
      return state;
  }
}
