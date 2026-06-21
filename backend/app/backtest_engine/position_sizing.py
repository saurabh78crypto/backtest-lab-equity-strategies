"""
Position sizing: turns a selected list of company_ids into portfolio weights
that sum to 1.0.
"""
import logging

import pandas as pd

from app.schemas.enums import PositionSizingMethod

logger = logging.getLogger(__name__)

def compute_weights(
    selected_df: pd.DataFrame,
    method: PositionSizingMethod,
    metric_col: str | None = None,
) -> pd.Series:
    """
    `selected_df`: indexed by company_id, already filtered down to the chosen
    portfolio (top N). Must contain a `market_cap` column if method is
    market_cap_weighted, and `metric_col` if metric_weighted.
    Returns a Series of weights (company_id -> weight), summing to 1.0.
    """
    n = len(selected_df)
    if n == 0:
        return pd.Series(dtype="float64")

    if method == PositionSizingMethod.EQUAL_WEIGHTED:
        return pd.Series(1.0 / n, index=selected_df.index)

    if method == PositionSizingMethod.MARKET_CAP_WEIGHTED:
        values = selected_df["market_cap"].clip(lower=0).fillna(0)
        return _normalize_or_fallback_equal(values, n)

    if method == PositionSizingMethod.METRIC_WEIGHTED:
        if metric_col is None or metric_col not in selected_df.columns:
            raise ValueError("metric_weighted sizing requires a valid metric_col")
        # Long-only weighting requires non-negative weights; negative metric
        # values (e.g. a negative ROCE that slipped past filters) are clipped
        # to zero and a warning is logged rather than producing a short position.
        raw = selected_df[metric_col]
        if (raw < 0).any():
            logger.warning(
                "metric_weighted sizing: %d of %d holdings have a negative '%s' "
                "value - clipped to 0 for weighting purposes",
                int((raw < 0).sum()), n, metric_col,
            )
        values = raw.clip(lower=0).fillna(0)
        return _normalize_or_fallback_equal(values, n)

    raise ValueError(f"Unknown position sizing method: {method}")

def _normalize_or_fallback_equal(values: pd.Series, n: int) -> pd.Series:
    total = values.sum()
    if total <= 0:
        logger.warning("Sizing weights summed to <= 0; falling back to equal-weighting for this rebalance.")
        return pd.Series(1.0 / n, index=values.index)
    return values / total
