import { Download } from "lucide-react";

import { buildExportUrl } from "@/lib/api";

function ExportLink({ href, label }: { href: string; label: string }) {
  return (
    <a
      href={href}
      className="flex items-center gap-2 rounded border border-border bg-surface-raised px-3 py-2 text-xs text-ink-secondary transition-colors hover:border-accent/40 hover:text-ink-primary"
    >
      <Download className="h-3.5 w-3.5" />
      {label}
    </a>
  );
}

export function ExportMenu({ runId }: { runId: string }) {
  return (
    <div className="flex flex-wrap gap-2">
      <ExportLink href={buildExportUrl(runId, "csv", "holdings")} label="Portfolio log (CSV)" />
      <ExportLink href={buildExportUrl(runId, "xlsx", "holdings")} label="Portfolio log (Excel)" />
      <ExportLink href={buildExportUrl(runId, "csv", "equity_curve")} label="Equity curve (CSV)" />
      <ExportLink href={buildExportUrl(runId, "xlsx", "equity_curve")} label="Equity curve (Excel)" />
    </div>
  );
}
