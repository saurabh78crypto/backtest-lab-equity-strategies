import logging
import random
import time
from yfinance.exceptions import YFRateLimitError
from typing import Callable, TypeVar

from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Substrings seen in yfinance/urllib3/requests errors when Yahoo throttles.
_RATE_LIMIT_MARKERS = (
    "429",
    "too many requests",
    "rate limit",
    "rate-limited",
)

def is_rate_limit_error(exc: BaseException) -> bool:
    if isinstance(exc, YFRateLimitError):
        return True
    msg = str(exc).lower()
    return any(marker in msg for marker in _RATE_LIMIT_MARKERS)

def call_with_retry(
    func: Callable[[], T],
    *,
    description: str,
    max_retries: int = settings.YF_RATE_LIMIT_MAX_RETRIES,
    base_delay: float = settings.YF_RATE_LIMIT_BASE_DELAY_SEC,
) -> T:
    """
    Calls `func()`, retrying with exponential backoff + jitter if the
    failure looks like a Yahoo Finance rate limit (HTTP 429).

    Non-rate-limit exceptions are raised immediately on the first failure -
    the per-ticker try/except in fetch_prices.py / fetch_fundamentals.py
    already handles those by logging and moving on.

    Rate-limit-shaped failures are retried up to `max_retries` times before
    being raised, so the caller's existing "skip this ticker" handling still
    applies as a last resort.
    """
    attempt = 0
    while True:
        try:
            return func()
        except Exception as exc:  # noqa: BLE001 - re-raised below if not retryable
            if not is_rate_limit_error(exc) or attempt >= max_retries:
                raise
            delay = base_delay * (2**attempt) + random.uniform(0, base_delay / 2)
            attempt += 1
            logger.warning(
                "%s: rate-limited by Yahoo Finance (attempt %d/%d). Backing off %.1fs...",
                description,
                attempt,
                max_retries,
                delay,
            )
            time.sleep(delay)
