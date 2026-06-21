"""
Generates rebalance dates for a given frequency, then snaps each one to the
next available trading day found in the price data (so we never try to
trade on a date with no price - weekends/holidays/listing gaps).
"""
from datetime import date

import pandas as pd
from dateutil.relativedelta import relativedelta

from app.schemas.enums import RebalanceFrequency

_FREQ_MONTHS = {
    RebalanceFrequency.MONTHLY: 1,
    RebalanceFrequency.QUARTERLY: 3,
    RebalanceFrequency.HALF_YEARLY: 6,
    RebalanceFrequency.YEARLY: 12,
}

def generate_calendar_rebalance_dates(
    start_date: date, end_date: date, frequency: RebalanceFrequency
) -> list[date]:
    """Raw calendar dates (e.g. 1st of every quarter from start_date), before trading-day snapping."""
    step = _FREQ_MONTHS[frequency]
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current = current + relativedelta(months=step)
    return dates

def snap_to_trading_days(target_dates: list[date], trading_dates: pd.DatetimeIndex) -> list[date]:
    """
    For each target date, return the next available trading date on/after it.
    Dates beyond the available trading calendar are dropped.
    """
    if len(trading_dates) == 0:
        return []
    trading_dates = pd.DatetimeIndex(sorted(trading_dates))
    snapped = []
    for d in target_dates:
        ts = pd.Timestamp(d)
        pos = trading_dates.searchsorted(ts, side="left")
        if pos >= len(trading_dates):
            continue 
        snapped.append(trading_dates[pos].date())
    # de-duplicate while preserving order
    seen = set()
    out = []
    for d in snapped:
        if d not in seen:
            seen.add(d)
            out.append(d)
    return out

def build_rebalance_dates(
    start_date: date, end_date: date, frequency: RebalanceFrequency, trading_dates: pd.DatetimeIndex
) -> list[date]:
    calendar_dates = generate_calendar_rebalance_dates(start_date, end_date, frequency)
    return snap_to_trading_days(calendar_dates, trading_dates)
