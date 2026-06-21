"""
The BacktestEngine ties together filters -> ranking -> position sizing ->
rebalancing -> performance analytics, and persists the full result set.

No-future-data-leakage guarantee, by construction:
  - The eligible universe is computed once, using only fundamentals whose
    `report_date <= first_rebalance_date` (see filters.apply_filters).
  - At every subsequent rebalance, ranking metrics are re-read via
    MarketDataset.point_in_time_snapshot(rebalance_date), which again only
    considers rows with `report_date <= rebalance_date`.
  - Trade prices are always the price on (or the next available trading day
    on/after) the rebalance date itself - never a future price.
"""
import logging
import uuid
from datetime import date, datetime

import pandas as pd
from sqlalchemy.orm import Session

from app.backtest_engine import metrics as perf
from app.backtest_engine.data_loader import MarketDataset, get_available_date_range, load_market_dataset
from app.backtest_engine.filters import apply_filters
from app.backtest_engine.position_sizing import compute_weights
from app.backtest_engine.ranking import rank_companies
from app.backtest_engine.rebalance_dates import build_rebalance_dates
from app.models import BacktestMetrics, BacktestResult, BacktestRun, BacktestStatus, PortfolioHolding
from app.schemas.backtest import BacktestConfigRequest

logger = logging.getLogger(__name__)

class BacktestEngine:
    def __init__(self, db: Session, config: BacktestConfigRequest):
        self.db = db
        self.config = config

    # Public entrypoint
    def run(self) -> BacktestRun:
        run = BacktestRun(
            id=uuid.uuid4(),
            name=self.config.name,
            config=self.config.model_dump(mode="json"),
            status=BacktestStatus.RUNNING,
        )
        self.db.add(run)
        self.db.flush()

        try:
            data_start, data_end = get_available_date_range(self.db)
            if data_start and data_end and (self.config.start_date < data_start or self.config.end_date > data_end):
                raise ValueError(
                    f"Selected date range ({self.config.start_date} to {self.config.end_date}) is outside "
                    f"the data available in the database ({data_start} to {data_end}). ..."
                )
                
            dataset = load_market_dataset(
                self.db, self.config.start_date, self.config.end_date, include_benchmark=True
            )
            if dataset.price_panel.empty:
                raise ValueError(
                    "No price data found for the selected date range. Run the data "
                    "collection pipeline first (see README)."
                )

            result = self._execute(dataset)
            self._persist(run, result)
            run.status = BacktestStatus.COMPLETED
            run.completed_at = datetime.utcnow()
        except Exception as exc:
            logger.exception("Backtest run %s failed", run.id)
            run.status = BacktestStatus.FAILED
            run.error_message = str(exc)
            self.db.flush()
            raise
        self.db.flush()
        return run

    # Core simulation
    def _execute(self, dataset: MarketDataset) -> dict:
        cfg = self.config
        trading_dates = dataset.trading_dates
        rebalance_dates = build_rebalance_dates(cfg.start_date, cfg.end_date, cfg.rebalance_frequency, trading_dates)
        if len(rebalance_dates) < 1:
            raise ValueError("No valid rebalance dates within the available price data range")

        benchmark_id = self._benchmark_company_id(dataset)
        equity_ids = [cid for cid in dataset.companies.index if not dataset.companies.loc[cid, "is_benchmark"]]

        # Step 1: filters, applied ONCE at the first rebalance date 
        first_date = rebalance_dates[0]
        snapshot0 = dataset.point_in_time_snapshot(first_date)
        snapshot0 = snapshot0.loc[snapshot0.index.intersection(equity_ids)]
        market_caps0 = dataset.market_caps_on(first_date, equity_ids)
        eligible_ids = apply_filters(snapshot0, market_caps0, cfg.filters)
        if not eligible_ids:
            raise ValueError(
                "No companies passed the configured filters as of the start date. "
                "Try relaxing the filter thresholds."
            )
        logger.info("Eligible universe after filtering: %d companies", len(eligible_ids))

        # Step 2: walk-forward rebalancing 
        portfolio_value = cfg.initial_capital
        equity_points: list[dict] = []
        holdings_rows: list[dict] = []
        period_returns: list[float] = []

        last_trading_date = trading_dates[-1].date()

        for i, rdate in enumerate(rebalance_dates):
            next_rdate = rebalance_dates[i + 1] if i + 1 < len(rebalance_dates) else last_trading_date

            metrics_df = self._build_metrics_frame(dataset, eligible_ids, rdate)
            if metrics_df.empty:
                logger.warning("No tradeable companies with price data at %s - skipping rebalance", rdate)
                continue

            ranked = rank_companies(metrics_df, cfg.ranking)
            selected = ranked.head(min(cfg.portfolio_size, len(ranked))).copy()

            weights = compute_weights(selected, cfg.position_sizing, metric_col=cfg.position_sizing_metric)
            selected["weight"] = weights

            primary_metric = cfg.ranking.metrics[0].metric
            shares_by_id: dict = {}
            period_value_start = portfolio_value

            for rank_pos, (cid, row) in enumerate(selected.iterrows(), start=1):
                weight = float(row["weight"])
                entry_price = float(row["entry_price"])
                alloc = period_value_start * weight
                shares = alloc / entry_price if entry_price > 0 else 0.0
                shares_by_id[cid] = shares

                # Exit price = price on/just before the next rebalance date (or the
                # final trading date for the last leg). Falls back to entry_price
                # (0% return) only if no later price exists at all (e.g. delisting),
                # so a data gap never silently destroys/creates capital.
                exit_price = dataset.price_on_or_before(cid, next_rdate) or entry_price
                return_pct = (exit_price / entry_price - 1) * 100 if entry_price > 0 else None
                contribution_pct = (weight * return_pct) if return_pct is not None else None

                holdings_rows.append(
                    {
                        "rebalance_date": rdate,
                        "next_rebalance_date": next_rdate if i + 1 < len(rebalance_dates) else None,
                        "company_id": cid,
                        "symbol": dataset.companies.loc[cid, "trading_symbol"],
                        "rank": rank_pos,
                        "ranking_metric_value": float(row[primary_metric]) if pd.notna(row.get(primary_metric)) else None,
                        "weight_pct": weight * 100,
                        "shares": shares,
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "return_pct": return_pct,
                        "contribution_pct": contribution_pct,
                    }
                )

            # daily mark-to-market for this holding period (compounding) 
            period_dates = trading_dates[(trading_dates >= pd.Timestamp(rdate)) & (trading_dates <= pd.Timestamp(next_rdate))]
            held_ids = list(shares_by_id.keys())
            if len(period_dates) > 0 and held_ids:
                price_slice = dataset.price_panel.loc[period_dates, held_ids].ffill()
                shares_series = pd.Series(shares_by_id)
                period_value_series = (price_slice * shares_series).sum(axis=1)
                for d, v in period_value_series.items():
                    equity_points.append({"date": d.date(), "portfolio_value": float(v)})
                portfolio_value = float(period_value_series.iloc[-1])
            period_returns.append((portfolio_value / period_value_start - 1) * 100 if period_value_start > 0 else 0.0)

        if not equity_points:
            raise ValueError("Backtest produced no valuation points - check date range and universe data coverage")

        equity_df = (
            pd.DataFrame(equity_points)
            .drop_duplicates(subset="date", keep="last")
            .sort_values("date")
            .set_index("date")
        )
        equity_series = equity_df["portfolio_value"]
        equity_series.index = pd.to_datetime(equity_series.index)

        # benchmark series (buy & hold, normalised to initial capital) 
        benchmark_series = None
        if cfg.include_benchmark and benchmark_id is not None:
            bench_prices = dataset.price_panel.get(benchmark_id)
            if bench_prices is not None:
                bench_prices = bench_prices.reindex(equity_series.index).ffill().bfill()
                base = bench_prices.iloc[0]
                if base and base > 0:
                    benchmark_series = bench_prices / base * cfg.initial_capital

        result = {
            "equity_series": equity_series,
            "benchmark_series": benchmark_series,
            "holdings_rows": holdings_rows,
            "period_returns": period_returns,
        }
        return result

    # Helpers
    @staticmethod
    def _benchmark_company_id(dataset: MarketDataset):
        if dataset.companies.empty:
            return None
        bench = dataset.companies[dataset.companies["is_benchmark"]]
        return bench.index[0] if len(bench) else None

    @staticmethod
    def _build_metrics_frame(dataset: MarketDataset, eligible_ids: list, rdate: date) -> pd.DataFrame:
        snapshot = dataset.point_in_time_snapshot(rdate)
        snapshot = snapshot.loc[snapshot.index.intersection(eligible_ids)]
        if snapshot.empty:
            return snapshot
        market_caps = dataset.market_caps_on(rdate, eligible_ids)

        rows = []
        for cid, frow in snapshot.iterrows():
            price_info = dataset.price_on_or_after(cid, rdate)
            if price_info is None:
                continue
            price_date, price = price_info
            row = frow.to_dict()
            row["market_cap"] = market_caps.get(cid)
            row["entry_price"] = price
            row["entry_date"] = price_date
            eps, bvps = row.get("eps"), row.get("book_value_per_share")
            row["pe_ratio"] = (price / eps) if eps and eps > 0 else None
            row["pb_ratio"] = (price / bvps) if bvps and bvps > 0 else None
            row["company_id"] = cid
            rows.append(row)

        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows).set_index("company_id")
    
    # Persistence
    def _persist(self, run: BacktestRun, result: dict) -> None:
        equity_series: pd.Series = result["equity_series"]
        benchmark_series: pd.Series | None = result["benchmark_series"]
        dd = perf.drawdown_series(equity_series)
        rets = perf.daily_returns(equity_series)

        for d in equity_series.index:
            self.db.add(
                BacktestResult(
                    run_id=run.id,
                    date=d.date(),
                    portfolio_value=float(equity_series.loc[d]),
                    benchmark_value=float(benchmark_series.loc[d]) if benchmark_series is not None and d in benchmark_series.index else None,
                    drawdown_pct=float(dd.loc[d]),
                    daily_return_pct=float(rets.loc[d]) if d in rets.index else 0.0,
                )
            )

        for h in result["holdings_rows"]:
            self.db.add(PortfolioHolding(run_id=run.id, **h))

        cagr = perf.cagr_pct(equity_series)
        max_dd = perf.max_drawdown_pct(equity_series)
        period_returns = result["period_returns"]

        bench_total_ret = bench_cagr = bench_max_dd = alpha = beta = None
        if benchmark_series is not None:
            bench_total_ret = perf.total_return_pct(benchmark_series)
            bench_cagr = perf.cagr_pct(benchmark_series)
            bench_max_dd = perf.max_drawdown_pct(benchmark_series)
            bench_rets = perf.daily_returns(benchmark_series)
            alpha, beta = perf.alpha_beta(rets, bench_rets)

        self.db.add(
            BacktestMetrics(
                run_id=run.id,
                total_return_pct=perf.total_return_pct(equity_series),
                cagr_pct=cagr,
                volatility_pct=perf.volatility_pct(rets),
                sharpe_ratio=perf.sharpe_ratio(rets),
                sortino_ratio=perf.sortino_ratio(rets),
                max_drawdown_pct=max_dd,
                calmar_ratio=perf.calmar_ratio(cagr, max_dd),
                win_rate_pct=perf.win_rate_pct(period_returns),
                best_period_return_pct=max(period_returns) if period_returns else None,
                worst_period_return_pct=min(period_returns) if period_returns else None,
                benchmark_total_return_pct=bench_total_ret,
                benchmark_cagr_pct=bench_cagr,
                benchmark_max_drawdown_pct=bench_max_dd,
                alpha_pct=alpha,
                beta=beta,
            )
        )
