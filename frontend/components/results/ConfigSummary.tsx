import { Badge } from "@/components/ui/Badge";
import { formatDate } from "@/lib/format";
import { METRIC_LABELS, REBALANCE_LABELS, SIZING_LABELS } from "@/lib/types";
import type { BacktestConfigRequest } from "@/lib/types";

export function ConfigSummary({ config }: { config: Record<string, unknown> }) {
  const cfg = config as unknown as BacktestConfigRequest;

  const filterBadges: string[] = [];
  if (cfg.filters?.market_cap_min_cr) filterBadges.push(`Mkt Cap ≥ ₹${cfg.filters.market_cap_min_cr} Cr`);
  if (cfg.filters?.market_cap_max_cr) filterBadges.push(`Mkt Cap ≤ ₹${cfg.filters.market_cap_max_cr} Cr`);
  if (cfg.filters?.roce_min_pct) filterBadges.push(`ROCE > ${cfg.filters.roce_min_pct}%`);
  if (cfg.filters?.roe_min_pct) filterBadges.push(`ROE > ${cfg.filters.roe_min_pct}%`);
  if (cfg.filters?.debt_to_equity_max) filterBadges.push(`D/E ≤ ${cfg.filters.debt_to_equity_max}`);
  if (cfg.filters?.pat_positive) filterBadges.push("PAT > 0");

  return (
    <div className="flex flex-col gap-3 text-xs text-ink-secondary">
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 font-mono">
        <span>{formatDate(cfg.start_date)} → {formatDate(cfg.end_date)}</span>
        <span>{REBALANCE_LABELS[cfg.rebalance_frequency] ?? cfg.rebalance_frequency} rebalancing</span>
        <span>Top {cfg.portfolio_size}</span>
        <span>{SIZING_LABELS[cfg.position_sizing] ?? cfg.position_sizing}{cfg.position_sizing_metric ? ` (${METRIC_LABELS[cfg.position_sizing_metric] ?? cfg.position_sizing_metric})` : ""}</span>
      </div>

      {filterBadges.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {filterBadges.map((b) => (
            <Badge key={b} tone="neutral">{b}</Badge>
          ))}
        </div>
      )}

      <div className="flex flex-wrap gap-1.5">
        {cfg.ranking?.metrics?.map((m, i) => (
          <Badge key={`${m.metric}-${i}`} tone="accent">
            {METRIC_LABELS[m.metric] ?? m.metric} {m.order === "ascending" ? "↑" : "↓"}
            {cfg.ranking.metrics.length > 1 ? ` ×${m.weight}` : ""}
          </Badge>
        ))}
      </div>
    </div>
  );
}
