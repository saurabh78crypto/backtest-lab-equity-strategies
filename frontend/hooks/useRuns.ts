"use client";

import { useQuery } from "@tanstack/react-query";

import { listRuns } from "@/lib/api";

export function useRuns(limit = 50) {
  return useQuery({
    queryKey: ["runs", limit],
    queryFn: () => listRuns(limit),
  });
}
