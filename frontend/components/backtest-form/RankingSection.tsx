"use client";

import { Plus, X } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { NumberInput } from "@/components/ui/Field";
import { Select } from "@/components/ui/Select";
import type { ConfigAction } from "@/components/backtest-form/configReducer";
import type { ConfigFieldErrors } from "@/components/backtest-form/validateConfig";
import { METRIC_LABELS } from "@/lib/types";
import type { BacktestConfigRequest, BacktestOptions } from "@/lib/types";

const MAX_RANKING_METRICS = 5;

interface Props {
  config: BacktestConfigRequest;
  dispatch: React.Dispatch<ConfigAction>;
  options: BacktestOptions;
  errors: ConfigFieldErrors;
  touch: (field: string) => void;
}

export function RankingSection({ config, dispatch, options, errors, touch }: Props) {
  const { metrics } = config.ranking;
  const isComposite = metrics.length > 1;
  const atLimit = metrics.length >= MAX_RANKING_METRICS;

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Ranking</CardTitle>
          <CardDescription>
            {isComposite
              ? "Composite rank — each metric below ranks the eligible universe, then ranks are averaged (weighted) into one score."
              : "Stocks are ranked on a single metric. Add another to build a composite, weighted rank."}
          </CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        <ol className="flex flex-col gap-3">
          {metrics.map((metric, index) => {
            const weightError = isComposite ? errors.rankingWeights?.[index] : undefined;
            return (
              <li
                key={index}
                className="flex flex-col gap-3 rounded border border-border bg-surface-raised p-3 sm:flex-row sm:items-end"
              >
                <span className="flex h-7 w-7 shrink-0 items-center justify-center self-start rounded-full border border-accent/40 bg-accent-soft font-mono text-xs text-accent sm:self-end sm:mb-0.5">
                  {index + 1}
                </span>

                <div className="grid flex-1 grid-cols-1 gap-3 sm:grid-cols-3">
                  <div>
                    <label className="mb-1.5 block text-2xs font-medium text-ink-secondary">Metric</label>
                    <Select
                      value={metric.metric}
                      onChange={(e) =>
                        dispatch({ type: "UPDATE_RANKING_METRIC", index, patch: { metric: e.target.value } })
                      }
                    >
                      {options.rankable_metrics.map((m) => (
                        <option key={m} value={m}>
                          {METRIC_LABELS[m] ?? m}
                        </option>
                      ))}
                    </Select>
                  </div>

                  <div>
                    <label className="mb-1.5 block text-2xs font-medium text-ink-secondary">Order</label>
                    <Select
                      value={metric.order}
                      onChange={(e) =>
                        dispatch({
                          type: "UPDATE_RANKING_METRIC",
                          index,
                          patch: { order: e.target.value as "ascending" | "descending" },
                        })
                      }
                    >
                      <option value="descending">Descending (higher is better)</option>
                      <option value="ascending">Ascending (lower is better)</option>
                    </Select>
                  </div>

                  <div>
                    <label className="mb-1.5 block text-2xs font-medium text-ink-secondary">
                      Weight {isComposite && "in composite"}
                    </label>
                    <NumberInput
                      min={0.1}
                      step={0.1}
                      disabled={!isComposite}
                      value={metric.weight}
                      onChange={(value) =>
                        dispatch({ type: "UPDATE_RANKING_METRIC", index, patch: { weight: value ?? 1 } })
                      }
                      onBlur={() => touch(`ranking_weight_${index}`)}
                    />
                    {isComposite ? (
                      weightError && <p className="mt-1 text-2xs text-negative">{weightError}</p>
                    ) : (
                      <p className="mt-1 text-2xs text-ink-muted">
                        Only used once you&apos;re combining multiple metrics
                      </p>
                    )}
                  </div>
                </div>

                <button
                  type="button"
                  disabled={metrics.length === 1}
                  onClick={() => dispatch({ type: "REMOVE_RANKING_METRIC", index })}
                  className="flex h-8 w-8 shrink-0 items-center justify-center self-start rounded text-ink-muted transition-colors hover:bg-negative-soft hover:text-negative disabled:cursor-not-allowed disabled:opacity-30 sm:self-end"
                  aria-label="Remove metric"
                >
                  <X className="h-4 w-4" />
                </button>
              </li>
            );
          })}
        </ol>

        <div className="mt-3 flex items-center gap-3">
          <Button
            type="button"
            variant="secondary"
            size="sm"
            disabled={atLimit}
            onClick={() => dispatch({ type: "ADD_RANKING_METRIC" })}
          >
            <Plus className="h-3.5 w-3.5" />
            Add ranking metric
          </Button>
          <span className="text-2xs text-ink-muted">
            {metrics.length} / {MAX_RANKING_METRICS}
            {atLimit ? " — limit reached" : ""}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
