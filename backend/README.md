# Backend — Backtesting Framework API

FastAPI + SQLAlchemy + PostgreSQL (Supabase) service that ingests NSE equity
data and runs configurable, point-in-time-correct fundamental backtests.

## 1. Quick Start

### 1.1 Prerequisites
- Python 3.11+
- A PostgreSQL database — either:
  - **Supabase** (recommended, matches the assignment's tech stack): create a free project at supabase.com and grab the connection string from *Project Settings → Database → Connection string → URI*, **or**
  - **Local Postgres via Docker**: `docker compose up -d` from the repo root (uses `docker-compose.yml`)

### 1.2 Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.data_collection.pipeline   # ingest ~125 NSE companies + Nifty 50
cp .env.example .env
# edit .env -> set DATABASE_URL to your Supabase or local Postgres connection string
```

### 1.3 Run the data collection pipeline

> Tables are created automatically and idempotently the moment anything
> touches the database — both the API server's startup and this pipeline
> call the same `create_all_tables()` helper — so run these steps in
> whichever order you like; there's no separate init-db step.


### 1.4 Run the API

```bash
uvicorn app.main:app --reload --port 8000
```
Tables are created automatically on startup (`create_all_tables()` runs in
the FastAPI `lifespan` handler in `app/main.py`) — no separate init script
needed. It only creates tables that don't already exist, so it's safe to run
on every restart.

Swagger docs: http://localhost:8000/docs

### 1.5 Run the API

```bash
uvicorn app.main:app --reload --port 8000
```
Swagger docs: http://localhost:8000/docs

---

## 2. Architecture Overview

```
backend/app/
├── main.py                  FastAPI app, CORS, router registration
├── core/
│   ├── config.py             Centralised env-driven settings (pydantic-settings)
│   └── logging.py            Logging setup
├── db/
│   ├── base.py                SQLAlchemy declarative base
│   └── session.py             Engine, session factory, get_db dependency
├── models/                    SQLAlchemy ORM models (the DB schema, see §3)
│   ├── company.py
│   ├── price.py
│   ├── fundamental.py
│   └── backtest.py
├── schemas/                   Pydantic request/response contracts
│   ├── enums.py                Shared enums + the canonical metric list
│   ├── backtest.py
│   └── company.py
├── data_collection/            Ingestion pipeline (see §4)
│   ├── universe.py              The ~125-company NSE universe definition
│   ├── fetch_prices.py
│   ├── fetch_fundamentals.py
│   └── pipeline.py
├── backtest_engine/            The actual backtest logic (see §5)
│   ├── data_loader.py            Loads prices+fundamentals once per run
│   ├── filters.py                 Universe filtering (applied once)
│   ├── ranking.py                 Single/composite ranking
│   ├── position_sizing.py        Equal / market-cap / metric weighting
│   ├── rebalance_dates.py        Calendar -> trading-day-snapped dates
│   ├── metrics.py                 CAGR, Sharpe, Sortino, drawdown, alpha/beta
│   └── engine.py                  Orchestrator: ties everything together
├── strategies/
│   └── prebuilt.py               Bonus: ready-made strategy configs
├── api/routes/                  HTTP layer (thin — delegates to engine)
    ├── metadata.py
    ├── companies.py
    ├── backtest.py
    └── strategies.py

```
`db/base.py` also exposes `create_all_tables(engine)` — an idempotent
helper called both by the API server's startup (`main.py` `lifespan`) and by
the data-collection scripts, so tables exist automatically no matter which
entrypoint you run first.


**Design principle:** the HTTP layer (`api/routes`) never contains business
logic — it validates input (Pydantic), calls `BacktestEngine`, and serializes
the result. All backtest logic lives in `backtest_engine/`, independently
testable without spinning up FastAPI at all.

---

## 3. Database Schema

| Table | Grain | Purpose |
|---|---|---|
| `companies` | 1 row / instrument | Master reference (incl. the Nifty 50 benchmark, flagged `is_benchmark=True`, so it shares the exact same prices schema/query path as every equity) |
| `stock_prices` | 1 row / (company, date) | Daily OHLCV. Narrow & append-only — kept separate from fundamentals because it has a different grain (daily vs. quarterly) and a different access pattern (full date-range scans). |
| `fundamentals` | 1 row / (company, period_end_date, period_type) | Raw P&L / Balance Sheet / Cash Flow line items **and** derived ratios (ROE, ROCE, ROA, margins, etc.) in one table. See design note below. |
| `backtest_runs` | 1 row / run | The full request config (JSONB, for reproducibility) + run status |
| `backtest_results` | 1 row / (run, date) | Daily equity curve: portfolio value, benchmark value, drawdown, daily return — powers the equity curve & drawdown charts |
| `portfolio_holdings` | 1 row / (run, rebalance_date, stock) | The portfolio log: rank, weight, entry/exit price, realised return, contribution |
| `backtest_metrics` | 1 row / run | The summary scorecard: CAGR, Sharpe, Sortino, Max DD, alpha/beta vs. benchmark, etc. |

**Indexes:** `stock_prices(company_id, date)` and `fundamentals(company_id, report_date)`
are the two indexes the backtest engine's hot path relies on (point-in-time
lookups and date-range scans). `backtest_results(run_id, date)` and
`portfolio_holdings(run_id, rebalance_date)` support fast retrieval of a
specific run's outputs for the frontend / export.

**Design note — why fundamentals isn't split into "raw" and "ratios" tables:**
the backtest engine's hot path is "give me every metric needed for
filtering/ranking, for N companies, as of a point-in-time date" — at *every*
rebalance, of *every* run. Both raw line items and derived ratios share the
same grain (company + period), so splitting them would force an extra join
on that hot path for no normalization benefit. `stock_prices`, which has a
genuinely different grain (daily) and access pattern, **is** kept separate,
per the assignment's explicit requirement.

**Point-in-time correctness / no future-data leakage:** `fundamentals.report_date`
(not `period_end_date`) is what the engine filters on everywhere. Yahoo
Finance only exposes period-end dates, not actual filing dates, so
`report_date` is estimated as `period_end_date + reporting_lag`, using SEBI's
mandated filing windows (45 days for quarterly results, 60 days for audited
annual results) as a conservative default — see `Settings.QUARTERLY_REPORT_LAG_DAYS`
/ `ANNUAL_REPORT_LAG_DAYS` in `core/config.py`. This is a **documented
assumption**, not exact data — see §7.

---

## 4. Data Collection

- **Source:** Yahoo Finance via the `yfinance` library (prices + financial
  statements), per the assignment's allowed data sources.
- **Universe:** ~125 NSE-listed companies spanning 14 sectors (Financial
  Services, IT, Healthcare, Auto, FMCG, Energy, Metals, Cement, Capital
  Goods, Telecom, Consumer Durables, Chemicals, Realty, Diversified) —
  defined in `data_collection/universe.py`. Edit that one file to add/remove
  companies; everything downstream picks it up automatically.
- **Prices:** full daily OHLCV from `PRICE_HISTORY_START` (default
  2014-01-01) to today, upserted idempotently (safe to re-run).
- **Fundamentals:** annual + quarterly Income Statement, Balance Sheet and
  Cash Flow data via `yfinance.Ticker`, normalized across yfinance's
  occasionally-inconsistent row labels (`_find_row` tries several candidate
  labels per field), then derives: EPS, Book Value/Share, ROE, ROCE, ROA,
  Debt/Equity, Current Ratio, Operating Margin, Net Margin, Free Cash Flow.
- **Resilience:** every ticker is fetched in its own try/except so one
  failing symbol never aborts the whole pipeline; failures are logged with
  the ticker name for manual follow-up.

---

## 5. Backtest Engine — How It Works

1. **Load once:** `data_loader.load_market_dataset` pulls *all* prices and
   fundamentals for the date range into memory (a date×company price panel +
   a flat fundamentals table) in two queries total — not one query per
   rebalance per company (`MarketDataset`).
2. **Filter once:** `filters.apply_filters` is evaluated a single time, using
   the point-in-time fundamentals snapshot as of the *first* rebalance date
   (Market Cap range, ROCE > X%, PAT > 0, Debt/Equity ≤ X, ROE > X%). The
   resulting eligible company list is fixed for the entire run — only each
   company's *metric values* are refreshed at every rebalance, never the
   universe membership, per the spec ("applied once at the beginning, used
   for every rebalance").
3. **Walk forward:** `rebalance_dates.build_rebalance_dates` generates
   monthly / quarterly / half-yearly / yearly dates and snaps each to the
   next available trading day. At each rebalance:
   - `ranking.rank_companies` computes a per-metric rank (single metric, or
     a weighted average of ranks across several metrics for composite
     ranking), sorted best-first.
   - The top N (`portfolio_size`) are selected.
   - `position_sizing.compute_weights` turns the selection into weights:
     equal-weighted, market-cap-weighted, or metric-weighted (e.g. weight ∝
     ROCE), with safe fallbacks (negative weights are clipped to zero and
     logged, never shorted).
   - Capital is allocated using **that period's actual portfolio value**
     (the prior period's exit value) — i.e., compounding, not a fixed
     initial-capital re-deploy.
   - Daily mark-to-market values are computed for every trading day in the
     holding period (vectorised: `price_slice * shares`), which is what
     builds the equity curve and drawdown chart.
4. **Analytics:** `metrics.py` computes CAGR, annualised volatility, Sharpe,
   Sortino, Max Drawdown, Calmar, win rate (% of rebalance periods with a
   positive return), and alpha/beta vs. the Nifty 50 benchmark (OLS slope/
   intercept of daily returns).
5. **Persist:** one `BacktestRun`, N `BacktestResult` rows (daily equity
   curve), M `PortfolioHolding` rows (full portfolio log), and one
   `BacktestMetrics` row.

**No future-data leakage, by construction** — not bolted on after the fact:
- Every fundamental lookup goes through `MarketDataset.point_in_time_snapshot(as_of_date)`,
  which only considers rows with `report_date <= as_of_date`.
- Trade prices are always the price *on or after* the rebalance date for
  entries, and *on or before* the next rebalance date for exits — never a
  price from before the decision date or after the holding period.
- The filter universe is locked in using only data available at the first
  rebalance date; nothing computed later can change which companies were
  eligible at the start.

---

## 6. API Reference (summary — full interactive docs at `/docs`)

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/metadata/backtest-options` | Enums/options for building the config form (rebalance frequencies, sizing methods, rankable metrics, etc.) **+ `data_start_date`/`data_end_date`** - the safe date window for a custom backtest, computed live from the DB |
| GET | `/api/v1/companies` | List the ingested universe |
| GET | `/api/v1/companies/stats` | Universe stats (row counts, date coverage, sectors) |
| POST | `/api/v1/backtest/run` | Run a backtest, returns full results immediately |
| GET | `/api/v1/backtest/runs` | List past runs (history) |
| GET | `/api/v1/backtest/{run_id}` | Fetch a run's full results |
| DELETE | `/api/v1/backtest/{run_id}` | Delete a run |
| POST | `/api/v1/backtest/compare` | **Bonus:** compare 2-5 runs side by side |
| GET | `/api/v1/backtest/{run_id}/export?format=csv\|xlsx&table=holdings\|equity_curve` | Export portfolio log or equity curve |
| GET | `/api/v1/strategies/prebuilt` | **Bonus:** list prebuilt strategy configs |
| POST | `/api/v1/strategies/prebuilt/{key}/run` | **Bonus:** run a prebuilt strategy |

---

## 7. Assumptions & Known Simplifications

- **Reporting lag for point-in-time data:** see §3 — `report_date` is
  estimated (period end + 45/60 days), not the actual filing date, since
  Yahoo Finance doesn't expose filing dates. This is the single biggest
  assumption in the system and is the standard approach for this kind of
  project when working from index-style providers rather than a regulatory
  filings feed.
- **Prices used throughout are adjusted close** (`adj_close`), so returns
  already account for splits/dividends/bonus issues without separate
  corporate-action handling.
- **Shares outstanding** is taken from the balance sheet for that period
  where available; if missing, it's backed out from `Net Income / Diluted EPS`,
  and as a last resort falls back to the company's *current* shares
  outstanding (`yfinance` doesn't expose a clean historical shares-outstanding
  series).
- **Universe is static** (curated list, not auto-updated index membership) —
  there's no survivorship-bias correction beyond what's naturally present in
  Yahoo Finance's data (delisted/renamed companies are not separately
  tracked).
- **No transaction costs / slippage / taxes** are modeled — returns are
  gross.
- If fewer than `portfolio_size` companies pass the filters, the portfolio
  simply holds however many are available.
- A holding with no exit price available at the next rebalance (e.g. a data
  gap) is treated as a 0% return for that leg rather than dropped, so a data
  gap can't silently destroy or create capital.
- **Custom strategy date range is bounded by actual data coverage, not the
  full price history.** Different companies start reporting fundamentals at
  different times (IPOs, coverage added later, etc.), so a `start_date`
  earlier than the date by which *every* company has at least one report
  would quietly shrink/bias the eligible universe instead of erroring -
  e.g. a strategy backtested from an early date might only see 40 eligible
  companies where a later date sees 120, for reasons that have nothing to
  do with the strategy itself. `data_loader.get_available_date_range()`
  computes this "safe universal start date" (and the latest date with price
  data, as the safe end) live from the DB on every request to
  `/metadata/backtest-options`; the frontend uses it to constrain the date
  pickers (see frontend README §5), and `BacktestEngine.run()` re-checks it
  server-side and raises a clear `ValueError` if a request slips through
  outside that window. The prebuilt strategies are already defined within
  this window, so this never affects them - it only guards user-defined
  custom strategies.

## 8. Future Improvements (out of scope for this assignment)
- Alembic migrations instead of `create_all` for schema versioning
- Async/background execution (Celery/RQ) for very large backtests
- Point-in-time financial statement vendor (e.g. actual filing-date feed) to
  remove the reporting-lag assumption
- Transaction cost & slippage modelling
