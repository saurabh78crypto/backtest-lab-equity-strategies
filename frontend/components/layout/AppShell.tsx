"use client";

import { X } from "lucide-react";
import { useState } from "react";

import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export function AppShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Desktop sidebar */}
      <div className="hidden h-full shrink-0 lg:block">
        <Sidebar />
      </div>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 flex lg:hidden">
          <div className="absolute inset-0 bg-black/60" onClick={() => setMobileOpen(false)} />
          <div className="relative z-10 h-full">
            <Sidebar onNavigate={() => setMobileOpen(false)} />
          </div>
          <button
            onClick={() => setMobileOpen(false)}
            className="absolute right-4 top-4 z-20 flex h-8 w-8 items-center justify-center rounded bg-surface-raised text-ink-secondary"
            aria-label="Close navigation menu"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      <div className="flex min-h-0 min-w-0 flex-1 flex-col">
        <Topbar title={title} subtitle={subtitle} onMenuClick={() => setMobileOpen(true)} />
        <main className="min-h-0 flex-1 overflow-y-auto px-4 py-6 lg:px-8 lg:py-8">{children}</main>
      </div>
    </div>
  );
}
