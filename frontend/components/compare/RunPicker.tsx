"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { COMPARE_COLORS } from "@/lib/constants";
import { formatDateTime } from "@/lib/format";
import type { BacktestRunSummary } from "@/lib/types";

const MAX_SELECTION = 5;
const MIN_SELECTION = 2;

export function RunPicker({
  runs,
  selectedIds,
  onToggle,
}: {
  runs: BacktestRunSummary[];
  selectedIds: string[];
  onToggle: (id: string) => void;
}) {
  const completedRuns = runs.filter((r) => r.status === "completed");

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Select Runs to Compare</CardTitle>
          <CardDescription>
            Pick {MIN_SELECTION}–{MAX_SELECTION} completed runs ({selectedIds.length} selected).
          </CardDescription>
        </div>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        {completedRuns.length === 0 && (
          <p className="text-xs text-ink-muted">No completed runs yet — run a backtest first.</p>
        )}
        {completedRuns.map((run) => {
          const selectedIndex = selectedIds.indexOf(run.id);
          const isSelected = selectedIndex !== -1;
          const disabled = !isSelected && selectedIds.length >= MAX_SELECTION;
          return (
            <label
              key={run.id}
              className={`flex cursor-pointer items-center justify-between gap-3 rounded border px-3 py-2.5 transition-colors ${
                isSelected ? "border-accent/40 bg-accent-soft" : "border-border bg-surface-raised hover:border-ink-muted"
              } ${disabled ? "cursor-not-allowed opacity-50" : ""}`}
            >
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={isSelected}
                  disabled={disabled}
                  onChange={() => onToggle(run.id)}
                  className="h-4 w-4 rounded-sm border-border bg-surface text-accent accent-accent"
                />
                <div>
                  <p className="flex items-center gap-2 text-sm text-ink-primary">
                    {isSelected && (
                      <span
                        className="h-2 w-2 rounded-full"
                        style={{ backgroundColor: COMPARE_COLORS[selectedIndex % COMPARE_COLORS.length] }}
                      />
                    )}
                    {run.name}
                  </p>
                  <p className="text-2xs text-ink-muted">{formatDateTime(run.created_at)}</p>
                </div>
              </div>
              <StatusBadge status={run.status} />
            </label>
          );
        })}
      </CardContent>
    </Card>
  );
}
