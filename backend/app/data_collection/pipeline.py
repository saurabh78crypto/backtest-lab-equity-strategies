"""
Single entrypoint that runs the full data collection pipeline:
  1. Create/refresh company master rows + price history
  2. Fetch fundamentals + compute ratios

Run:
    python -m app.data_collection.pipeline
"""
import logging

from app.core.logging import setup_logging
from app.data_collection.fetch_fundamentals import fetch_all_fundamentals
from app.data_collection.fetch_prices import fetch_all_prices

logger = logging.getLogger(__name__)

def run_pipeline() -> None:
    logger.info("=== STEP 1/2: Fetching price history (OHLCV) ===")
    fetch_all_prices()

    logger.info("=== STEP 2/2: Fetching fundamentals & computing ratios ===")
    fetch_all_fundamentals()

    logger.info("Pipeline complete.")

if __name__ == "__main__":
    setup_logging()
    run_pipeline()
