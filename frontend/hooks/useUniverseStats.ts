"use client";

import { useQuery } from "@tanstack/react-query";

import { getUniverseStats } from "@/lib/api";

export function useUniverseStats() {
  return useQuery({
    queryKey: ["universe-stats"],
    queryFn: getUniverseStats,
    staleTime: 5 * 60_000,
  });
}
