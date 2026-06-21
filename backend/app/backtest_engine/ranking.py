"""
Ranking system. Supports:
- Single-metric ranking (e.g. ROE descending)
- Composite ranking: average the per-metric ranks (optionally weighted) into
  one composite rank, then sort ascending (rank 1 = best).
"""
import pandas as pd

from app.schemas.backtest import RankingConfig
from app.schemas.enums import RankingOrder

def rank_companies(metrics_df: pd.DataFrame, ranking: RankingConfig) -> pd.DataFrame:
    """
    `metrics_df`: indexed by company_id, with one column per metric referenced
    in `ranking.metrics`.
    Returns a copy of metrics_df with per-metric rank columns, a
    `composite_rank` column, sorted best-first (lowest composite_rank first).
    Companies missing a required metric are pushed to the worst rank for that
    metric (so they still get ranked, but never win on missing data).
    """
    df = metrics_df.copy()
    if df.empty:
        df["composite_rank"] = pd.Series(dtype="float64")
        return df

    rank_cols = []
    total_weight = sum(m.weight for m in ranking.metrics)

    for m in ranking.metrics:
        if m.metric not in df.columns:
            raise ValueError(f"Ranking metric '{m.metric}' not available in computed metrics")
        ascending = m.order == RankingOrder.ASCENDING
        col_name = f"_rank_{m.metric}"
        df[col_name] = df[m.metric].rank(method="average", ascending=ascending, na_option="bottom")
        rank_cols.append((col_name, m.weight))

    df["composite_rank"] = sum(df[c] * w for c, w in rank_cols) / total_weight
    df = df.sort_values("composite_rank", ascending=True)
    return df
