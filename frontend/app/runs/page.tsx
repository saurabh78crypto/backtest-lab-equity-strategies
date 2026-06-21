"use client";

import { Plus } from "lucide-react";
import Link from "next/link";

import { AppShell } from "@/components/layout/AppShell";
import { RunsTable } from "@/components/runs/RunsTable";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/States";
import { useRuns } from "@/hooks/useRuns";

export default function RunHistoryPage() {
  const { data: runs, isLoading, isError } = useRuns();

  return (
    <AppShell title="Run History" subtitle="Every backtest you've run, most recent first">
      <div className="mx-auto max-w-5xl">
        <Card>
          {isLoading && <LoadingState label="Loading run history..." />}
          {isError && <ErrorState description="Couldn't reach the backtest API." />}
          {runs && runs.length === 0 && (
            <EmptyState
              title="No backtests yet"
              description="Configure and run your first strategy to see it here."
              action={
                <Link href="/">
                  <Button size="sm">
                    <Plus className="h-3.5 w-3.5" />
                    New Backtest
                  </Button>
                </Link>
              }
            />
          )}
          {runs && runs.length > 0 && <RunsTable runs={runs} />}
        </Card>
      </div>
    </AppShell>
  );
}
