"use client";

import { formatDate } from "@/lib/format";

interface TooltipPayloadItem {
  name: string;
  value: number;
  color: string;
  unit?: string;
}

export function ChartTooltip({
  active,
  label,
  payload,
  valueFormatter,
}: {
  active?: boolean;
  label?: string;
  payload?: TooltipPayloadItem[];
  valueFormatter: (value: number) => string;
}) {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className="rounded border border-border bg-surface-raised px-3 py-2 shadow-panel">
      <p className="mb-1 font-mono text-2xs text-ink-muted">{formatDate(label)}</p>
      {payload.map((item) => (
        <p key={item.name} className="flex items-center gap-2 font-mono text-xs text-ink-primary">
          <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: item.color }} />
          {item.name}: {valueFormatter(item.value)}
        </p>
      ))}
    </div>
  );
}
