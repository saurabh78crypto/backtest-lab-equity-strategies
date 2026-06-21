"use client";

import { useMutation } from "@tanstack/react-query";

import { compareRuns } from "@/lib/api";

export function useCompareRuns() {
  return useMutation({
    mutationFn: (runIds: string[]) => compareRuns(runIds),
  });
}
