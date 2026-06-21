"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Checkbox } from "@/components/ui/Checkbox";
import { Field, NumberInput } from "@/components/ui/Field";
import type { ConfigAction } from "@/components/backtest-form/configReducer";
import type { ConfigFieldErrors } from "@/components/backtest-form/validateConfig";
import type { BacktestConfigRequest } from "@/lib/types";

interface Props {
  config: BacktestConfigRequest;
  dispatch: React.Dispatch<ConfigAction>;
  errors: ConfigFieldErrors;
  touch: (field: string) => void;
}

export function FiltersSection({ config, dispatch, errors, touch }: Props) {
  const { filters } = config;

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Universe Filters</CardTitle>
          <CardDescription>
            Evaluated once, on the start date, against the full universe — the resulting list of eligible
            stocks is then reused at every rebalance.
          </CardDescription>
        </div>
      </CardHeader>
      <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Field label="Market cap — minimum" hint="In INR Crores">
          <NumberInput
            prefix="₹"
            suffix="Cr"
            min={0}
            value={filters.market_cap_min_cr ?? null}
            onChange={(value) => dispatch({ type: "SET_FILTER", field: "market_cap_min_cr", value })}
            onBlur={() => touch("market_cap_max_cr")}
            placeholder="No minimum"
          />
        </Field>

        <Field label="Market cap — maximum" hint="In INR Crores" error={errors.market_cap_max_cr}>
          <NumberInput
            prefix="₹"
            suffix="Cr"
            min={0}
            value={filters.market_cap_max_cr ?? null}
            onChange={(value) => dispatch({ type: "SET_FILTER", field: "market_cap_max_cr", value })}
            onBlur={() => touch("market_cap_max_cr")}
            placeholder="No maximum"
          />
        </Field>

        <Field label="Debt / Equity — maximum">
          <NumberInput
            min={0}
            step={0.1}
            value={filters.debt_to_equity_max ?? null}
            onChange={(value) => dispatch({ type: "SET_FILTER", field: "debt_to_equity_max", value })}
            placeholder="No cap"
          />
        </Field>

        <Field label="ROCE greater than" hint="%">
          <NumberInput
            suffix="%"
            step={0.5}
            value={filters.roce_min_pct ?? null}
            onChange={(value) => dispatch({ type: "SET_FILTER", field: "roce_min_pct", value })}
            placeholder="No minimum"
          />
        </Field>

        <Field label="ROE greater than" hint="%">
          <NumberInput
            suffix="%"
            step={0.5}
            value={filters.roe_min_pct ?? null}
            onChange={(value) => dispatch({ type: "SET_FILTER", field: "roe_min_pct", value })}
            placeholder="No minimum"
          />
        </Field>

        <Field label="Profitability">
          <Checkbox
            label="Require PAT > 0"
            description="Excludes loss-making companies"
            checked={filters.pat_positive}
            onChange={(e) => dispatch({ type: "SET_FILTER", field: "pat_positive", value: e.target.checked })}
          />
        </Field>
      </CardContent>
    </Card>
  );
}
