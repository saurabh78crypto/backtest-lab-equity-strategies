"""
Bonus feature: a small library of prebuilt, ready-to-run strategy configs so
the frontend can offer one-click demos instead of forcing a user to build a
config from scratch every time.
"""
from datetime import date

from app.schemas.backtest import BacktestConfigRequest, FilterConfig, RankingConfig, RankingMetric
from app.schemas.enums import PositionSizingMethod, RankingOrder, RebalanceFrequency

DEFAULT_START = date(2023, 5, 30)
DEFAULT_END = date(2026, 5, 30)

def _base(**overrides) -> dict:
    base = dict(
        start_date=DEFAULT_START,
        end_date=DEFAULT_END,
        rebalance_frequency=RebalanceFrequency.QUARTERLY,
        portfolio_size=20,
        position_sizing=PositionSizingMethod.EQUAL_WEIGHTED,
        initial_capital=1_000_000,
        include_benchmark=True,
    )
    base.update(overrides)
    return base

PREBUILT_STRATEGIES: dict[str, BacktestConfigRequest] = {
    "quality_roce": BacktestConfigRequest(
        **_base(
            name="Quality - High ROCE",
            filters=FilterConfig(market_cap_min_cr=1000, roce_min_pct=15, pat_positive=True),
            ranking=RankingConfig(metrics=[RankingMetric(metric="roce", order=RankingOrder.DESCENDING, weight=1)]),
        )
    ),
    "value_pe": BacktestConfigRequest(
        **_base(
            name="Value - Low PE, Positive Earnings",
            filters=FilterConfig(market_cap_min_cr=1000, pat_positive=True, debt_to_equity_max=1.5),
            ranking=RankingConfig(metrics=[RankingMetric(metric="pe_ratio", order=RankingOrder.ASCENDING, weight=1)]),
        )
    ),
    "composite_quality_value": BacktestConfigRequest(
        **_base(
            name="Composite Quality + Value",
            filters=FilterConfig(market_cap_min_cr=1000, roce_min_pct=10, pat_positive=True),
            ranking=RankingConfig(
                metrics=[
                    RankingMetric(metric="roe", order=RankingOrder.DESCENDING, weight=1),
                    RankingMetric(metric="pe_ratio", order=RankingOrder.ASCENDING, weight=1),
                ]
            ),
        )
    ),
    "large_cap_market_cap_weighted": BacktestConfigRequest(
        **_base(
            name="Large Cap - Market Cap Weighted",
            portfolio_size=30,
            position_sizing=PositionSizingMethod.MARKET_CAP_WEIGHTED,
            filters=FilterConfig(market_cap_min_cr=20000, pat_positive=True),
            ranking=RankingConfig(metrics=[RankingMetric(metric="market_cap", order=RankingOrder.DESCENDING, weight=1)]),
        )
    ),
    "small_mid_cap_growth": BacktestConfigRequest(
        **_base(
            name="Small-Mid Cap Growth",
            filters=FilterConfig(market_cap_min_cr=1000, market_cap_max_cr=80000, pat_positive=True, roce_min_pct=12),
            ranking=RankingConfig(metrics=[RankingMetric(metric="net_margin", order=RankingOrder.DESCENDING, weight=1)]),
        )
    ),
}

def list_prebuilt_strategies() -> list[dict]:
    return [{"key": key, "config": cfg.model_dump(mode="json")} for key, cfg in PREBUILT_STRATEGIES.items()]

def get_prebuilt_strategy(key: str) -> BacktestConfigRequest | None:
    return PREBUILT_STRATEGIES.get(key)
