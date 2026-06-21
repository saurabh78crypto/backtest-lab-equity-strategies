"use client";

import { useRouter } from "next/navigation";

import { AppShell } from "@/components/layout/AppShell";
import { StrategyCard } from "@/components/strategies/StrategyCard";
import { ErrorState, LoadingState } from "@/components/ui/States";
import { usePrebuiltStrategies } from "@/hooks/usePrebuiltStrategies";
import { useRunPrebuiltStrategy } from "@/hooks/useRunPrebuiltStrategy";
import { ApiError } from "@/lib/api";

export default function PrebuiltStrategiesPage() {
  const router = useRouter();
  const { data: strategies, isLoading, isError } = usePrebuiltStrategies();
  const runStrategy = useRunPrebuiltStrategy();

  function handleRun(key: string) {
    runStrategy.mutate(key, {
      onSuccess: (result) => router.push(`/runs/${result.run.id}`),
    });
  }

  return (
    <AppShell title="Prebuilt Strategies" subtitle="Ready-made strategy configs you can run with one click">
      <div className="mx-auto max-w-5xl">
        {isLoading && <LoadingState label="Loading prebuilt strategies..." />}
        {isError && <ErrorState description="Couldn't reach the backtest API." />}
        {runStrategy.isError && (
          <div className="mb-4 rounded-md border border-negative/30 bg-negative-soft p-3 text-xs text-negative">
            {runStrategy.error instanceof ApiError ? runStrategy.error.message : "Failed to run this strategy."}
          </div>
        )}
        {strategies && (
          <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
            {strategies.map((strategy) => (
              <StrategyCard
                key={strategy.key}
                strategy={strategy}
                onRun={handleRun}
                isRunning={runStrategy.isPending && runStrategy.variables === strategy.key}
              />
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
