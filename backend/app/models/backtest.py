import enum
import uuid
from datetime import date as date_type
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Date,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class BacktestStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class BacktestRun(Base):
    """
    One row per backtest execution. `config` stores the full request payload
    (filters, ranking, sizing, dates, etc.) as JSONB so the exact run is fully
    reproducible/auditable, and so new config fields never require a schema
    migration.
    """

    __tablename__ = "backtest_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[BacktestStatus] = mapped_column(
        Enum(BacktestStatus, name="backtest_status_enum"), default=BacktestStatus.PENDING
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    results = relationship("BacktestResult", back_populates="run", cascade="all, delete-orphan")
    holdings = relationship("PortfolioHolding", back_populates="run", cascade="all, delete-orphan")
    metrics = relationship(
        "BacktestMetrics", back_populates="run", cascade="all, delete-orphan", uselist=False
    )

    __table_args__ = (Index("ix_backtest_runs_created_at", "created_at"),)

class BacktestResult(Base):
    """Daily equity-curve point: portfolio value vs benchmark, for charting."""

    __tablename__ = "backtest_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("backtest_runs.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    portfolio_value: Mapped[float] = mapped_column(Float, nullable=False)
    benchmark_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    drawdown_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    daily_return_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    run = relationship("BacktestRun", back_populates="results")

    __table_args__ = (Index("ix_backtest_results_run_date", "run_id", "date"),)

class PortfolioHolding(Base):
    """
    One row per (run, rebalance_date, stock held). Captures the full
    portfolio log: rank/metric used for selection, weight, entry/exit price
    and realised return for that holding period.
    """

    __tablename__ = "portfolio_holdings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("backtest_runs.id", ondelete="CASCADE"), nullable=False
    )
    rebalance_date: Mapped[date_type] = mapped_column(Date, nullable=False)
    next_rebalance_date: Mapped[date_type | None] = mapped_column(Date, nullable=True)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)  # denormalised for fast export
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    ranking_metric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_pct: Mapped[float] = mapped_column(Float, nullable=False)
    shares: Mapped[float] = mapped_column(Float, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    exit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    return_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    contribution_pct: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )  # this holding's contribution to that period's portfolio return

    run = relationship("BacktestRun", back_populates="holdings")

    __table_args__ = (
        Index("ix_portfolio_holdings_run_rebalance", "run_id", "rebalance_date"),
        Index("ix_portfolio_holdings_run_symbol", "run_id", "symbol"),
    )

class BacktestMetrics(Base):
    """One row per run - the summary performance scorecard."""

    __tablename__ = "backtest_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("backtest_runs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    total_return_pct: Mapped[float] = mapped_column(Float, nullable=False)
    cagr_pct: Mapped[float] = mapped_column(Float, nullable=False)
    volatility_pct: Mapped[float] = mapped_column(Float, nullable=False)
    sharpe_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    sortino_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    max_drawdown_pct: Mapped[float] = mapped_column(Float, nullable=False)
    calmar_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    win_rate_pct: Mapped[float] = mapped_column(Float, nullable=False)  # % of rebalance periods with positive return
    best_period_return_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    worst_period_return_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Benchmark comparison
    benchmark_total_return_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    benchmark_cagr_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    benchmark_max_drawdown_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    alpha_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    beta: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    run = relationship("BacktestRun", back_populates="metrics")
