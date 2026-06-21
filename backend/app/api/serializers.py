"""
Shared ORM -> Pydantic serialization for a BacktestRun, used by both the
`/backtest` and `/strategies` route modules.
"""
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import BacktestRun
from app.schemas.backtest import (
    BacktestRunDetail,
    BacktestRunSummary,
    EquityCurvePoint,
    HoldingLog,
    PerformanceMetrics,
    WinnerLoser,
)

def get_run_or_404(db: Session, run_id: uuid.UUID) -> BacktestRun:
    run = db.get(BacktestRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Backtest run not found")
    return run

def build_run_detail(run: BacktestRun) -> BacktestRunDetail:
    equity_curve = [EquityCurvePoint.model_validate(r) for r in sorted(run.results, key=lambda r: r.date)]
    holdings = [HoldingLog.model_validate(h) for h in sorted(run.holdings, key=lambda h: (h.rebalance_date, h.rank))]
    metrics = PerformanceMetrics.model_validate(run.metrics) if run.metrics else None

    closed_holdings = [h for h in run.holdings if h.return_pct is not None]
    winners = sorted(closed_holdings, key=lambda h: h.return_pct, reverse=True)[:10]
    losers = sorted(closed_holdings, key=lambda h: h.return_pct)[:10]

    return BacktestRunDetail(
        run=BacktestRunSummary.model_validate(run),
        config=run.config,
        metrics=metrics,
        equity_curve=equity_curve,
        holdings=holdings,
        top_winners=[WinnerLoser(symbol=h.symbol, rebalance_date=h.rebalance_date, return_pct=h.return_pct) for h in winners],
        top_losers=[WinnerLoser(symbol=h.symbol, rebalance_date=h.rebalance_date, return_pct=h.return_pct) for h in losers],
    )
