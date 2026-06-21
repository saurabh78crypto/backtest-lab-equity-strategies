"""
Fetches annual + quarterly fundamental statements from Yahoo Finance (via
`yfinance`), derives a standard set of ratios, and upserts point-in-time rows
into `fundamentals`.

IMPORTANT - point-in-time correctness:
Yahoo Finance gives us the financial *period end* date (e.g. 2024-03-31 for
FY24), not the date the results were actually published. To avoid look-ahead
bias in the backtest engine we estimate `report_date` by adding a reporting
lag to the period end date (SEBI requires NSE-listed companies to publish
quarterly results within 45 days, and audited annual results within 60 days,
of period end) - see `settings.QUARTERLY_REPORT_LAG_DAYS` / `ANNUAL_REPORT_LAG_DAYS`.
This is a documented assumption, not exact filing-date data.

Run directly:
    python -m app.data_collection.fetch_fundamentals
"""
import logging
import time
from datetime import timedelta

import pandas as pd
import yfinance as yf
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.config import settings
from app.data_collection.universe import UNIVERSE
from app.data_collection.yf_utils import call_with_retry, is_rate_limit_error
from app.db.base import create_all_tables
from app.db.session import engine, session_scope
from app.models import Company, Fundamental, PeriodType

logger = logging.getLogger(__name__)

def _find_row(df: pd.DataFrame, candidates: list[str]) -> pd.Series | None:
    """yfinance row labels vary across versions; try several candidates (case-insensitive substring match)."""
    if df is None or df.empty:
        return None
    index_lower = {str(i).lower(): i for i in df.index}
    for cand in candidates:
        cand_l = cand.lower()
        for lower_label, original_label in index_lower.items():
            if cand_l == lower_label or cand_l in lower_label:
                return df.loc[original_label]
    return None

def _safe(series: pd.Series | None, col) -> float | None:
    if series is None or col not in series.index:
        return None
    val = series[col]
    if pd.isna(val):
        return None
    return float(val)

def _extract_period(
    income: pd.DataFrame, balance: pd.DataFrame, cashflow: pd.DataFrame, period_col, shares_fallback: float | None
) -> dict:
    revenue = _safe(_find_row(income, ["Total Revenue", "Operating Revenue"]), period_col)
    ebitda = _safe(_find_row(income, ["EBITDA", "Normalized EBITDA"]), period_col)
    ebit = _safe(_find_row(income, ["EBIT", "Operating Income"]), period_col)
    interest_expense = _safe(_find_row(income, ["Interest Expense"]), period_col)
    tax_expense = _safe(_find_row(income, ["Tax Provision", "Income Tax Expense"]), period_col)
    pat = _safe(_find_row(income, ["Net Income Common Stockholders", "Net Income"]), period_col)
    diluted_eps = _safe(_find_row(income, ["Diluted EPS", "Basic EPS"]), period_col)

    total_assets = _safe(_find_row(balance, ["Total Assets"]), period_col)
    total_equity = _safe(
        _find_row(balance, ["Stockholders Equity", "Total Equity Gross Minority Interest"]), period_col
    )
    total_debt = _safe(_find_row(balance, ["Total Debt"]), period_col)
    current_assets = _safe(_find_row(balance, ["Current Assets"]), period_col)
    current_liabilities = _safe(_find_row(balance, ["Current Liabilities"]), period_col)
    cash = _safe(
        _find_row(balance, ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"]),
        period_col,
    )
    shares_out = _safe(_find_row(balance, ["Ordinary Shares Number", "Share Issued"]), period_col)

    ocf = _safe(_find_row(cashflow, ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"]), period_col)
    icf = _safe(_find_row(cashflow, ["Investing Cash Flow", "Cash Flow From Continuing Investing Activities"]), period_col)
    fcf_financing = _safe(_find_row(cashflow, ["Financing Cash Flow", "Cash Flow From Continuing Financing Activities"]), period_col)
    capex = _safe(_find_row(cashflow, ["Capital Expenditure"]), period_col)

    # Derive shares outstanding for the period: prefer balance sheet figure,
    # else back into it from PAT / diluted EPS, else fall back to the
    # company's current shares outstanding.
    shares = shares_out
    if shares is None and pat is not None and diluted_eps not in (None, 0):
        shares = pat / diluted_eps
    if shares is None:
        shares = shares_fallback

    eps = diluted_eps if diluted_eps is not None else (pat / shares if (pat is not None and shares) else None)
    book_value_per_share = (total_equity / shares) if (total_equity is not None and shares) else None

    capital_employed = (
        (total_assets - current_liabilities)
        if (total_assets is not None and current_liabilities is not None)
        else None
    )
    roce = (ebit / capital_employed * 100) if (ebit is not None and capital_employed) else None
    roe = (pat / total_equity * 100) if (pat is not None and total_equity) else None
    roa = (pat / total_assets * 100) if (pat is not None and total_assets) else None
    debt_to_equity = (total_debt / total_equity) if (total_debt is not None and total_equity) else None
    current_ratio = (current_assets / current_liabilities) if (current_assets is not None and current_liabilities) else None
    operating_margin = (ebit / revenue * 100) if (ebit is not None and revenue) else None
    net_margin = (pat / revenue * 100) if (pat is not None and revenue) else None
    free_cash_flow = (ocf + capex) if (ocf is not None and capex is not None) else ocf

    return dict(
        revenue=revenue, ebitda=ebitda, ebit=ebit, interest_expense=interest_expense,
        tax_expense=tax_expense, pat=pat, total_assets=total_assets, total_equity=total_equity,
        total_debt=total_debt, current_assets=current_assets, current_liabilities=current_liabilities,
        cash_and_equivalents=cash, shares_outstanding=shares, operating_cash_flow=ocf,
        investing_cash_flow=icf, financing_cash_flow=fcf_financing, capex=capex, eps=eps,
        book_value_per_share=book_value_per_share, roe=roe, roce=roce, roa=roa,
        debt_to_equity=debt_to_equity, current_ratio=current_ratio, operating_margin=operating_margin,
        net_margin=net_margin, free_cash_flow=free_cash_flow,
    )

def _upsert_fundamental(db, company: Company, period_end, period_type: PeriodType, data: dict) -> None:
    lag = (
        settings.QUARTERLY_REPORT_LAG_DAYS
        if period_type == PeriodType.QUARTERLY
        else settings.ANNUAL_REPORT_LAG_DAYS
    )
    report_date = period_end + timedelta(days=lag)

    row = {
        "company_id": company.id,
        "period_end_date": period_end,
        "period_type": period_type,
        "report_date": report_date,
        **data,
    }
    stmt = pg_insert(Fundamental).values(**row)
    update_cols = {k: getattr(stmt.excluded, k) for k in data.keys()}
    update_cols["report_date"] = stmt.excluded.report_date
    stmt = stmt.on_conflict_do_update(
        constraint="uq_fundamentals_company_period", set_=update_cols
    )
    db.execute(stmt)

def fetch_company_fundamentals(db, company: Company) -> int:
    ticker = yf.Ticker(company.symbol)

    info = {}
    try:
        info = call_with_retry(lambda: ticker.get_info() or {}, description=f"{company.symbol} info")
    except Exception as exc:  # noqa: BLE001 - info is best-effort, used only as a shares-outstanding fallback
        logger.warning(
            "%s: couldn't fetch info (%s) - continuing without the shares-outstanding fallback", company.symbol, exc
        )
    shares_fallback = info.get("sharesOutstanding")
    time.sleep(0.3)  # `ticker.get_info()` is its own request; give Yahoo a beat before the statement calls below

    rows_written = 0
    for period_type, statement_attrs in (
        (PeriodType.ANNUAL, ("financials", "balance_sheet", "cashflow")),
        (PeriodType.QUARTERLY, ("quarterly_financials", "quarterly_balance_sheet", "quarterly_cashflow")),
    ):
        income, balance, cashflow = (
            call_with_retry(lambda attr=attr: getattr(ticker, attr), description=f"{company.symbol} {attr}")
            for attr in statement_attrs
        )
        if income is None or income.empty:
            continue
        for period_col in income.columns:
            period_end = pd.Timestamp(period_col).date()
            data = _extract_period(income, balance, cashflow, period_col, shares_fallback)
            # Skip totally empty periods (e.g. column exists but no usable data)
            if all(v is None for v in data.values()):
                continue
            _upsert_fundamental(db, company, period_end, period_type, data)
            rows_written += 1
        time.sleep(0.3)  # 3 more requests just happened (financials/balance/cashflow) - pace before the next batch
    return rows_written

def fetch_all_fundamentals(pause_sec: float | None = None) -> None:
    create_all_tables(engine)
    pause_sec = settings.YF_FUNDAMENTALS_PAUSE_SEC if pause_sec is None else pause_sec
    total = 0
    with session_scope() as db:
        companies = db.query(Company).filter(Company.is_benchmark.is_(False)).all()
        # Grab plain values now - `companies` becomes detached the moment
        # this `with` block exits (commit expires every attribute).
        company_refs = [(c.id, c.symbol) for c in companies]

    for i, (company_id, symbol) in enumerate(company_refs, start=1):
        try:
            with session_scope() as db:
                company = db.get(Company, company_id)  # fresh, attached instance
                n = fetch_company_fundamentals(db, company)
            total += n
            logger.info("[%d/%d] %s: upserted %d fundamental periods", i, len(company_refs), symbol, n)
        except Exception as exc:  # noqa: BLE001
            logger.error("[%d/%d] %s: FAILED (%s)", i, len(company_refs), symbol, exc)
            if is_rate_limit_error(exc):
                cooldown = pause_sec * 10
                logger.warning("Still rate-limited - cooling down %.1fs before the next ticker.", cooldown)
                time.sleep(cooldown)
                continue
        time.sleep(pause_sec)

    logger.info("Done. Total fundamental rows upserted: %d", total)

if __name__ == "__main__":
    from app.core.logging import setup_logging

    setup_logging()
    fetch_all_fundamentals()
