import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Table, Td, Th, Thead, Tr } from "@/components/ui/Table";
import { COMPARE_COLORS } from "@/lib/constants";
import { formatNumber, formatPercent, signColorClass } from "@/lib/format";
import type { CompareRunsResponse } from "@/lib/types";

export function CompareMetricsTable({ data }: { data: CompareRunsResponse }) {
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Metrics Comparison</CardTitle>
          <CardDescription>Side-by-side performance scorecard for the selected runs.</CardDescription>
        </div>
      </CardHeader>
      <Table>
        <Thead>
          <tr>
            <Th>Run</Th>
            <Th align="right">CAGR</Th>
            <Th align="right">Total Return</Th>
            <Th align="right">Sharpe</Th>
            <Th align="right">Sortino</Th>
            <Th align="right">Max DD</Th>
            <Th align="right">Volatility</Th>
            <Th align="right">Win Rate</Th>
          </tr>
        </Thead>
        <tbody>
          {data.runs.map((run, i) => {
            const m = data.metrics[run.id];
            if (!m) return null;
            return (
              <Tr key={run.id}>
                <Td>
                  <span className="flex items-center gap-2 font-medium text-ink-primary">
                    <span
                      className="h-2 w-2 rounded-full"
                      style={{ backgroundColor: COMPARE_COLORS[i % COMPARE_COLORS.length] }}
                    />
                    {run.name}
                  </span>
                </Td>
                <Td align="right" className={`font-mono ${signColorClass(m.cagr_pct)}`}>{formatPercent(m.cagr_pct)}</Td>
                <Td align="right" className={`font-mono ${signColorClass(m.total_return_pct)}`}>{formatPercent(m.total_return_pct)}</Td>
                <Td align="right" className="font-mono">{formatNumber(m.sharpe_ratio)}</Td>
                <Td align="right" className="font-mono">{formatNumber(m.sortino_ratio)}</Td>
                <Td align="right" className="font-mono text-negative">{formatPercent(m.max_drawdown_pct, { signed: false })}</Td>
                <Td align="right" className="font-mono">{formatPercent(m.volatility_pct, { signed: false })}</Td>
                <Td align="right" className="font-mono">{formatPercent(m.win_rate_pct, { signed: false })}</Td>
              </Tr>
            );
          })}
        </tbody>
      </Table>
    </Card>
  );
}
