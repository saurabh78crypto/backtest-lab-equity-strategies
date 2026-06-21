"use client";

import { useQuery } from "@tanstack/react-query";

import { listPrebuiltStrategies } from "@/lib/api";

export function usePrebuiltStrategies() {
  return useQuery({
    queryKey: ["prebuilt-strategies"],
    queryFn: listPrebuiltStrategies,
    staleTime: Infinity,
  });
}
