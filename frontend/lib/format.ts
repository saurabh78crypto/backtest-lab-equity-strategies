import { format, parseISO } from "date-fns";

const inrNumberFormatter = new Intl.NumberFormat("en-IN", {
  maximumFractionDigits: 0,
});

const inrDecimalFormatter = new Intl.NumberFormat("en-IN", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/** Formats a raw rupee amount with Indian digit grouping, e.g. 1234567 -> "₹12,34,567" */
export function formatINR(value: number): string {
  return `₹${inrNumberFormatter.format(Math.round(value))}`;
}

/** Formats a value already expressed in INR Crores, e.g. 1234.5 -> "₹1,234.5 Cr" */
export function formatCrores(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `₹${inrDecimalFormatter.format(value)} Cr`;
}

/** Compact axis-friendly form: 150000 -> "₹1.5L", 12000000 -> "₹1.2Cr" */
export function formatCompactINR(value: number): string {
  const abs = Math.abs(value);
  if (abs >= 1e7) return `₹${(value / 1e7).toFixed(1)}Cr`;
  if (abs >= 1e5) return `₹${(value / 1e5).toFixed(1)}L`;
  if (abs >= 1e3) return `₹${(value / 1e3).toFixed(0)}K`;
  return `₹${value.toFixed(0)}`;
}

/** Signed percentage, e.g. 12.345 -> "+12.35%", -4.2 -> "-4.20%" */
export function formatPercent(value: number | null | undefined, opts?: { signed?: boolean; decimals?: number }): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  const decimals = opts?.decimals ?? 2;
  const signed = opts?.signed ?? true;
  const sign = signed && value > 0 ? "+" : "";
  return `${sign}${value.toFixed(decimals)}%`;
}

export function formatNumber(value: number | null | undefined, decimals = 2): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return value.toLocaleString("en-IN", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

export function formatShares(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return value.toLocaleString("en-IN", { maximumFractionDigits: value < 10 ? 4 : 2 });
}

export function formatDate(value: string | null | undefined, pattern = "dd MMM yyyy"): string {
  if (!value) return "—";
  try {
    return format(parseISO(value), pattern);
  } catch {
    return value;
  }
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return "—";
  try {
    return format(parseISO(value), "dd MMM yyyy, HH:mm");
  } catch {
    return value;
  }
}

/** Tailwind text-color class for a signed number */
export function signColorClass(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value) || value === 0) return "text-ink-secondary";
  return value > 0 ? "text-positive" : "text-negative";
}
