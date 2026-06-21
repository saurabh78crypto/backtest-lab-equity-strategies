import { Badge } from "@/components/ui/Badge";
import type { BacktestStatus } from "@/lib/types";

const STATUS_TONE: Record<BacktestStatus, "neutral" | "accent" | "positive" | "negative"> = {
  pending: "neutral",
  running: "accent",
  completed: "positive",
  failed: "negative",
};

export function StatusBadge({ status }: { status: BacktestStatus }) {
  return <Badge tone={STATUS_TONE[status]}>{status}</Badge>;
}
