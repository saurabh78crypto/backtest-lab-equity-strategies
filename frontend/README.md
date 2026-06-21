# Frontend — Backtest Lab

Next.js (TypeScript) + Tailwind CSS UI for configuring, running, and
analysing fundamental equity backtests against the FastAPI backend.

## 1. Quick Start

### 1.1 Prerequisites
- Node.js 18.18+ (Node 20 LTS recommended)
- The backend running locally (see `../backend/README.md`) — by default at `http://localhost:8000`

### 1.2 Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```
Open http://localhost:3000

### 1.3 Build for production

```bash
npm run build
npm run start
```

---

## 2. Architecture Overview

```
frontend/
├── app/                         Next.js App Router pages (route = folder)
│   ├── layout.tsx                 Root layout: fonts, React Query provider
│   ├── globals.css                 Tailwind layers + base terminal styling
│   ├── page.tsx                    "/" — New Backtest config form
│   ├── runs/
│   │   ├── page.tsx                  "/runs" — run history
│   │   └── [runId]/page.tsx          "/runs/:id" — full results view
│   ├── strategies/page.tsx         "/strategies" — prebuilt strategies (bonus)
│   └── compare/page.tsx            "/compare" — multi-run comparison (bonus)
├── components/
│   ├── layout/                    AppShell, Sidebar, Topbar (responsive shell)
│   ├── ui/                        Reusable primitives: Button, Card, Field,
│   │                                Select, Checkbox, Badge, Table, Tabs,
│   │                                States (loading/empty/error), StatusBadge
│   ├── backtest-form/              The config form, split by concern:
│   │   ├── configReducer.ts          useReducer state machine for the form
│   │   ├── validateConfig.ts         Client-side validation (mirrors backend)
│   │   ├── BasicsSection.tsx         Name, dates, capital, benchmark toggle
│   │   ├── RebalanceSizingSection.tsx Rebalance freq, portfolio size, sizing
│   │   ├── FiltersSection.tsx        Market cap / ROCE / ROE / D-E / PAT filters
│   │   ├── RankingSection.tsx        Single/composite ranking metric builder
│   │   └── BacktestConfigForm.tsx    Orchestrator - wires sections together
│   ├── results/                    Everything shown after a run completes:
│   │   ├── ResultsView.tsx           Orchestrator
│   │   ├── EquityDrawdownChart.tsx   Equity curve + synced drawdown panel
│   │   ├── MetricsGrid.tsx           CAGR/Sharpe/Sortino/MaxDD/etc. scorecard
│   │   ├── WinnersLosersPanel.tsx    Top winners/losers tables
│   │   ├── HoldingsLogTable.tsx      Portfolio log, browsable by rebalance
│   │   ├── ExportMenu.tsx            CSV/Excel download links
│   │   └── ConfigSummary.tsx         Human-readable summary of a run's config
│   ├── runs/RunsTable.tsx          Run history table (view/delete)
│   ├── strategies/StrategyCard.tsx Prebuilt strategy card + run button
│   └── compare/                    RunPicker, CompareChart, CompareMetricsTable
├── hooks/                        One React Query hook per backend endpoint
├── lib/
│   ├── types.ts                    TypeScript types - 1:1 mirror of backend
│   │                                  Pydantic schemas (see note below)
│   ├── api.ts                      Typed fetch client, one function per endpoint
│   ├── format.ts                   INR/percentage/date formatting helpers
│   ├── constants.ts                Nav items, chart color tokens
│   └── cn.ts                       clsx + tailwind-merge classname utility
└── providers/QueryProvider.tsx   React Query client provider
```

**Design principle:** pages in `app/` are thin — they fetch via a hook and
hand data to a `components/results|backtest-form|...` orchestrator. Every
section of the config form and every panel of the results view is its own
component, not one giant file, so each piece is independently readable and
reusable (e.g. `ConfigSummary` is reused on both the results page and the
prebuilt-strategies cards).

**Why `lib/types.ts` duplicates the backend's Pydantic schemas:** the
frontend and backend are separate deployable apps with no shared package, so
the contract is kept in sync by hand. If you change a field on a backend
schema, update the matching interface in `lib/types.ts`.

---

## 3. Design System

This is a data-dense analytics tool, not a marketing site, so the visual
language is built around a "ledger/terminal" concept rather than a generic
admin-dashboard template:

| Token | Choice | Why |
|---|---|---|
| Background | Deep ink-indigo (`#0B0E14`) | Comfortable for long data-reading sessions, less flat than pure near-black |
| Accent | Amber/gold (`#D4A24E`) | Evokes ledgers/exchange branding; reserved for actions, active states, and the strategy line on charts |
| Gain / Loss | Emerald / Rose | The **only** place green/red appear — never used decoratively, so a red number always means "down" |
| Display face | Space Grotesk | Distinct geometric character for headings, avoids the generic-Inter-everywhere look |
| Body face | Inter | Neutral, highly legible for dense UI chrome |
| Data face | JetBrains Mono, `tabular-nums` | Every price, percentage, share count, and date is monospaced and column-aligned — figures should read like a real terminal, not jitter row to row |

**Signature element:** the equity curve + drawdown panel
(`EquityDrawdownChart`) is two synced charts (`syncId`) stacked like a real
trading terminal's price/volume pane, rather than a single line chart — this
is the central, most-used visual in the app and it's built to actually carry
information (hovering one panel highlights the same date on the other), not
just to look distinctive.

**Responsiveness:** the sidebar collapses into a slide-in drawer below the
`lg` breakpoint (`AppShell`); all data tables scroll horizontally on narrow
viewports rather than truncating; the config form's multi-column field grids
collapse to a single column on mobile.

---

## 4. How Each Requirement Is Met

| Requirement | Where |
|---|---|
| Configure date range, rebalance frequency, portfolio size | `BasicsSection`, `RebalanceSizingSection` |
| Input stock filters | `FiltersSection` (Market Cap range, ROCE/ROE thresholds, Debt/Equity cap, PAT > 0) |
| Input ranking logic (single or composite) | `RankingSection` — add any number of metrics, each with order + weight |
| Select position sizing method | `RebalanceSizingSection` (equal / market-cap / metric-weighted, with the weighting metric picker appearing only when relevant) |
| Run the backtest and view outputs | `BacktestConfigForm` submits to `POST /backtest/run`, then routes to `/runs/:id` |
| Equity curve | `EquityDrawdownChart` (top panel) |
| Drawdown chart | `EquityDrawdownChart` (bottom, synced panel) |
| Performance metrics (CAGR, Sharpe, Max DD, etc.) | `MetricsGrid` |
| Top winners and losers | `WinnersLosersPanel` |
| Portfolio logs with weights and returns | `HoldingsLogTable` |
| Export as CSV/Excel | `ExportMenu` (holdings and equity curve, each in CSV or XLSX) |
| **Bonus:** prebuilt strategy outputs | `/strategies` page + `StrategyCard` |
| **Bonus:** strategy comparison | `/compare` page — overlay 2-5 runs, indexed to 100 at each run's start |
| **Bonus:** benchmark comparison | Nifty 50 plotted on the equity curve whenever the run includes it; alpha/beta/benchmark CAGR/DD shown in `MetricsGrid` |

---

## 5. Assumptions & Notes

- All config form options (rebalance frequencies, sizing methods, rankable
  metrics) are fetched from `GET /metadata/backtest-options` rather than
  hardcoded, so the form never drifts out of sync with what the backend
  actually supports.
- **The Start/End date pickers in `BasicsSection` are constrained to the
  database's actual data coverage**, not left open to any date. The same
  `GET /metadata/backtest-options` response carries `data_start_date`/
  `data_end_date`; `BasicsSection` sets these as `min`/`max` on both date
  inputs and shows them in a note under the section header,
  `validateConfig.getFieldErrors` rejects a typed-in date outside that
  window with an inline error (native `min`/`max` only affects the calendar
  widget, not keyboard input), and `BacktestConfigForm` pre-fills both
  fields with that range on first load. See backend README §7 for why this
  exists.
- A backtest run executes synchronously on the backend and the form shows a
  loading state for the duration — there's no polling/job-queue UI, matching
  the backend's synchronous `POST /backtest/run` design (see backend README
  §8 for the async/background execution noted as a future improvement).
- The compare page indexes each run's equity curve to 100 at its own start
  and aligns by trading-day offset rather than calendar date, since runs
  being compared can have different date ranges and initial capital — see
  the comment in `components/compare/CompareChart.tsx`.
- This project was built without network access to npm in the build
  environment, so `npm install` has not been run against it here — only
  static TypeScript syntax parsing, import-path resolution, and
  named-export/import cross-checks were performed. Run `npm install && npm
  run dev` to do a full compile; if anything surfaces, it's most likely a
  third-party type-definition nuance (e.g. a recharts prop type) rather than
  application logic.
