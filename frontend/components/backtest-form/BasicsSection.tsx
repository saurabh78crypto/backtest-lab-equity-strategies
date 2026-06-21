"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Checkbox } from "@/components/ui/Checkbox";
import { Field, Input, NumberInput } from "@/components/ui/Field";
import type { ConfigAction } from "@/components/backtest-form/configReducer";
import type { ConfigFieldErrors } from "@/components/backtest-form/validateConfig";
import type { BacktestConfigRequest } from "@/lib/types";

interface Props {
  config: BacktestConfigRequest;
  dispatch: React.Dispatch<ConfigAction>;
  benchmarkName?: string;
  errors: ConfigFieldErrors;
  touch: (field: string) => void;
  dataStartDate?: string | null;
  dataEndDate?: string | null;
}

export function BasicsSection({ config, dispatch, benchmarkName, errors, touch, dataStartDate, dataEndDate }: Props) {
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Strategy Basics</CardTitle>
          <CardDescription>Name the strategy and define the simulation window.</CardDescription>
          <CardDescription>
            Name the strategy and define the simulation window.{" "}
            {dataStartDate && dataEndDate
              ? `We only have data between ${dataStartDate} and ${dataEndDate} - pick a start/end date inside this range.`
              : "Loading the available data range…"}
          </CardDescription>
        </div>
      </CardHeader>
      <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Field
          label="Strategy name"
          htmlFor="name"
          required
          error={errors.name}
          className="sm:col-span-2 lg:col-span-4"
        >
          <Input
            id="name"
            placeholder="e.g. Quality ROCE Compounders"
            value={config.name}
            onChange={(e) => dispatch({ type: "SET_FIELD", field: "name", value: e.target.value })}
            onBlur={() => touch("name")}
          />
        </Field>

        <Field label="Start date" htmlFor="start_date" required error={errors.start_date}>
          <Input
            id="start_date"
            type="date"
            value={config.start_date}
            onChange={(e) => dispatch({ type: "SET_FIELD", field: "start_date", value: e.target.value })}
            onBlur={() => touch("start_date")}
            min={dataStartDate ?? undefined}
            max={dataEndDate ?? undefined}
          />
        </Field>

        <Field label="End date" htmlFor="end_date" required error={errors.end_date}>
          <Input
            id="end_date"
            type="date"
            value={config.end_date}
            onChange={(e) => dispatch({ type: "SET_FIELD", field: "end_date", value: e.target.value })}
            onBlur={() => touch("end_date")}
            min={dataStartDate ?? undefined}
            max={dataEndDate ?? undefined}
          />
        </Field>
        
        <Field label="Initial capital" htmlFor="initial_capital" required hint="In INR" error={errors.initial_capital}>
          <NumberInput
            id="initial_capital"
            prefix="₹"
            min={1}
            value={config.initial_capital}
            onChange={(value) => dispatch({ type: "SET_FIELD", field: "initial_capital", value: value ?? 0 })}
            onBlur={() => touch("initial_capital")}
          />
        </Field>

        <Field label="Benchmark">
          <Checkbox
            id="include_benchmark"
            label={`Compare against ${benchmarkName ?? "Nifty 50"}`}
            description="Plots the index alongside your equity curve"
            checked={config.include_benchmark}
            onChange={(e) => dispatch({ type: "SET_FIELD", field: "include_benchmark", value: e.target.checked })}
          />
        </Field>
      </CardContent>
    </Card>
  );
}
