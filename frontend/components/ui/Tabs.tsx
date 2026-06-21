"use client";

import { cn } from "@/lib/cn";

export interface TabItem {
  value: string;
  label: string;
  count?: number;
}

interface TabsProps {
  items: TabItem[];
  value: string;
  onChange: (value: string) => void;
  className?: string;
}

export function Tabs({ items, value, onChange, className }: TabsProps) {
  return (
    <div className={cn("flex items-center gap-1 border-b border-border", className)} role="tablist">
      {items.map((item) => {
        const active = item.value === value;
        return (
          <button
            key={item.value}
            role="tab"
            aria-selected={active}
            onClick={() => onChange(item.value)}
            className={cn(
              "relative flex items-center gap-1.5 px-3 py-2.5 text-xs font-medium transition-colors",
              active ? "text-accent" : "text-ink-muted hover:text-ink-secondary"
            )}
          >
            {item.label}
            {item.count !== undefined && (
              <span className="rounded-full bg-surface-raised px-1.5 py-0.5 text-2xs text-ink-muted">
                {item.count}
              </span>
            )}
            {active && <span className="absolute inset-x-0 -bottom-px h-0.5 bg-accent" />}
          </button>
        );
      })}
    </div>
  );
}
