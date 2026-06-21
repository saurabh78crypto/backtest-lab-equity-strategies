"use client";

import { useMemo } from "react";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { COMPARE_COLORS, CHART_COLORS } from "@/lib/constants";
import type { BacktestRunSummary, CompareRunsResponse } from "@/lib/types";

function buildIndexedRows(data: CompareRunsResponse) {
  const seriesByRun = data.runs.map((run) => data.equity_curves[run.id] ?? []);
  const maxLen = Math.max(0, ...seriesByRun.map((s) => s.length));
  const rows: Record<string, number>[] = [];

  for (let i = 0; i < maxLen; i++) {
    const row: Record<string, number> = { index: i };
    data.runs.forEach((run) => {
      const series = data.equity_curves[run.id];
      const base = series?.[0]?.portfolio_value;
      const point = series?.[i];
      if (base && point) {
        row[run.id] = (point.portfolio_value / base) * 100;
      }
    });
    rows.push(row);
  }
  return rows;
}

export function CompareChart({ data }: { data: CompareRunsResponse }) {
  const rows = useMemo(() => buildIndexedRows(data), [data]);

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Indexed Equity Curves</CardTitle>
          <CardDescription>Each run indexed to 100 at its own start date, plotted by trading days elapsed.</CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={340}>
          <LineChart data={rows} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid stroke={CHART_COLORS.grid} strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="index"
              tick={{ fontSize: 11, fill: CHART_COLORS.axis }}
              tickLine={false}
              axisLine={{ stroke: CHART_COLORS.grid }}
              label={{ value: "Trading days since start", position: "insideBottom", offset: -4, fontSize: 11, fill: CHART_COLORS.axis }}
            />
            <YAxis
              tick={{ fontSize: 11, fill: CHART_COLORS.axis }}
              tickLine={false}
              axisLine={false}
              width={48}
              tickFormatter={(v: number) => v.toFixed(0)}
            />
            <Tooltip
              contentStyle={{ background: "#1B2230", border: "1px solid #232A39", borderRadius: 6, fontSize: 12 }}
              labelFormatter={(v) => `Day ${v}`}
              formatter={(value: number, key: string) => {
                const run = data.runs.find((r) => r.id === key);
                return [value.toFixed(1), run?.name ?? key];
              }}
            />
            <Legend
              formatter={(key) => data.runs.find((r) => r.id === key)?.name ?? key}
              wrapperStyle={{ fontSize: 12 }}
            />
            {data.runs.map((run: BacktestRunSummary, i: number) => (
              <Line
                key={run.id}
                type="monotone"
                dataKey={run.id}
                name={run.id}
                stroke={COMPARE_COLORS[i % COMPARE_COLORS.length]}
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
                connectNulls
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
