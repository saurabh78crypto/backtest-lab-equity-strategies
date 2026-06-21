import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Table, Td, Th, Thead, Tr } from "@/components/ui/Table";
import { formatDate, formatPercent, signColorClass } from "@/lib/format";
import type { WinnerLoser } from "@/lib/types";

function WinnerLoserTable({ rows, emptyLabel }: { rows: WinnerLoser[]; emptyLabel: string }) {
  if (rows.length === 0) {
    return <p className="px-4 py-6 text-center text-xs text-ink-muted">{emptyLabel}</p>;
  }
  return (
    <Table>
      <Thead>
        <tr>
          <Th>Symbol</Th>
          <Th>Rebalance Date</Th>
          <Th align="right">Return</Th>
        </tr>
      </Thead>
      <tbody>
        {rows.map((r, i) => (
          <Tr key={`${r.symbol}-${r.rebalance_date}-${i}`}>
            <Td className="font-mono font-medium">{r.symbol}</Td>
            <Td className="font-mono text-ink-secondary">{formatDate(r.rebalance_date)}</Td>
            <Td align="right" className={`font-mono ${signColorClass(r.return_pct)}`}>
              {formatPercent(r.return_pct)}
            </Td>
          </Tr>
        ))}
      </tbody>
    </Table>
  );
}

export function WinnersLosersPanel({ winners, losers }: { winners: WinnerLoser[]; losers: WinnerLoser[] }) {
  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <div>
            <CardTitle>Top Winners</CardTitle>
            <CardDescription>Best-performing individual holding periods</CardDescription>
          </div>
        </CardHeader>
        <WinnerLoserTable rows={winners} emptyLabel="No closed holdings yet." />
      </Card>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>Top Losers</CardTitle>
            <CardDescription>Worst-performing individual holding periods</CardDescription>
          </div>
        </CardHeader>
        <WinnerLoserTable rows={losers} emptyLabel="No closed holdings yet." />
      </Card>
    </div>
  );
}
