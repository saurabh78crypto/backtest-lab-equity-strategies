import { ConfigSummary } from "@/components/results/ConfigSummary";
import { EquityDrawdownChart } from "@/components/results/EquityDrawdownChart";
import { ExportMenu } from "@/components/results/ExportMenu";
import { HoldingsLogTable } from "@/components/results/HoldingsLogTable";
import { MetricsGrid } from "@/components/results/MetricsGrid";
import { WinnersLosersPanel } from "@/components/results/WinnersLosersPanel";
import { Card, CardContent } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatDateTime } from "@/lib/format";
import type { BacktestRunDetail } from "@/lib/types";

export function ResultsView({ result }: { result: BacktestRunDetail }) {
  const { run, config, metrics, equity_curve, holdings, top_winners, top_losers } = result;
  const hasBenchmark = equity_curve.some((p) => p.benchmark_value !== null && p.benchmark_value !== undefined);

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardContent className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-2.5">
              <h2 className="font-display text-lg font-semibold text-ink-primary">{run.name}</h2>
              <StatusBadge status={run.status} />
            </div>
            <p className="mt-1 text-2xs text-ink-muted">
              Run {formatDateTime(run.created_at)}
              {run.completed_at ? ` · completed ${formatDateTime(run.completed_at)}` : ""}
            </p>
            <div className="mt-3">
              <ConfigSummary config={config} />
            </div>
          </div>
          <ExportMenu runId={run.id} />
        </CardContent>
      </Card>

      {run.status === "failed" && (
        <div className="rounded-md border border-negative/30 bg-negative-soft p-4 text-sm text-negative">
          {run.error_message ?? "This backtest failed to complete."}
        </div>
      )}

      {metrics && <MetricsGrid metrics={metrics} />}

      {equity_curve.length > 0 && <EquityDrawdownChart equityCurve={equity_curve} showBenchmark={hasBenchmark} />}

      {(top_winners.length > 0 || top_losers.length > 0) && (
        <WinnersLosersPanel winners={top_winners} losers={top_losers} />
      )}

      <HoldingsLogTable holdings={holdings} />
    </div>
  );
}
