from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Backtesting Framework API"
    API_V1_PREFIX: str = "/api/v1"
    ENV: str = "development"
    DEBUG: bool = True

    #  Database (Supabase / PostgreSQL)
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/backtesting"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    #  CORS 
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    #  Data collection 
    # NSE tickers on Yahoo Finance carry a ".NS" suffix
    YF_SUFFIX: str = ".NS"
    BENCHMARK_SYMBOL: str = "^NSEI"  # Nifty 50 index on Yahoo Finance
    BENCHMARK_NAME: str = "NIFTY 50"
    PRICE_HISTORY_START: str = "2014-01-01"
    # Assumed reporting lag (days) between a financial period end and the date
    # the results are actually public, used to build a point-in-time dataset
    # and avoid look-ahead bias. SEBI mandates NSE-listed companies to file
    # quarterly results within 45 days and annual (audited) results within
    # 60 days of period end - we use a slightly conservative default.
    QUARTERLY_REPORT_LAG_DAYS: int = 45
    ANNUAL_REPORT_LAG_DAYS: int = 60

    #  Data collection: Yahoo Finance pacing / rate-limit handling 
    YF_REQUEST_PAUSE_SEC: float = 1.5  # baseline pause between tickers (prices)
    YF_FUNDAMENTALS_PAUSE_SEC: float = 2.5  # fundamentals issue ~7 requests/ticker, so pace slower
    YF_RATE_LIMIT_MAX_RETRIES: int = 5
    YF_RATE_LIMIT_BASE_DELAY_SEC: float = 10.0  # first backoff sleep; doubles each retry + jitter

    #  Backtest engine defaults 
    RISK_FREE_RATE: float = 0.065  # ~ Indian 10Y G-Sec, used for Sharpe/Sortino
    TRADING_DAYS_PER_YEAR: int = 252

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
