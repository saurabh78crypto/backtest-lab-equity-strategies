"use client";

import { LineChart } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useUniverseStats } from "@/hooks/useUniverseStats";
import { cn } from "@/lib/cn";
import { NAV_ITEMS } from "@/lib/constants";

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  const { data: stats } = useUniverseStats();

  return (
    <div className="flex h-full w-64 flex-col overflow-hidden border-r border-border bg-surface">
      <div className="flex shrink-0 items-center gap-2.5 border-b border-border px-5 py-5">
        <div className="flex h-8 w-8 items-center justify-center rounded bg-accent-soft text-accent">
          <LineChart className="h-4 w-4" />
        </div>
        <div>
          <p className="font-display text-sm font-semibold leading-none text-ink-primary">Backtest Lab</p>
          <p className="mt-1 text-2xs text-ink-muted">Equity strategy terminal</p>
        </div>
      </div>

      <nav className="flex min-h-0 flex-1 flex-col gap-0.5 overflow-y-auto px-3 py-4">
        {NAV_ITEMS.map((item) => {
          const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={cn(
                "rounded px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-accent-soft text-accent"
                  : "text-ink-secondary hover:bg-surface-hover hover:text-ink-primary"
              )}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="shrink-0 border-t border-border px-5 py-4">
        <p className="text-2xs uppercase tracking-wide text-ink-muted">Universe</p>
        {stats ? (
          <div className="mt-2 space-y-1 font-mono text-2xs text-ink-secondary">
            <p>{stats.total_companies} companies tracked</p>
            <p>
              {stats.earliest_price_date ?? "—"} → {stats.latest_price_date ?? "—"}
            </p>
          </div>
        ) : (
          <p className="mt-2 text-2xs text-ink-muted">Not connected to data yet</p>
        )}
      </div>
    </div>
  );
}
