import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.database import SessionLocal
from app.services.sync_service import sync_dividends, sync_prices, update_dividend_statuses

logger = logging.getLogger("dse.scheduler")

scheduler = BackgroundScheduler()


def _run_sync(sync_func, sync_name: str):
    """Wrapper that creates a DB session, runs a sync function, and handles errors."""
    logger.info("Scheduler running: %s", sync_name)
    db = SessionLocal()
    try:
        sync_func(db, triggered_by="scheduler")
    except Exception:
        logger.exception("Scheduled %s failed", sync_name)
    finally:
        db.close()


def setup_scheduler():
    """Configure and start the APScheduler with cron jobs for DSE data sync."""

    if settings.sync_prices_enabled:
        # Price sync: daily weekdays at 17:00 EAT (14:00 UTC)
        scheduler.add_job(
            _run_sync,
            trigger=CronTrigger(day_of_week="mon-fri", hour=14, minute=0),  # 17:00 EAT = 14:00 UTC
            args=[sync_prices, "price_sync"],
            id="price_sync",
            name="Daily price sync",
            replace_existing=True,
        )
        logger.info("Added job: price_sync (weekdays 17:00 EAT)")

    if settings.sync_dividends_enabled:
        # Dividend sync: Monday & Thursday at 09:00 EAT (06:00 UTC)
        scheduler.add_job(
            _run_sync,
            trigger=CronTrigger(day_of_week="mon,thu", hour=6, minute=0),  # 09:00 EAT = 06:00 UTC
            args=[sync_dividends, "dividend_sync"],
            id="dividend_sync",
            name="Dividend sync (Mon & Thu)",
            replace_existing=True,
        )
        logger.info("Added job: dividend_sync (Mon & Thu 09:00 EAT)")

    # Status update: daily at 00:30 EAT (21:30 UTC previous day)
    scheduler.add_job(
        _run_sync,
        trigger=CronTrigger(hour=21, minute=30),  # 00:30 EAT = 21:30 UTC
        args=[update_dividend_statuses, "status_update"],
        id="status_update",
        name="Daily status update",
        replace_existing=True,
    )
    logger.info("Added job: status_update (daily 00:30 EAT)")

    scheduler.start()
    logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))


def shutdown_scheduler():
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")
