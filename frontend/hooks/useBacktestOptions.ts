"use client";

import { useQuery } from "@tanstack/react-query";

import { getBacktestOptions } from "@/lib/api";

export function useBacktestOptions() {
  return useQuery({
    queryKey: ["backtest-options"],
    queryFn: getBacktestOptions,
    staleTime: 5 * 60_000,
  });
}
