"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { runBacktest } from "@/lib/api";
import type { BacktestConfigRequest } from "@/lib/types";

export function useRunBacktest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (config: BacktestConfigRequest) => runBacktest(config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["runs"] });
    },
  });
}
