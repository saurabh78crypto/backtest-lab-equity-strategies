import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.enums import RANKABLE_METRICS, PositionSizingMethod, RankingOrder, RebalanceFrequency

class FilterConfig(BaseModel):
    """
    Stock universe filters - applied ONCE at the backtest start date and
    reused, unchanged, for every subsequent rebalance.
    """
    market_cap_min_cr: Optional[float] = Field(
        None, description="Minimum market cap in INR Crores, e.g. 1000"
    )
    market_cap_max_cr: Optional[float] = Field(
        None, description="Maximum market cap in INR Crores, e.g. 10000"
    )
    roce_min_pct: Optional[float] = Field(None, description="ROCE must be > this value (%)")
    pat_positive: bool = Field(False, description="Require PAT (net profit) > 0")
    debt_to_equity_max: Optional[float] = None
    roe_min_pct: Optional[float] = None

    @model_validator(mode="after")
    def validate_range(self):
        if (
            self.market_cap_min_cr is not None
            and self.market_cap_max_cr is not None
            and self.market_cap_min_cr > self.market_cap_max_cr
        ):
            raise ValueError("market_cap_min_cr cannot exceed market_cap_max_cr")
        return self

class RankingMetric(BaseModel):
    metric: str = Field(..., description="One of the supported ranking metrics, e.g. 'roe'")
    order: RankingOrder = RankingOrder.DESCENDING
    weight: float = Field(1.0, gt=0, description="Relative weight in composite rank average")

    @field_validator("metric")
    @classmethod
    def metric_supported(cls, v: str) -> str:
        if v not in RANKABLE_METRICS:
            raise ValueError(f"Unsupported metric '{v}'. Must be one of: {', '.join(RANKABLE_METRICS)}")
        return v

class RankingConfig(BaseModel):
    metrics: List[RankingMetric] = Field(
        ..., min_length=1, description="One metric = simple rank. Multiple = composite rank."
    )

class BacktestConfigRequest(BaseModel):
    name: str = Field(..., max_length=255, examples=["Quality ROCE Strategy"])
    start_date: date
    end_date: date
    rebalance_frequency: RebalanceFrequency = RebalanceFrequency.QUARTERLY
    portfolio_size: int = Field(20, ge=1, le=200)
    position_sizing: PositionSizingMethod = PositionSizingMethod.EQUAL_WEIGHTED
    position_sizing_metric: Optional[str] = Field(
        None, description="Required when position_sizing = metric_weighted, e.g. 'roce'"
    )
    initial_capital: float = Field(1_000_000, gt=0)
    filters: FilterConfig = FilterConfig()
    ranking: RankingConfig
    include_benchmark: bool = True
    benchmark_symbol: Optional[str] = None  # defaults to settings.BENCHMARK_SYMBOL

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v: date, info):
        start = info.data.get("start_date")
        if start and v <= start:
            raise ValueError("end_date must be after start_date")
        return v

    @model_validator(mode="after")
    def validate_metric_weighting(self):
        if self.position_sizing == PositionSizingMethod.METRIC_WEIGHTED:
            if not self.position_sizing_metric:
                raise ValueError("position_sizing_metric is required for metric_weighted sizing")
            if self.position_sizing_metric not in RANKABLE_METRICS:
                raise ValueError(
                    f"Unsupported position_sizing_metric '{self.position_sizing_metric}'. "
                    f"Must be one of: {', '.join(RANKABLE_METRICS)}"
                )
        return self

class BacktestRunSummary(BaseModel):
    id: uuid.UUID
    name: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}

class EquityCurvePoint(BaseModel):
    date: date
    portfolio_value: float
    benchmark_value: Optional[float] = None
    drawdown_pct: float
    daily_return_pct: float

    model_config = {"from_attributes": True}

class HoldingLog(BaseModel):
    rebalance_date: date
    next_rebalance_date: Optional[date] = None
    symbol: str
    rank: int
    ranking_metric_value: Optional[float] = None
    weight_pct: float
    shares: float
    entry_price: float
    exit_price: Optional[float] = None
    return_pct: Optional[float] = None
    contribution_pct: Optional[float] = None

    model_config = {"from_attributes": True}

class PerformanceMetrics(BaseModel):
    total_return_pct: float
    cagr_pct: float
    volatility_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown_pct: float
    calmar_ratio: Optional[float] = None
    win_rate_pct: float
    best_period_return_pct: Optional[float] = None
    worst_period_return_pct: Optional[float] = None
    benchmark_total_return_pct: Optional[float] = None
    benchmark_cagr_pct: Optional[float] = None
    benchmark_max_drawdown_pct: Optional[float] = None
    alpha_pct: Optional[float] = None
    beta: Optional[float] = None

    model_config = {"from_attributes": True}

class WinnerLoser(BaseModel):
    symbol: str
    rebalance_date: date
    return_pct: float

class BacktestRunDetail(BaseModel):
    run: BacktestRunSummary
    config: dict
    metrics: Optional[PerformanceMetrics] = None
    equity_curve: List[EquityCurvePoint] = []
    holdings: List[HoldingLog] = []
    top_winners: List[WinnerLoser] = []
    top_losers: List[WinnerLoser] = []

class CompareRunsRequest(BaseModel):
    run_ids: List[uuid.UUID] = Field(..., min_length=2, max_length=5)

class CompareRunsResponse(BaseModel):
    runs: List[BacktestRunSummary]
    equity_curves: dict  # run_id (str) -> List[EquityCurvePoint]
    metrics: dict  # run_id (str) -> PerformanceMetrics
