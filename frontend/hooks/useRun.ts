"use client";

import { useQuery } from "@tanstack/react-query";

import { getRun } from "@/lib/api";

export function useRun(runId: string | undefined) {
  return useQuery({
    queryKey: ["run", runId],
    queryFn: () => getRun(runId as string),
    enabled: Boolean(runId),
  });
}
