import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { StatCard } from "@/components/results/StatCard";
import { formatNumber, formatPercent, signColorClass } from "@/lib/format";
import type { PerformanceMetrics } from "@/lib/types";

export function MetricsGrid({ metrics }: { metrics: PerformanceMetrics }) {
  const hasBenchmark = metrics.benchmark_cagr_pct !== null && metrics.benchmark_cagr_pct !== undefined;

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Performance Metrics</CardTitle>
          <CardDescription>Computed on daily portfolio returns over the full backtest window.</CardDescription>
        </div>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          <StatCard label="CAGR" value={formatPercent(metrics.cagr_pct)} valueClassName={signColorClass(metrics.cagr_pct)} />
          <StatCard label="Total Return" value={formatPercent(metrics.total_return_pct)} valueClassName={signColorClass(metrics.total_return_pct)} />
          <StatCard label="Sharpe Ratio" value={formatNumber(metrics.sharpe_ratio)} />
          <StatCard label="Sortino Ratio" value={formatNumber(metrics.sortino_ratio)} />
          <StatCard label="Max Drawdown" value={formatPercent(metrics.max_drawdown_pct, { signed: false })} valueClassName="text-negative" />
          <StatCard label="Volatility (ann.)" value={formatPercent(metrics.volatility_pct, { signed: false })} />
          <StatCard label="Calmar Ratio" value={metrics.calmar_ratio !== null && metrics.calmar_ratio !== undefined ? formatNumber(metrics.calmar_ratio) : "—"} />
          <StatCard label="Win Rate" value={formatPercent(metrics.win_rate_pct, { signed: false })} />
          <StatCard
            label="Best Rebalance Period"
            value={formatPercent(metrics.best_period_return_pct)}
            valueClassName={signColorClass(metrics.best_period_return_pct)}
          />
          <StatCard
            label="Worst Rebalance Period"
            value={formatPercent(metrics.worst_period_return_pct)}
            valueClassName={signColorClass(metrics.worst_period_return_pct)}
          />
        </div>

        {hasBenchmark && (
          <div>
            <p className="mb-2 text-2xs uppercase tracking-wide text-ink-muted">Vs. Benchmark</p>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <StatCard label="Benchmark CAGR" value={formatPercent(metrics.benchmark_cagr_pct)} valueClassName={signColorClass(metrics.benchmark_cagr_pct)} />
              <StatCard
                label="Benchmark Max DD"
                value={formatPercent(metrics.benchmark_max_drawdown_pct, { signed: false })}
                valueClassName="text-negative"
              />
              <StatCard
                label="Alpha (ann.)"
                value={metrics.alpha_pct !== null && metrics.alpha_pct !== undefined ? formatPercent(metrics.alpha_pct) : "—"}
                valueClassName={signColorClass(metrics.alpha_pct)}
              />
              <StatCard label="Beta" value={metrics.beta !== null && metrics.beta !== undefined ? formatNumber(metrics.beta) : "—"} />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
