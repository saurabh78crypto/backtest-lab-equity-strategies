"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { runPrebuiltStrategy } from "@/lib/api";

export function useRunPrebuiltStrategy() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (key: string) => runPrebuiltStrategy(key),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["runs"] });
    },
  });
}
