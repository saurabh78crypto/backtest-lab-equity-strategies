"use client";

import { GitCompare } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { CompareChart } from "@/components/compare/CompareChart";
import { CompareMetricsTable } from "@/components/compare/CompareMetricsTable";
import { RunPicker } from "@/components/compare/RunPicker";
import { Button } from "@/components/ui/Button";
import { ErrorState, LoadingState } from "@/components/ui/States";
import { useCompareRuns } from "@/hooks/useCompareRuns";
import { useRuns } from "@/hooks/useRuns";
import { ApiError } from "@/lib/api";

const MIN_SELECTION = 2;
const MAX_SELECTION = 5;

export default function CompareRunsPage() {
  const { data: runs, isLoading, isError } = useRuns();
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const compare = useCompareRuns();

  function toggle(id: string) {
    setSelectedIds((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id);
      if (prev.length >= MAX_SELECTION) return prev;
      return [...prev, id];
    });
    compare.reset();
  }

  const canCompare = selectedIds.length >= MIN_SELECTION && selectedIds.length <= MAX_SELECTION;

  return (
    <AppShell title="Compare Runs" subtitle="Overlay equity curves and metrics across multiple backtests">
      <div className="mx-auto flex max-w-5xl flex-col gap-6">
        {isLoading && <LoadingState label="Loading runs..." />}
        {isError && <ErrorState description="Couldn't reach the backtest API." />}

        {runs && (
          <>
            <RunPicker runs={runs} selectedIds={selectedIds} onToggle={toggle} />

            <Button
              className="self-start"
              disabled={!canCompare}
              loading={compare.isPending}
              onClick={() => compare.mutate(selectedIds)}
            >
              <GitCompare className="h-4 w-4" />
              Compare {selectedIds.length} runs
            </Button>

            {compare.isError && (
              <div className="rounded-md border border-negative/30 bg-negative-soft p-3 text-xs text-negative">
                {compare.error instanceof ApiError ? compare.error.message : "Failed to compare these runs."}
              </div>
            )}

            {compare.data && (
              <>
                <CompareChart data={compare.data} />
                <CompareMetricsTable data={compare.data} />
              </>
            )}
          </>
        )}
      </div>
    </AppShell>
  );
}
