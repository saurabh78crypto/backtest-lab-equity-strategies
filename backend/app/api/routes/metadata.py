from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backtest_engine.data_loader import get_available_date_range
from app.core.config import settings
from app.db.session import get_db
from app.schemas.enums import (
    FILTERABLE_METRICS,
    RANKABLE_METRICS,
    PositionSizingMethod,
    RankingOrder,
    RebalanceFrequency,
)

router = APIRouter(prefix="/metadata", tags=["metadata"])

@router.get("/backtest-options")
def get_backtest_options(db: Session = Depends(get_db)):
    """Single source of truth for every dropdown/enum the config form needs."""
    data_start_date, data_end_date = get_available_date_range(db)
    return {
        "rebalance_frequencies": [f.value for f in RebalanceFrequency],
        "position_sizing_methods": [m.value for m in PositionSizingMethod],
        "ranking_orders": [o.value for o in RankingOrder],
        "rankable_metrics": RANKABLE_METRICS,
        "filterable_metrics": FILTERABLE_METRICS,
        "benchmark_symbol": settings.BENCHMARK_SYMBOL,
        "benchmark_name": settings.BENCHMARK_NAME,
        "data_start_date": str(data_start_date) if data_start_date else None,
        "data_end_date": str(data_end_date) if data_end_date else None,
    }
