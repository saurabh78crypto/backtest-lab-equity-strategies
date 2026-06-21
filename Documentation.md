# Documentation - Backtesting Framework for Equity-Based Strategies

This document describes each module of the project, the file structure,
the assumptions made while building it, and the optional/bonus features
implemented.

**Tech stack:** FastAPI + SQLAlchemy + PostgreSQL (backend) · Next.js +
TypeScript + Tailwind CSS (frontend) · Yahoo Finance (`yfinance`) for data.

---

## 1. Module Descriptions

### 1.1 Backend (`backend/app/`)

| Module | What it does |
|---|---|
| `main.py` | Creates the FastAPI app, sets up CORS, registers all API routes, and creates database tables on startup. |
| `core/config.py` | Central place for all settings (database URL, reporting-lag days, risk-free rate, etc.), read from environment variables. |
| `core/logging.py` | Basic logging setup used across the app. |
| `db/base.py` | SQLAlchemy declarative base, plus the `create_all_tables()` helper that creates tables if they don't already exist. |
| `db/session.py` | Database engine, session factory, and the `get_db` dependency used by API routes. |
| `models/` | SQLAlchemy ORM models - these define the database schema. Split into `company.py`, `price.py`, `fundamental.py`, and `backtest.py` (see §3 for the schema itself). |
| `schemas/` | Pydantic models that define the shape of API requests and responses (`backtest.py`, `company.py`), plus `enums.py` which holds shared enums and the list of metrics that can be filtered/ranked on. |
| `data_collection/` | The data ingestion pipeline. `universe.py` lists the companies to track; `fetch_prices.py` and `fetch_fundamentals.py` pull data from Yahoo Finance; `yf_utils.py` has shared helper functions; `pipeline.py` runs the whole ingestion end-to-end. |
| `backtest_engine/` | The core backtest logic, split by responsibility: `data_loader.py` (loads prices/fundamentals once per run), `filters.py` (applies the universe filters once), `ranking.py` (single/composite ranking), `position_sizing.py` (equal / market-cap / metric weighting), `rebalance_dates.py` (builds the rebalance calendar), `metrics.py` (CAGR, Sharpe, drawdown, etc.), and `engine.py` (the orchestrator that ties all of the above together into one backtest run). |
| `strategies/prebuilt.py` | A small library of ready-made strategy configurations (bonus feature, see §4). |
| `api/routes/` | The HTTP layer - thin route handlers that validate the request, call into `backtest_engine`, and return the result. Split into `metadata.py`, `companies.py`, `backtest.py`, and `strategies.py`. |
| `api/serializers.py` | Converts internal/ORM objects into the response shapes the API returns. |

**Design principle:** the API route files contain no business logic - they
just validate input and call the backtest engine. All the actual backtest
logic lives in `backtest_engine/`.

### 1.2 Frontend (`frontend/`)

| Module | What it does |
|---|---|
| `app/` | Next.js pages - one folder per route. `page.tsx` (`/`) is the New Backtest form, `runs/page.tsx` (`/runs`) is run history, `runs/[runId]/page.tsx` (`/runs/:id`) is the results view, `strategies/page.tsx` (`/strategies`) is the prebuilt strategies page, and `compare/page.tsx` (`/compare`) is the multi-run comparison page. |
| `components/layout/` | The app shell - `AppShell`, `Sidebar`, `Topbar` - that wraps every page. |
| `components/ui/` | Reusable building blocks: `Button`, `Card`, `Field`, `Select`, `Checkbox`, `Badge`, `Table`, `Tabs`, `States` (loading/empty/error), `StatusBadge`. |
| `components/backtest-form/` | The New Backtest configuration form, split into sections: `BasicsSection` (name, dates, capital, benchmark toggle), `RebalanceSizingSection` (rebalance frequency, portfolio size, position sizing), `FiltersSection` (market cap, ROCE, ROE, debt/equity, PAT filters), `RankingSection` (single/composite ranking builder). `configReducer.ts` manages the form's state and `validateConfig.ts` validates it before submission. `BacktestConfigForm.tsx` wires all the sections together. |
| `components/results/` | Everything shown after a backtest finishes: `EquityDrawdownChart` (equity curve + drawdown), `MetricsGrid` (CAGR/Sharpe/Sortino/Max Drawdown/etc.), `WinnersLosersPanel` (top winners/losers), `HoldingsLogTable` (the portfolio log), `ExportMenu` (CSV/Excel downloads), `ConfigSummary` (a readable summary of the run's config). `ResultsView.tsx` is the orchestrator that puts all of these together. |
| `components/runs/RunsTable.tsx` | The run history table. |
| `components/strategies/StrategyCard.tsx` | A card for each prebuilt strategy, with a run button. |
| `components/compare/` | `RunPicker` (select runs to compare), `CompareChart` (overlaid equity curves), `CompareMetricsTable` (metrics side by side). |
| `hooks/` | One React Query hook per backend endpoint - e.g. `useRunBacktest`, `useRuns`, `useRun`, `usePrebuiltStrategies`, `useCompareRuns`, `useUniverseStats`, `useBacktestOptions`, `useDeleteRun`. |
| `lib/types.ts` | TypeScript types that mirror the backend's Pydantic schemas. |
| `lib/api.ts` | The typed fetch client - one function per backend endpoint. |
| `lib/format.ts` | Formatting helpers for currency, percentages, and dates. |
| `lib/constants.ts` | Navigation items and chart colour tokens. |
| `lib/cn.ts` | Small utility for combining Tailwind class names. |
| `providers/QueryProvider.tsx` | Sets up the React Query client used across the app. |

**Design principle:** pages in `app/` are thin - they fetch data through a
hook and hand it to a components orchestrator. Every section of the form
and every panel of the results view is its own component rather than one
large file.

---

## 2. File Structure

```
.
├── README.md                          Project overview, quick start
├── docker-compose.yml                 Local PostgreSQL for development
│
├── backend/
│   ├── README.md                       Backend setup & architecture docs
│   ├── requirements.txt                Python dependencies
│   └── app/
│       ├── main.py                      FastAPI app entrypoint
│       ├── core/
│       │   ├── config.py
│       │   └── logging.py
│       ├── db/
│       │   ├── base.py
│       │   └── session.py
│       ├── models/
│       │   ├── company.py
│       │   ├── price.py
│       │   ├── fundamental.py
│       │   └── backtest.py
│       ├── schemas/
│       │   ├── enums.py
│       │   ├── backtest.py
│       │   └── company.py
│       ├── data_collection/
│       │   ├── universe.py
│       │   ├── fetch_prices.py
│       │   ├── fetch_fundamentals.py
│       │   ├── yf_utils.py
│       │   └── pipeline.py
│       ├── backtest_engine/
│       │   ├── data_loader.py
│       │   ├── filters.py
│       │   ├── ranking.py
│       │   ├── position_sizing.py
│       │   ├── rebalance_dates.py
│       │   ├── metrics.py
│       │   └── engine.py
│       ├── strategies/
│       │   └── prebuilt.py
│       └── api/
│           ├── serializers.py
│           └── routes/
│               ├── metadata.py
│               ├── companies.py
│               ├── backtest.py
│               └── strategies.py
│
└── frontend/
    ├── README.md                       Frontend setup & architecture docs
    ├── package.json                    Node dependencies
    ├── tailwind.config.ts
    ├── next.config.mjs
    ├── app/
    │   ├── layout.tsx
    │   ├── globals.css
    │   ├── page.tsx                      "/"  - New Backtest
    │   ├── runs/
    │   │   ├── page.tsx                    "/runs"
    │   │   └── [runId]/page.tsx            "/runs/:id"
    │   ├── strategies/page.tsx           "/strategies"
    │   └── compare/page.tsx              "/compare"
    ├── components/
    │   ├── layout/        AppShell.tsx, Sidebar.tsx, Topbar.tsx
    │   ├── ui/             Button, Card, Field, Select, Checkbox, Badge,
    │   │                     Table, Tabs, States, StatusBadge
    │   ├── backtest-form/  BasicsSection, RebalanceSizingSection,
    │   │                     FiltersSection, RankingSection,
    │   │                     BacktestConfigForm, configReducer, validateConfig
    │   ├── results/        ResultsView, EquityDrawdownChart, MetricsGrid,
    │   │                     WinnersLosersPanel, HoldingsLogTable,
    │   │                     ExportMenu, ConfigSummary, ChartTooltip, StatCard
    │   ├── runs/RunsTable.tsx
    │   ├── strategies/StrategyCard.tsx
    │   └── compare/        RunPicker, CompareChart, CompareMetricsTable
    ├── hooks/              useRunBacktest, useRuns, useRun, useDeleteRun,
    │                         usePrebuiltStrategies, useRunPrebuiltStrategy,
    │                         useCompareRuns, useUniverseStats, useBacktestOptions
    ├── lib/                types.ts, api.ts, format.ts, constants.ts, cn.ts
    └── providers/QueryProvider.tsx
```

---

## 3. Database Schema

| Table | One row per | What it stores |
|---|---|---|
| `companies` | instrument | Master list of companies (the Nifty 50 benchmark is stored here too, flagged `is_benchmark=True`). |
| `stock_prices` | company + date | Daily OHLCV price data. Kept in its own table since it has a different grain (daily) than fundamentals (quarterly/annual). |
| `fundamentals` | company + period_end_date + period_type | Raw P&L / Balance Sheet / Cash Flow line items, plus derived ratios (ROE, ROCE, ROA, margins, etc.). |
| `backtest_runs` | run | The full request configuration (stored as JSON) and the run's status. |
| `backtest_results` | run + date | The daily equity curve: portfolio value, benchmark value, drawdown, daily return. |
| `portfolio_holdings` | run + rebalance_date + stock | The portfolio log: rank, weight, entry/exit price, realised return. |
| `backtest_metrics` | run | The summary scorecard: CAGR, Sharpe, Sortino, Max Drawdown, alpha/beta vs. benchmark, etc. |

**Indexes:** `stock_prices(company_id, date)` and `fundamentals(company_id, report_date)`
support the backtest engine's lookups; `backtest_results(run_id, date)` and
`portfolio_holdings(run_id, rebalance_date)` support fast retrieval of a
run's results for the frontend.

---

## 4. Optional Features Implemented (Bonus)

The assignment listed these as optional/bonus items. All of them are implemented:

- **API endpoints via FastAPI** - the entire backend is a FastAPI service
  (`POST /backtest/run`, `GET /backtest/runs`, `GET /backtest/{run_id}`,
  `DELETE /backtest/{run_id}`, `GET /backtest/{run_id}/export`, etc.).
- **Outputs of prebuilt strategies** - `strategies/prebuilt.py` defines five
  ready-to-run strategies (Quality - High ROCE, Value - Low PE, Composite
  Quality + Value, Large Cap - Market Cap Weighted, Small-Mid Cap Growth),
  exposed on the `/strategies` page with one-click run.
- **Strategy comparison feature** - the `/compare` page lets a user pick
  2–5 past runs and view their equity curves overlaid on one chart plus a
  side-by-side metrics table.
- **Benchmark comparison (Nifty 50)** - every run can include the Nifty 50
  benchmark; it's plotted alongside the strategy's equity curve, and
  alpha/beta/benchmark CAGR/drawdown are shown in the metrics grid.

---

## 5. Assumptions

These are the assumptions made while building the system, and why:

- **Reporting lag for point-in-time correctness.** Yahoo Finance only
  exposes a fundamental statement's *period-end date*, not the date it was
  actually filed/published. To avoid using data that wouldn't have been
  available yet (future-data leakage), the system estimates a filing date
  as `period_end_date + reporting_lag`, using SEBI's mandated filing
  windows as a conservative default - 45 days for quarterly results, 60
  days for audited annual results. This is the single biggest assumption
  in the system, since it's an estimate rather than the company's actual
  filing date.
- **Prices are adjusted close prices.** Returns already account for
  stock splits, dividends, and bonus issues, so no separate corporate
  action handling was needed.
- **Shares outstanding** is taken from the balance sheet for that period
  where available. If missing, it's backed out from `Net Income / Diluted
  EPS`, and if that's also unavailable, the company's current shares
  outstanding is used as a last resort (Yahoo Finance doesn't expose a
  clean historical shares-outstanding series).
- **The universe is a static, curated list** of ~125 companies (not an
  auto-updated index), so there's no survivorship-bias correction beyond
  what's naturally present in Yahoo Finance's data.
- **No transaction costs, slippage, or taxes are modelled** - returns
  shown are gross returns.
- **If fewer companies than the requested portfolio size pass the
  filters**, the portfolio simply holds however many are available rather
  than erroring out.
- **A holding with no exit price available at the next rebalance** (e.g. a
  data gap) is treated as a 0% return for that leg, so a data gap can't
  silently create or destroy capital.
- **The custom backtest date range is bounded by actual data coverage**,
  not the full price history. Different companies start reporting
  fundamentals at different times, so the system computes a "safe"
  start/end date window live from the database and constrains the
  frontend's date pickers to it - this prevents an early start date from
  silently shrinking the eligible universe in a way that has nothing to do
  with the strategy itself. The prebuilt strategies are already defined
  within this safe window.
- **A backtest run executes synchronously** - the API call runs the
  backtest and returns full results in one request/response, with the
  frontend showing a loading state for the duration. There is no
  background job queue.
- **The frontend's TypeScript types are kept in sync with the backend's
  Pydantic schemas by hand**, since the two are separate applications with
  no shared package.

---

## 6. Tech Stack Summary

| Layer | Technology |
|---|---|
| Backend | Python - FastAPI, SQLAlchemy, Pydantic, pandas, numpy |
| Database | PostgreSQL |
| Frontend | Next.js (TypeScript), Tailwind CSS, React Query, Recharts |
| Data source | Yahoo Finance (`yfinance`) |