import { BacktestConfigForm } from "@/components/backtest-form/BacktestConfigForm";
import { AppShell } from "@/components/layout/AppShell";

export default function NewBacktestPage() {
  return (
    <AppShell title="New Backtest" subtitle="Configure filters, ranking, and sizing, then run the simulation">
      <div className="mx-auto max-w-5xl">
        <BacktestConfigForm />
      </div>
    </AppShell>
  );
}
