"""
Loads everything the backtest engine needs from the DB once per run
and exposes fast in-memory, point-in-time lookups on top of it.
"""
from datetime import date

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Company, Fundamental, StockPrice

def get_available_date_range(db: Session) -> tuple[date | None, date | None]:
    """safe start = date by which every active company has ≥1 fundamentals report.
       safe end = latest date with price data. Mirrors your check_db.py logic."""
    first_report_per_company = db.execute(
        select(Fundamental.company_id, func.min(Fundamental.report_date))
        .join(Company, Company.id == Fundamental.company_id)
        .where(Company.is_active.is_(True), Company.is_benchmark.is_(False))
        .group_by(Fundamental.company_id)
    ).all()
    if not first_report_per_company:
        return None, None
    safe_start_date = max(d for _, d in first_report_per_company)
    latest_price_date = db.scalar(
        select(func.max(StockPrice.date))
        .join(Company, Company.id == StockPrice.company_id)
        .where(Company.is_active.is_(True), Company.is_benchmark.is_(False))
    )
    return safe_start_date, latest_price_date

class MarketDataset:
    """
    In-memory snapshot of prices + fundamentals for a fixed set of companies,
    loaded once and reused across every rebalance of a single backtest run.
    """

    def __init__(self, price_panel: pd.DataFrame, fundamentals: pd.DataFrame, companies: pd.DataFrame):
        self.price_panel = price_panel        # index=date, columns=company_id -> adj_close
        self.fundamentals = fundamentals      # flat table, one row per (company_id, period)
        self.companies = companies            # indexed by company_id

    @property
    def trading_dates(self) -> pd.DatetimeIndex:
        return pd.DatetimeIndex(self.price_panel.index)

    def price_on_or_after(self, company_id, target_date: date) -> tuple[date, float] | None:
        col = self.price_panel.get(company_id)
        if col is None:
            return None
        col = col.dropna()
        idx = col.index[col.index >= pd.Timestamp(target_date)]
        if len(idx) == 0:
            return None
        d = idx[0]
        return d.date(), float(col.loc[d])

    def price_on_or_before(self, company_id, target_date: date) -> float | None:
        col = self.price_panel.get(company_id)
        if col is None:
            return None
        col = col.dropna()
        idx = col.index[col.index <= pd.Timestamp(target_date)]
        if len(idx) == 0:
            return None
        return float(col.loc[idx[-1]])

    def point_in_time_snapshot(self, as_of_date: date) -> pd.DataFrame:
        """
        Latest fundamentals row per company with report_date <= as_of_date.
        Returns a DataFrame indexed by company_id.
        """
        usable = self.fundamentals[self.fundamentals["report_date"] <= as_of_date]
        if usable.empty:
            return usable
        latest_idx = usable.groupby("company_id")["report_date"].idxmax()
        snapshot = usable.loc[latest_idx].set_index("company_id")
        return snapshot

    def market_caps_on(self, as_of_date: date, company_ids: list) -> pd.Series:
        """shares_outstanding (point-in-time) * price (as of date), in INR Crores assuming price in INR and shares in absolute units -> result scaled to Crores."""
        snapshot = self.point_in_time_snapshot(as_of_date)
        out = {}
        for cid in company_ids:
            if cid not in snapshot.index:
                continue
            shares = snapshot.loc[cid].get("shares_outstanding")
            price = self.price_on_or_before(cid, as_of_date)
            if shares is None or price is None or pd.isna(shares):
                continue
            # price in INR, shares absolute -> market cap in INR; convert to Crores (1 Cr = 1e7)
            out[cid] = (shares * price) / 1e7
        return pd.Series(out, dtype="float64")

def load_market_dataset(
    db: Session, start_date: date, end_date: date, include_benchmark: bool = True
) -> MarketDataset:
    companies_q = db.execute(select(Company).where(Company.is_active.is_(True))).scalars().all()
    companies_df = pd.DataFrame(
        [
            {
                "company_id": c.id,
                "symbol": c.symbol,
                "trading_symbol": c.trading_symbol,
                "name": c.name,
                "sector": c.sector,
                "is_benchmark": c.is_benchmark,
            }
            for c in companies_q
        ]
    ).set_index("company_id") if companies_q else pd.DataFrame()

    company_ids = [c.id for c in companies_q if include_benchmark or not c.is_benchmark]

    prices_q = db.execute(
        select(StockPrice.company_id, StockPrice.date, StockPrice.adj_close).where(
            StockPrice.company_id.in_([c.id for c in companies_q]),
            StockPrice.date >= start_date,
            StockPrice.date <= end_date,
        )
    ).all()
    prices_df = pd.DataFrame(prices_q, columns=["company_id", "date", "adj_close"])
    if prices_df.empty:
        price_panel = pd.DataFrame()
    else:
        prices_df["date"] = pd.to_datetime(prices_df["date"])
        price_panel = prices_df.pivot_table(index="date", columns="company_id", values="adj_close")
        price_panel = price_panel.sort_index().ffill()  # forward-fill small gaps (holidays etc.)

    fund_q = db.execute(
        select(Fundamental).where(
            Fundamental.company_id.in_([c.id for c in companies_q]),
            Fundamental.report_date <= end_date,
        )
    ).scalars().all()
    fund_rows = []
    for f in fund_q:
        fund_rows.append(
            {
                "company_id": f.company_id,
                "period_end_date": f.period_end_date,
                "period_type": f.period_type.value if hasattr(f.period_type, "value") else f.period_type,
                "report_date": f.report_date,
                "revenue": f.revenue, "ebitda": f.ebitda, "ebit": f.ebit,
                "interest_expense": f.interest_expense, "tax_expense": f.tax_expense, "pat": f.pat,
                "total_assets": f.total_assets, "total_equity": f.total_equity, "total_debt": f.total_debt,
                "current_assets": f.current_assets, "current_liabilities": f.current_liabilities,
                "cash_and_equivalents": f.cash_and_equivalents, "shares_outstanding": f.shares_outstanding,
                "operating_cash_flow": f.operating_cash_flow, "investing_cash_flow": f.investing_cash_flow,
                "financing_cash_flow": f.financing_cash_flow, "capex": f.capex, "eps": f.eps,
                "book_value_per_share": f.book_value_per_share, "roe": f.roe, "roce": f.roce, "roa": f.roa,
                "debt_to_equity": f.debt_to_equity, "current_ratio": f.current_ratio,
                "operating_margin": f.operating_margin, "net_margin": f.net_margin,
                "free_cash_flow": f.free_cash_flow,
            }
        )
    fundamentals_df = pd.DataFrame(fund_rows)

    return MarketDataset(price_panel=price_panel, fundamentals=fundamentals_df, companies=companies_df)
