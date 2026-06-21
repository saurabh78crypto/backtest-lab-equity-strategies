"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Field, NumberInput } from "@/components/ui/Field";
import { Select } from "@/components/ui/Select";
import type { ConfigAction } from "@/components/backtest-form/configReducer";
import type { ConfigFieldErrors } from "@/components/backtest-form/validateConfig";
import { METRIC_LABELS, REBALANCE_LABELS, SIZING_LABELS } from "@/lib/types";
import type { BacktestConfigRequest, BacktestOptions } from "@/lib/types";

interface Props {
  config: BacktestConfigRequest;
  dispatch: React.Dispatch<ConfigAction>;
  options: BacktestOptions;
  errors: ConfigFieldErrors;
  touch: (field: string) => void;
}

export function RebalanceSizingSection({ config, dispatch, options, errors, touch }: Props) {
  const isMetricWeighted = config.position_sizing === "metric_weighted";

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Rebalancing &amp; Position Sizing</CardTitle>
          <CardDescription>How often the portfolio turns over, how many stocks it holds, and how capital is split.</CardDescription>
        </div>
      </CardHeader>
      <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Field label="Rebalance frequency" htmlFor="rebalance_frequency" required>
          <Select
            id="rebalance_frequency"
            value={config.rebalance_frequency}
            onChange={(e) =>
              dispatch({ type: "SET_FIELD", field: "rebalance_frequency", value: e.target.value as BacktestConfigRequest["rebalance_frequency"] })
            }
          >
            {options.rebalance_frequencies.map((f) => (
              <option key={f} value={f}>
                {REBALANCE_LABELS[f]}
              </option>
            ))}
          </Select>
        </Field>

        <Field
          label="Portfolio size"
          htmlFor="portfolio_size"
          required
          hint="Number of stocks held, e.g. top 20"
          error={errors.portfolio_size}
        >
          <NumberInput
            id="portfolio_size"
            min={1}
            max={200}
            suffix="stocks"
            value={config.portfolio_size}
            onChange={(value) => dispatch({ type: "SET_FIELD", field: "portfolio_size", value: value ?? 1 })}
            onBlur={() => touch("portfolio_size")}
          />
        </Field>

        <Field label="Position sizing" htmlFor="position_sizing" required>
          <Select
            id="position_sizing"
            value={config.position_sizing}
            onChange={(e) => {
              const value = e.target.value as BacktestConfigRequest["position_sizing"];
              dispatch({ type: "SET_FIELD", field: "position_sizing", value });
              if (value !== "metric_weighted") {
                dispatch({ type: "SET_FIELD", field: "position_sizing_metric", value: null });
              }
            }}
          >
            {options.position_sizing_methods.map((m) => (
              <option key={m} value={m}>
                {SIZING_LABELS[m]}
              </option>
            ))}
          </Select>
        </Field>

        <Field
          label="Weighting metric"
          htmlFor="position_sizing_metric"
          required={isMetricWeighted}
          hint={isMetricWeighted ? undefined : "Only used for metric-weighted sizing"}
          error={errors.position_sizing_metric}
        >
          <Select
            id="position_sizing_metric"
            disabled={!isMetricWeighted}
            value={config.position_sizing_metric ?? ""}
            onChange={(e) => dispatch({ type: "SET_FIELD", field: "position_sizing_metric", value: e.target.value || null })}
            onBlur={() => touch("position_sizing_metric")}
          >
            <option value="">Select a metric…</option>
            {options.rankable_metrics.map((m) => (
              <option key={m} value={m}>
                {METRIC_LABELS[m] ?? m}
              </option>
            ))}
          </Select>
        </Field>
      </CardContent>
    </Card>
  );
}
