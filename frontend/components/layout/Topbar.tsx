"use client";

import { Menu } from "lucide-react";

export function Topbar({ title, subtitle, onMenuClick }: { title: string; subtitle?: string; onMenuClick: () => void }) {
  return (
    <header className="flex items-center gap-3 border-b border-border bg-surface px-4 py-4 lg:px-8">
      <button
        onClick={onMenuClick}
        className="flex h-8 w-8 items-center justify-center rounded text-ink-secondary hover:bg-surface-hover lg:hidden"
        aria-label="Open navigation menu"
      >
        <Menu className="h-4 w-4" />
      </button>
      <div>
        <h1 className="font-display text-base font-semibold text-ink-primary">{title}</h1>
        {subtitle && <p className="text-xs text-ink-muted">{subtitle}</p>}
      </div>
    </header>
  );
}
