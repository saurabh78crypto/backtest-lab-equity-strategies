import io
import uuid

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.serializers import build_run_detail, get_run_or_404
from app.backtest_engine.engine import BacktestEngine
from app.db.session import get_db
from app.models import BacktestRun, PortfolioHolding
from app.schemas.backtest import (
    BacktestConfigRequest,
    BacktestRunDetail,
    BacktestRunSummary,
    CompareRunsRequest,
    CompareRunsResponse,
    EquityCurvePoint,
    PerformanceMetrics,
)

router = APIRouter(prefix="/backtest", tags=["backtest"])

@router.post("/run", response_model=BacktestRunDetail)
def run_backtest(config: BacktestConfigRequest, db: Session = Depends(get_db)):
    engine = BacktestEngine(db, config)
    try:
        run = engine.run()
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db.refresh(run)
    return build_run_detail(run)

@router.get("/runs", response_model=list[BacktestRunSummary])
def list_runs(db: Session = Depends(get_db), limit: int = Query(50, le=200)):
    runs = db.execute(select(BacktestRun).order_by(BacktestRun.created_at.desc()).limit(limit)).scalars().all()
    return [BacktestRunSummary.model_validate(r) for r in runs]

@router.get("/{run_id}", response_model=BacktestRunDetail)
def get_run(run_id: uuid.UUID, db: Session = Depends(get_db)):
    run = get_run_or_404(db, run_id)
    return build_run_detail(run)

@router.delete("/{run_id}", status_code=204)
def delete_run(run_id: uuid.UUID, db: Session = Depends(get_db)):
    run = get_run_or_404(db, run_id)
    db.delete(run)
    db.commit()

@router.post("/compare", response_model=CompareRunsResponse)
def compare_runs(payload: CompareRunsRequest, db: Session = Depends(get_db)):
    runs = []
    equity_curves = {}
    metrics_by_run = {}
    for run_id in payload.run_ids:
        run = get_run_or_404(db, run_id)
        runs.append(BacktestRunSummary.model_validate(run))
        equity_curves[str(run_id)] = [
            EquityCurvePoint.model_validate(r) for r in sorted(run.results, key=lambda r: r.date)
        ]
        if run.metrics:
            metrics_by_run[str(run_id)] = PerformanceMetrics.model_validate(run.metrics)

    return CompareRunsResponse(runs=runs, equity_curves=equity_curves, metrics=metrics_by_run)

@router.get("/{run_id}/export")
def export_run(
    run_id: uuid.UUID,
    db: Session = Depends(get_db),
    format: str = Query("xlsx", pattern="^(csv|xlsx)$"),
    table: str = Query("holdings", pattern="^(holdings|equity_curve)$"),
):
    run = get_run_or_404(db, run_id)

    if table == "holdings":
        rows = db.execute(
            select(PortfolioHolding)
            .where(PortfolioHolding.run_id == run_id)
            .order_by(PortfolioHolding.rebalance_date, PortfolioHolding.rank)
        ).scalars().all()
        df = pd.DataFrame(
            [
                {
                    "rebalance_date": h.rebalance_date,
                    "next_rebalance_date": h.next_rebalance_date,
                    "symbol": h.symbol,
                    "rank": h.rank,
                    "ranking_metric_value": h.ranking_metric_value,
                    "weight_pct": h.weight_pct,
                    "shares": h.shares,
                    "entry_price": h.entry_price,
                    "exit_price": h.exit_price,
                    "return_pct": h.return_pct,
                    "contribution_pct": h.contribution_pct,
                }
                for h in rows
            ]
        )
        filename_base = "portfolio_holdings"
    else:
        results = sorted(run.results, key=lambda r: r.date)
        df = pd.DataFrame(
            [
                {
                    "date": r.date,
                    "portfolio_value": r.portfolio_value,
                    "benchmark_value": r.benchmark_value,
                    "drawdown_pct": r.drawdown_pct,
                    "daily_return_pct": r.daily_return_pct,
                }
                for r in results
            ]
        )
        filename_base = "equity_curve"

    if format == "csv":
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        buf.seek(0)
        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename_base}_{run_id}.csv"},
        )

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=table[:31])
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename_base}_{run_id}.xlsx"},
    )
