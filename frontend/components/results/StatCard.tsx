import { cn } from "@/lib/cn";

export function StatCard({
  label,
  value,
  valueClassName,
  hint,
}: {
  label: string;
  value: string;
  valueClassName?: string;
  hint?: string;
}) {
  return (
    <div className="rounded border border-border bg-surface-raised px-4 py-3">
      <p className="text-2xs uppercase tracking-wide text-ink-muted">{label}</p>
      <p className={cn("mt-1 font-mono text-lg font-medium text-ink-primary", valueClassName)}>{value}</p>
      {hint && <p className="mt-0.5 text-2xs text-ink-muted">{hint}</p>}
    </div>
  );
}
