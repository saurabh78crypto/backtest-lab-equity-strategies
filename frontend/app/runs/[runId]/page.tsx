"use client";

import { AppShell } from "@/components/layout/AppShell";
import { ResultsView } from "@/components/results/ResultsView";
import { ErrorState, LoadingState } from "@/components/ui/States";
import { useRun } from "@/hooks/useRun";
import { ApiError } from "@/lib/api";

export default function RunDetailPage({ params }: { params: { runId: string } }) {
  const { data, isLoading, isError, error } = useRun(params.runId);

  return (
    <AppShell title="Backtest Results" subtitle={data ? data.run.name : "Loading run..."}>
      <div className="mx-auto max-w-6xl">
        {isLoading && <LoadingState label="Loading backtest results..." />}
        {isError && (
          <ErrorState
            title="Couldn't load this run"
            description={error instanceof ApiError ? error.message : "It may have been deleted, or the backend is unreachable."}
          />
        )}
        {data && <ResultsView result={data} />}
      </div>
    </AppShell>
  );
}
