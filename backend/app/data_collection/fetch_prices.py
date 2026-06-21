"""
Fetches daily OHLCV history from Yahoo Finance (via `yfinance`) for the full
universe + the Nifty 50 benchmark, and upserts it into `stock_prices`.

Run directly:
    python -m app.data_collection.fetch_prices
"""
import logging
import time
from datetime import datetime

import pandas as pd
import yfinance as yf
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.config import settings
from app.data_collection.universe import BENCHMARK_ENTRY, UNIVERSE
from app.data_collection.yf_utils import call_with_retry, is_rate_limit_error
from app.db.base import create_all_tables
from app.db.session import engine, session_scope
from app.models import Company, Exchange, StockPrice

logger = logging.getLogger(__name__)

def _get_or_create_company(db, entry: dict, is_benchmark: bool = False) -> Company:
    yf_symbol = (
        settings.BENCHMARK_SYMBOL
        if is_benchmark
        else f"{entry['trading_symbol']}{settings.YF_SUFFIX}"
    )
    company = db.query(Company).filter(Company.symbol == yf_symbol).one_or_none()
    if company is None:
        company = Company(
            symbol=yf_symbol,
            trading_symbol=entry["trading_symbol"],
            name=entry["name"],
            sector=entry["sector"],
            exchange=Exchange.NSE,
            is_benchmark=is_benchmark,
        )
        db.add(company)
        db.flush()
    return company

def _upsert_prices(db, company: Company, df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    df = df.reset_index()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).lower().replace(" ", "_") for c in df.columns]

    if "adj_close" not in df.columns:
        df["adj_close"] = df["close"]

    rows = []
    for _, r in df.iterrows():
        if pd.isna(r.get("close")):
            continue
        rows.append(
            {
                "company_id": company.id,
                "date": pd.Timestamp(r["date"]).date(),
                "open": float(r["open"]),
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
                "adj_close": float(r["adj_close"]),
                "volume": int(r["volume"]) if not pd.isna(r.get("volume")) else 0,
            }
        )

    if not rows:
        return 0

    stmt = pg_insert(StockPrice).values(rows)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_stock_prices_company_date",
        set_={
            "open": stmt.excluded.open,
            "high": stmt.excluded.high,
            "low": stmt.excluded.low,
            "close": stmt.excluded.close,
            "adj_close": stmt.excluded.adj_close,
            "volume": stmt.excluded.volume,
        },
    )
    db.execute(stmt)
    return len(rows)

def fetch_all_prices(start: str | None = None, end: str | None = None, pause_sec: float | None = None) -> None:
    create_all_tables(engine)
    start = start or settings.PRICE_HISTORY_START
    end = end or datetime.today().strftime("%Y-%m-%d")
    pause_sec = settings.YF_REQUEST_PAUSE_SEC if pause_sec is None else pause_sec

    total_rows = 0
    with session_scope() as db:
        # 1. Benchmark first
        bench_company = _get_or_create_company(db, BENCHMARK_ENTRY, is_benchmark=True)
        db.commit()

    logger.info("Fetching benchmark %s ...", settings.BENCHMARK_SYMBOL)
    bench_df = call_with_retry(
        lambda: yf.download(
            settings.BENCHMARK_SYMBOL, start=start, end=end,
            auto_adjust=False, progress=False, multi_level_index=False,
        ),
        description=f"benchmark {settings.BENCHMARK_SYMBOL}",
    )
    with session_scope() as db:
        bench_company = db.query(Company).filter(Company.is_benchmark.is_(True)).one()
        n = _upsert_prices(db, bench_company, bench_df)
        total_rows += n
        logger.info("Benchmark: upserted %d rows", n)
    time.sleep(pause_sec)

    # 2. Universe
    for i, entry in enumerate(UNIVERSE, start=1):
        ticker = f"{entry['trading_symbol']}{settings.YF_SUFFIX}"
        try:
            df = call_with_retry(
                lambda: yf.download(
                    ticker, start=start, end=end,
                    auto_adjust=False, progress=False, multi_level_index=False,
                ),
                description=f"[{i}/{len(UNIVERSE)}] {ticker}",
            )
            with session_scope() as db:
                company = _get_or_create_company(db, entry)
                n = _upsert_prices(db, company, df)
                total_rows += n
            logger.info("[%d/%d] %s: upserted %d rows", i, len(UNIVERSE), ticker, n)
        except Exception as exc:  # noqa: BLE001 - keep pipeline running on single-ticker failure
            logger.error("[%d/%d] %s: FAILED (%s)", i, len(UNIVERSE), ticker, exc)
            if is_rate_limit_error(exc):
                cooldown = pause_sec * 10
                logger.warning("Still rate-limited - cooling down %.1fs before the next ticker.", cooldown)
                time.sleep(cooldown)
                continue
        time.sleep(pause_sec)

    logger.info("Done. Total price rows upserted: %d", total_rows)

if __name__ == "__main__":
    from app.core.logging import setup_logging

    setup_logging()
    fetch_all_prices()
