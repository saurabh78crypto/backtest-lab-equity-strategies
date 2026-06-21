"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { deleteRun } from "@/lib/api";

export function useDeleteRun() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (runId: string) => deleteRun(runId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["runs"] });
    },
  });
}
