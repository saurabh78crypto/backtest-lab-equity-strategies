import { AlertTriangle, Inbox } from "lucide-react";

import { cn } from "@/lib/cn";

export function Spinner({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "h-5 w-5 animate-spin rounded-full border-2 border-border border-t-accent",
        className
      )}
    />
  );
}

export function LoadingState({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-ink-muted">
      <Spinner />
      <p className="text-xs">{label}</p>
    </div>
  );
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <div className="flex h-10 w-10 items-center justify-center rounded-full border border-border bg-surface-raised">
        <Inbox className="h-5 w-5 text-ink-muted" />
      </div>
      <div>
        <p className="font-display text-sm font-medium text-ink-primary">{title}</p>
        {description && <p className="mt-1 max-w-sm text-xs text-ink-muted">{description}</p>}
      </div>
      {action}
    </div>
  );
}

export function ErrorState({ title = "Something went wrong", description }: { title?: string; description?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <div className="flex h-10 w-10 items-center justify-center rounded-full border border-negative/30 bg-negative-soft">
        <AlertTriangle className="h-5 w-5 text-negative" />
      </div>
      <div>
        <p className="font-display text-sm font-medium text-ink-primary">{title}</p>
        {description && <p className="mt-1 max-w-sm text-xs text-ink-muted">{description}</p>}
      </div>
    </div>
  );
}
