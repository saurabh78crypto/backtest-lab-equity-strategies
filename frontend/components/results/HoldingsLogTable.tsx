"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { useMemo, useState } from "react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Select } from "@/components/ui/Select";
import { Table, Td, Th, Thead, Tr } from "@/components/ui/Table";
import { formatDate, formatPercent, formatShares, formatNumber, signColorClass } from "@/lib/format";
import type { HoldingLog } from "@/lib/types";

export function HoldingsLogTable({ holdings }: { holdings: HoldingLog[] }) {
  const rebalanceDates = useMemo(
    () => Array.from(new Set(holdings.map((h) => h.rebalance_date))).sort(),
    [holdings]
  );
  const [periodIndex, setPeriodIndex] = useState(0);

  if (holdings.length === 0 || rebalanceDates.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Portfolio Log</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-ink-muted">No holdings were generated for this run.</p>
        </CardContent>
      </Card>
    );
  }

  const currentDate = rebalanceDates[periodIndex] ?? rebalanceDates[0];
  const periodHoldings = holdings
    .filter((h) => h.rebalance_date === currentDate)
    .sort((a, b) => a.rank - b.rank);

  return (
    <Card>
      <CardHeader className="flex-col items-start gap-3 sm:flex-row sm:items-center">
        <div>
          <CardTitle>Portfolio Log</CardTitle>
          <CardDescription>Holdings, weights, and realised returns for each rebalance period.</CardDescription>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPeriodIndex((i) => Math.max(0, i - 1))}
            disabled={periodIndex === 0}
            className="flex h-8 w-8 items-center justify-center rounded border border-border text-ink-secondary transition-colors hover:bg-surface-hover disabled:cursor-not-allowed disabled:opacity-40"
            aria-label="Previous rebalance period"
          >
            <ChevronLeft className="h-3.5 w-3.5" />
          </button>
          <Select
            className="w-44"
            value={currentDate}
            onChange={(e) => setPeriodIndex(rebalanceDates.indexOf(e.target.value))}
          >
            {rebalanceDates.map((d, i) => (
              <option key={d} value={d}>
                {formatDate(d)} ({i + 1}/{rebalanceDates.length})
              </option>
            ))}
          </Select>
          <button
            onClick={() => setPeriodIndex((i) => Math.min(rebalanceDates.length - 1, i + 1))}
            disabled={periodIndex === rebalanceDates.length - 1}
            className="flex h-8 w-8 items-center justify-center rounded border border-border text-ink-secondary transition-colors hover:bg-surface-hover disabled:cursor-not-allowed disabled:opacity-40"
            aria-label="Next rebalance period"
          >
            <ChevronRight className="h-3.5 w-3.5" />
          </button>
        </div>
      </CardHeader>
      <Table>
        <Thead>
          <tr>
            <Th align="center">Rank</Th>
            <Th>Symbol</Th>
            <Th align="right">Metric Value</Th>
            <Th align="right">Weight</Th>
            <Th align="right">Shares</Th>
            <Th align="right">Entry Price</Th>
            <Th align="right">Exit Price</Th>
            <Th align="right">Return</Th>
            <Th align="right">Contribution</Th>
          </tr>
        </Thead>
        <tbody>
          {periodHoldings.map((h) => (
            <Tr key={`${h.rebalance_date}-${h.symbol}`}>
              <Td align="center" className="font-mono text-ink-secondary">{h.rank}</Td>
              <Td className="font-mono font-medium">{h.symbol}</Td>
              <Td align="right" className="font-mono text-ink-secondary">{formatNumber(h.ranking_metric_value)}</Td>
              <Td align="right" className="font-mono">{formatPercent(h.weight_pct, { signed: false })}</Td>
              <Td align="right" className="font-mono text-ink-secondary">{formatShares(h.shares)}</Td>
              <Td align="right" className="font-mono">₹{formatNumber(h.entry_price)}</Td>
              <Td align="right" className="font-mono">{h.exit_price !== null && h.exit_price !== undefined ? `₹${formatNumber(h.exit_price)}` : "—"}</Td>
              <Td align="right" className={`font-mono ${signColorClass(h.return_pct)}`}>{formatPercent(h.return_pct)}</Td>
              <Td align="right" className={`font-mono ${signColorClass(h.contribution_pct)}`}>{formatPercent(h.contribution_pct)}</Td>
            </Tr>
          ))}
        </tbody>
      </Table>
    </Card>
  );
}
