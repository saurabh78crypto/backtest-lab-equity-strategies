import { type HTMLAttributes } from "react";

import { cn } from "@/lib/cn";

type Tone = "neutral" | "accent" | "positive" | "negative";

const toneClasses: Record<Tone, string> = {
  neutral: "bg-surface-raised text-ink-secondary border-border",
  accent: "bg-accent-soft text-accent border-accent/30",
  positive: "bg-positive-soft text-positive border-positive/30",
  negative: "bg-negative-soft text-negative border-negative/30",
};

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: Tone;
}

export function Badge({ className, tone = "neutral", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-sm border px-2 py-0.5 text-2xs font-medium uppercase tracking-wide",
        toneClasses[tone],
        className
      )}
      {...props}
    />
  );
}
