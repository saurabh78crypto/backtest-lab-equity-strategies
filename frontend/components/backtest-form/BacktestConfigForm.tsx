"use client";

import { AlertCircle, Play } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useReducer, useState } from "react"; 

import { BasicsSection } from "@/components/backtest-form/BasicsSection";
import { configReducer, createInitialConfig } from "@/components/backtest-form/configReducer";
import { FiltersSection } from "@/components/backtest-form/FiltersSection";
import { RankingSection } from "@/components/backtest-form/RankingSection";
import { RebalanceSizingSection } from "@/components/backtest-form/RebalanceSizingSection";
import { getFieldErrors, hasFieldErrors, type ConfigFieldErrors } from "@/components/backtest-form/validateConfig";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/States";
import { useBacktestOptions } from "@/hooks/useBacktestOptions";
import { useRunBacktest } from "@/hooks/useRunBacktest";
import { ApiError } from "@/lib/api";

export function BacktestConfigForm() {
  const router = useRouter();
  const { data: options, isLoading: optionsLoading, isError: optionsError } = useBacktestOptions();
  const [config, dispatch] = useReducer(configReducer, undefined, createInitialConfig);
  const [touched, setTouched] = useState<Set<string>>(new Set());
  const runBacktest = useRunBacktest();

  useEffect(() => {
    if (!options) return;
    if (!config.start_date && options.data_start_date) {
      dispatch({ type: "SET_FIELD", field: "start_date", value: options.data_start_date });
    }
    if (!config.end_date && options.data_end_date) {
      dispatch({ type: "SET_FIELD", field: "end_date", value: options.data_end_date });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [options]);

  const fieldErrors = useMemo(
    () => getFieldErrors(config, { start: options?.data_start_date, end: options?.data_end_date }),
    [config, options?.data_start_date, options?.data_end_date]
  );

  const isValid = !hasFieldErrors(fieldErrors);

  function touch(field: string) {
    setTouched((prev) => (prev.has(field) ? prev : new Set(prev).add(field)));
  }

  const visibleErrors: ConfigFieldErrors = useMemo(() => {
    const out: ConfigFieldErrors = {};
    if (touched.has("name")) out.name = fieldErrors.name;
    if (touched.has("start_date")) out.start_date = fieldErrors.start_date;
    if (touched.has("end_date")) out.end_date = fieldErrors.end_date;
    if (touched.has("portfolio_size")) out.portfolio_size = fieldErrors.portfolio_size;
    if (touched.has("initial_capital")) out.initial_capital = fieldErrors.initial_capital;
    if (touched.has("position_sizing_metric")) out.position_sizing_metric = fieldErrors.position_sizing_metric;
    if (touched.has("market_cap_max_cr")) out.market_cap_max_cr = fieldErrors.market_cap_max_cr;

    if (fieldErrors.rankingWeights) {
      const visibleWeights: Record<number, string> = {};
      for (const [indexStr, message] of Object.entries(fieldErrors.rankingWeights)) {
        if (touched.has(`ranking_weight_${indexStr}`)) visibleWeights[Number(indexStr)] = message;
      }
      if (Object.keys(visibleWeights).length > 0) out.rankingWeights = visibleWeights;
    }

    return out;
  }, [fieldErrors, touched]);

  if (optionsLoading) return <LoadingState label="Loading configuration options..." />;
  if (optionsError || !options) {
    return (
      <div className="rounded-md border border-negative/30 bg-negative-soft p-4 text-sm text-negative">
        Couldn&apos;t reach the backtest API. Confirm the backend is running and
        <code className="mx-1 rounded bg-background/40 px-1 py-0.5 font-mono text-2xs">NEXT_PUBLIC_API_BASE_URL</code>
        is set correctly.
      </div>
    );
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isValid) return;

    runBacktest.mutate(config, {
      onSuccess: (result) => {
        router.push(`/runs/${result.run.id}`);
      },
    });
  }

  const apiErrorMessage =
    runBacktest.error instanceof ApiError ? runBacktest.error.message : runBacktest.error ? "Failed to run backtest." : null;

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6 pb-24">
      <BasicsSection
        config={config}
        dispatch={dispatch}
        benchmarkName={options.benchmark_name}
        dataStartDate={options.data_start_date}
        dataEndDate={options.data_end_date}
        errors={visibleErrors}
        touch={touch}
      />
      <RebalanceSizingSection config={config} dispatch={dispatch} options={options} errors={visibleErrors} touch={touch} />
      <FiltersSection config={config} dispatch={dispatch} errors={visibleErrors} touch={touch} />
      <RankingSection config={config} dispatch={dispatch} options={options} errors={visibleErrors} touch={touch} />

      {apiErrorMessage && (
        <div className="flex flex-col gap-2 rounded-md border border-negative/30 bg-negative-soft p-4">
          <div className="flex items-center gap-2 text-sm font-medium text-negative">
            <AlertCircle className="h-4 w-4" />
            The backend rejected this configuration
          </div>
          <p className="ml-6 text-xs text-negative/90">{apiErrorMessage}</p>
        </div>
      )}

      <div className="sticky bottom-0 -mx-4 flex items-center justify-between gap-3 border-t border-border bg-background/95 px-4 py-4 backdrop-blur lg:-mx-8 lg:px-8">
        <p className="text-2xs text-ink-muted">
          {config.ranking.metrics.length} ranking metric{config.ranking.metrics.length !== 1 ? "s" : ""} · top{" "}
          {config.portfolio_size} stocks · {config.rebalance_frequency.replace("_", "-")} rebalancing
        </p>
        <Button type="submit" disabled={!isValid} loading={runBacktest.isPending}>
          <Play className="h-4 w-4" />
          {runBacktest.isPending ? "Running backtest…" : "Run Backtest"}
        </Button>
      </div>
    </form>
  );
}
