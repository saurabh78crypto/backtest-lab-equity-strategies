"""
Enums shared between the API layer (Pydantic schemas) and the backtest
engine, so the two never drift out of sync.
"""
import enum

class RebalanceFrequency(str, enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    YEARLY = "yearly"

class PositionSizingMethod(str, enum.Enum):
    EQUAL_WEIGHTED = "equal_weighted"
    MARKET_CAP_WEIGHTED = "market_cap_weighted"
    METRIC_WEIGHTED = "metric_weighted"

class RankingOrder(str, enum.Enum):
    ASCENDING = "ascending"   # e.g. PE - lower is "better"
    DESCENDING = "descending"  # e.g. ROE - higher is "better"

# Metrics that are valid for filtering / ranking / metric-weighting.
RANKABLE_METRICS = [
    "roe", "roce", "roa", "pat", "revenue", "eps", "book_value_per_share",
    "debt_to_equity", "current_ratio", "operating_margin", "net_margin",
    "free_cash_flow", "market_cap", "pe_ratio", "pb_ratio",
]

FILTERABLE_METRICS = [
    "market_cap", "roce", "roe", "pat", "debt_to_equity", "current_ratio",
]
