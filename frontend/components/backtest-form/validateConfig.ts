import type { BacktestConfigRequest } from "@/lib/types";

export interface ConfigFieldErrors {
  name?: string;
  start_date?: string;
  end_date?: string;
  portfolio_size?: string;
  initial_capital?: string;
  position_sizing_metric?: string;
  market_cap_max_cr?: string;
  ranking?: string;
  rankingWeights?: Record<number, string>;
}

export interface DataBounds {
  start?: string | null;
  end?: string | null;
}

export function getFieldErrors(config: BacktestConfigRequest, dataBounds?: DataBounds): ConfigFieldErrors {
  const errors: ConfigFieldErrors = {};

  if (!config.name.trim()) errors.name = "Give the strategy a name.";

  if (!config.start_date) errors.start_date = "Pick a start date.";
  if (!config.end_date) errors.end_date = "Pick an end date.";
  if (config.start_date && config.end_date && config.end_date <= config.start_date) {
    errors.end_date = "Must be after the start date.";
  }

  const dataStart = dataBounds?.start;
  const dataEnd = dataBounds?.end;
  if (!errors.start_date && config.start_date && dataStart && config.start_date < dataStart) {
    errors.start_date = `No usable data before ${dataStart} (not every company has reported yet).`;
  }
  if (!errors.end_date && config.end_date && dataEnd && config.end_date > dataEnd) {
    errors.end_date = `No price data after ${dataEnd}.`;
  }

  if (config.portfolio_size === null || config.portfolio_size === undefined) {
    errors.portfolio_size = "Required.";
  } else if (config.portfolio_size < 1 || config.portfolio_size > 200) {
    errors.portfolio_size = "Must be between 1 and 200 stocks.";
  }

  if (config.initial_capital === null || config.initial_capital === undefined) {
    errors.initial_capital = "Required.";
  } else if (config.initial_capital <= 0) {
    errors.initial_capital = "Must be greater than zero.";
  }

  if (config.position_sizing === "metric_weighted" && !config.position_sizing_metric) {
    errors.position_sizing_metric = "Pick a metric to weight positions by.";
  }

  const { market_cap_min_cr, market_cap_max_cr } = config.filters;
  if (
    market_cap_min_cr !== null &&
    market_cap_min_cr !== undefined &&
    market_cap_max_cr !== null &&
    market_cap_max_cr !== undefined &&
    market_cap_min_cr > market_cap_max_cr
  ) {
    errors.market_cap_max_cr = "Can't be less than the minimum.";
  }

  if (config.ranking.metrics.length === 0) {
    errors.ranking = "Add at least one ranking metric.";
  } else {
    const rankingWeights: Record<number, string> = {};
    config.ranking.metrics.forEach((m, i) => {
      if (!m.weight || m.weight <= 0) rankingWeights[i] = "Must be greater than zero.";
    });
    if (Object.keys(rankingWeights).length > 0) errors.rankingWeights = rankingWeights;
  }

  return errors;
}

export function hasFieldErrors(errors: ConfigFieldErrors): boolean {
  return Object.keys(errors).length > 0;
}
