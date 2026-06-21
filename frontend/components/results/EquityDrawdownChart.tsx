"use client";

import { format, parseISO } from "date-fns";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ChartTooltip } from "@/components/results/ChartTooltip";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { CHART_COLORS } from "@/lib/constants";
import { formatCompactINR, formatPercent } from "@/lib/format";
import type { EquityCurvePoint } from "@/lib/types";

function tickDateFormatter(value: string): string {
  try {
    return format(parseISO(value), "MMM yy");
  } catch {
    return value;
  }
}

export function EquityDrawdownChart({
  equityCurve,
  showBenchmark,
}: {
  equityCurve: EquityCurvePoint[];
  showBenchmark: boolean;
}) {
  if (equityCurve.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Equity Curve &amp; Drawdown</CardTitle>
          <CardDescription>Portfolio value over time, with the underwater drawdown panel beneath it.</CardDescription>
        </div>
        {showBenchmark && (
          <div className="flex items-center gap-4 text-2xs text-ink-secondary">
            <span className="flex items-center gap-1.5">
              <span className="h-0.5 w-3 rounded bg-accent" /> Strategy
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-0.5 w-3 rounded bg-benchmark" style={{ borderTop: "1px dashed" }} /> Benchmark
            </span>
          </div>
        )}
      </CardHeader>
      <CardContent className="space-y-1">
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={equityCurve} syncId="equity-drawdown" margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="portfolioFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={CHART_COLORS.portfolio} stopOpacity={0.35} />
                <stop offset="100%" stopColor={CHART_COLORS.portfolio} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke={CHART_COLORS.grid} strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="date"
              tickFormatter={tickDateFormatter}
              tick={{ fontSize: 11, fill: CHART_COLORS.axis }}
              tickLine={false}
              axisLine={{ stroke: CHART_COLORS.grid }}
              minTickGap={48}
            />
            <YAxis
              tickFormatter={(v: number) => formatCompactINR(v)}
              tick={{ fontSize: 11, fill: CHART_COLORS.axis }}
              tickLine={false}
              axisLine={false}
              width={64}
            />
            <Tooltip
              content={(props) => (
                <ChartTooltip
                  active={props.active}
                  label={props.label as string}
                  payload={(props.payload ?? []).map((p) => ({
                    name: p.name as string,
                    value: p.value as number,
                    color: p.color as string,
                  }))}
                  valueFormatter={formatCompactINR}
                />
              )}
            />
            <Area
              type="monotone"
              dataKey="portfolio_value"
              name="Strategy"
              stroke={CHART_COLORS.portfolio}
              strokeWidth={2}
              fill="url(#portfolioFill)"
              dot={false}
              isAnimationActive={false}
            />
            {showBenchmark && (
              <Line
                type="monotone"
                dataKey="benchmark_value"
                name="Benchmark"
                stroke={CHART_COLORS.benchmark}
                strokeWidth={1.5}
                strokeDasharray="4 4"
                dot={false}
                isAnimationActive={false}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>

        <ResponsiveContainer width="100%" height={120}>
          <AreaChart data={equityCurve} syncId="equity-drawdown" margin={{ top: 0, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid stroke={CHART_COLORS.grid} strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="date"
              tickFormatter={tickDateFormatter}
              tick={{ fontSize: 11, fill: CHART_COLORS.axis }}
              tickLine={false}
              axisLine={{ stroke: CHART_COLORS.grid }}
              minTickGap={48}
            />
            <YAxis
              tickFormatter={(v: number) => `${v.toFixed(0)}%`}
              tick={{ fontSize: 11, fill: CHART_COLORS.axis }}
              tickLine={false}
              axisLine={false}
              width={64}
              domain={["auto", 0]}
            />
            <Tooltip
              content={(props) => (
                <ChartTooltip
                  active={props.active}
                  label={props.label as string}
                  payload={(props.payload ?? []).map((p) => ({
                    name: "Drawdown",
                    value: p.value as number,
                    color: CHART_COLORS.negative,
                  }))}
                  valueFormatter={(v) => formatPercent(v, { signed: false })}
                />
              )}
            />
            <Area
              type="monotone"
              dataKey="drawdown_pct"
              name="Drawdown"
              stroke={CHART_COLORS.negative}
              strokeWidth={1.5}
              fill={CHART_COLORS.negative}
              fillOpacity={0.18}
              dot={false}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
