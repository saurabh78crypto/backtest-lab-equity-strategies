"""
Filtering system. Per the spec, filters are evaluated ONCE using point-in-time
data as of the backtest start date, and the resulting eligible universe is
then reused, unchanged, for every rebalance (only the *ranking metric values*
are refreshed at each rebalance - membership in the universe is not).
"""
import pandas as pd

from app.schemas.backtest import FilterConfig

def apply_filters(snapshot: pd.DataFrame, market_caps: pd.Series, filters: FilterConfig) -> list:
    """
    `snapshot`: point-in-time fundamentals indexed by company_id (output of
                MarketDataset.point_in_time_snapshot).
    `market_caps`: company_id -> market cap in INR Crores, as of the same date.
    Returns the list of company_ids that pass every configured filter.
    """
    if snapshot.empty:
        return []

    df = snapshot.copy()
    df["market_cap"] = market_caps

    mask = pd.Series(True, index=df.index)

    if filters.market_cap_min_cr is not None:
        mask &= df["market_cap"] >= filters.market_cap_min_cr
    if filters.market_cap_max_cr is not None:
        mask &= df["market_cap"] <= filters.market_cap_max_cr
    if filters.roce_min_pct is not None:
        mask &= df["roce"] > filters.roce_min_pct
    if filters.roe_min_pct is not None:
        mask &= df["roe"] > filters.roe_min_pct
    if filters.pat_positive:
        mask &= df["pat"] > 0
    if filters.debt_to_equity_max is not None:
        mask &= df["debt_to_equity"] <= filters.debt_to_equity_max

    # Drop rows where a required column is missing data. 
    # Market_cap with no price/shares data is dropped explicitly 
    # since it's needed regardless of which filters are active.
    mask &= df["market_cap"].notna()

    return df.index[mask].tolist()
