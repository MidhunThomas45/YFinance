# jobs/fetch_jobs.py
from apscheduler.schedulers.background import BackgroundScheduler
from services.stock_service import fetch_historical_ohlcv
from services.storage_service import upsert_ohlcv_from_df
import logging

logger = logging.getLogger(__name__)

def job_fetch_and_store(symbols: list, period: str = "5d", interval: str = "1h"):
    """
    Fetch recent data for a list of symbols and store in DB.
    Use smaller period/interval for frequent jobs.
    """
    for s in symbols:
        try:
            df = fetch_historical_ohlcv(s, period=period, interval=interval)
            if not df.empty:
                upsert_ohlcv_from_df(df)
                logger.info(f"Inserted {len(df)} rows for {s}")
            else:
                logger.warning(f"No data fetched for {s}")
        except Exception as e:
            logger.exception(f"Error fetching/storing {s}: {e}")

def start_scheduler(symbols: list, cron_expr: dict = None):
    """
    Start background scheduler to run daily at a chosen time.
    cron_expr example: {"hour": 1, "minute": 0} for 01:00 daily
    """
    scheduler = BackgroundScheduler()
    # default: run once per day at 01:00
    schedule = cron_expr or {"hour": 1, "minute": 0}
    scheduler.add_job(job_fetch_and_store, "cron", args=[symbols], **schedule)
    scheduler.start()
    return scheduler
