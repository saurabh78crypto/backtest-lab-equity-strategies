"use client";

import { Play } from "lucide-react";

import { ConfigSummary } from "@/components/results/ConfigSummary";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import type { PrebuiltStrategy } from "@/lib/types";

const STRATEGY_TITLES: Record<string, string> = {
  quality_roce: "Quality — High ROCE",
  value_pe: "Value — Low PE",
  composite_quality_value: "Composite Quality + Value",
  large_cap_market_cap_weighted: "Large Cap — Market Cap Weighted",
  small_mid_cap_growth: "Small-Mid Cap Growth",
};

export function StrategyCard({
  strategy,
  onRun,
  isRunning,
}: {
  strategy: PrebuiltStrategy;
  onRun: (key: string) => void;
  isRunning: boolean;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{STRATEGY_TITLES[strategy.key] ?? strategy.config.name}</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <ConfigSummary config={strategy.config as unknown as Record<string, unknown>} />
        <Button size="sm" loading={isRunning} onClick={() => onRun(strategy.key)} className="self-start">
          <Play className="h-3.5 w-3.5" />
          {isRunning ? "Running…" : "Run this strategy"}
        </Button>
      </CardContent>
    </Card>
  );
}
