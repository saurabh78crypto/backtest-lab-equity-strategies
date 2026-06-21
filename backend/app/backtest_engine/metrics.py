"""
Standard performance-analytics functions operating on a daily equity curve
(pd.Series of portfolio value, indexed by date).
"""
import numpy as np
import pandas as pd

from app.core.config import settings

def daily_returns(equity_curve: pd.Series) -> pd.Series:
    return equity_curve.pct_change().dropna()

def total_return_pct(equity_curve: pd.Series) -> float:
    if len(equity_curve) < 2 or equity_curve.iloc[0] == 0:
        return 0.0
    return (equity_curve.iloc[-1] / equity_curve.iloc[0] - 1) * 100

def cagr_pct(equity_curve: pd.Series) -> float:
    if len(equity_curve) < 2 or equity_curve.iloc[0] <= 0:
        return 0.0
    n_days = (equity_curve.index[-1] - equity_curve.index[0]).days
    years = n_days / 365.25
    if years <= 0:
        return 0.0
    ratio = equity_curve.iloc[-1] / equity_curve.iloc[0]
    if ratio <= 0:
        return -100.0
    return (ratio ** (1 / years) - 1) * 100

def volatility_pct(returns: pd.Series, periods_per_year: int = None) -> float:
    periods_per_year = periods_per_year or settings.TRADING_DAYS_PER_YEAR
    if len(returns) < 2:
        return 0.0
    return float(returns.std(ddof=1) * np.sqrt(periods_per_year) * 100)

def sharpe_ratio(returns: pd.Series, risk_free_rate: float = None, periods_per_year: int = None) -> float:
    risk_free_rate = settings.RISK_FREE_RATE if risk_free_rate is None else risk_free_rate
    periods_per_year = periods_per_year or settings.TRADING_DAYS_PER_YEAR
    if len(returns) < 2 or returns.std(ddof=1) == 0:
        return 0.0
    daily_rf = risk_free_rate / periods_per_year
    excess = returns - daily_rf
    return float((excess.mean() / returns.std(ddof=1)) * np.sqrt(periods_per_year))

def sortino_ratio(returns: pd.Series, risk_free_rate: float = None, periods_per_year: int = None) -> float:
    risk_free_rate = settings.RISK_FREE_RATE if risk_free_rate is None else risk_free_rate
    periods_per_year = periods_per_year or settings.TRADING_DAYS_PER_YEAR
    if len(returns) < 2:
        return 0.0
    daily_rf = risk_free_rate / periods_per_year
    excess = returns - daily_rf
    downside = excess[excess < 0]
    downside_std = downside.std(ddof=1) if len(downside) > 1 else 0.0
    if not downside_std:
        return 0.0
    return float((excess.mean() / downside_std) * np.sqrt(periods_per_year))

def drawdown_series(equity_curve: pd.Series) -> pd.Series:
    running_max = equity_curve.cummax()
    return (equity_curve - running_max) / running_max * 100

def max_drawdown_pct(equity_curve: pd.Series) -> float:
    if equity_curve.empty:
        return 0.0
    return float(drawdown_series(equity_curve).min())

def calmar_ratio(cagr: float, max_dd: float) -> float | None:
    if max_dd == 0:
        return None
    return float(cagr / abs(max_dd))

def alpha_beta(portfolio_returns: pd.Series, benchmark_returns: pd.Series, periods_per_year: int = None) -> tuple[float | None, float | None]:
    periods_per_year = periods_per_year or settings.TRADING_DAYS_PER_YEAR
    aligned = pd.concat([portfolio_returns, benchmark_returns], axis=1, join="inner").dropna()
    if len(aligned) < 2:
        return None, None
    p, b = aligned.iloc[:, 0], aligned.iloc[:, 1]
    if b.var() == 0:
        return None, None
    beta = float(p.cov(b) / b.var())
    # Annualised alpha (Jensen's alpha) using mean daily excess return
    alpha_daily = p.mean() - beta * b.mean()
    alpha_annual_pct = float(alpha_daily * periods_per_year * 100)
    return alpha_annual_pct, beta

def win_rate_pct(period_returns: list[float]) -> float:
    if not period_returns:
        return 0.0
    wins = sum(1 for r in period_returns if r > 0)
    return wins / len(period_returns) * 100
