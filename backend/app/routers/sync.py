from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sync_log import SyncLog
from app.services.sync_service import sync_dividends, sync_prices, update_dividend_statuses
from app.scheduler import scheduler

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("/dividends")
def trigger_dividend_sync(db: Session = Depends(get_db)):
    """Manually trigger a dividend sync."""
    log = sync_dividends(db, triggered_by="manual")
    return _log_to_dict(log)


@router.post("/prices")
def trigger_price_sync(db: Session = Depends(get_db)):
    """Manually trigger a price sync."""
    log = sync_prices(db, triggered_by="manual")
    return _log_to_dict(log)


@router.post("/status-update")
def trigger_status_update(db: Session = Depends(get_db)):
    """Manually trigger dividend status transitions."""
    log = update_dividend_statuses(db, triggered_by="manual")
    return _log_to_dict(log)


@router.get("/logs")
def get_sync_logs(
    sync_type: str | None = Query(None, description="Filter by sync type"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """View recent sync logs, optionally filtered by type."""
    query = db.query(SyncLog).order_by(SyncLog.started_at.desc())
    if sync_type:
        query = query.filter(SyncLog.sync_type == sync_type)
    logs = query.limit(limit).all()
    return [_log_to_dict(log) for log in logs]


@router.get("/status")
def get_sync_status(db: Session = Depends(get_db)):
    """Show last sync time per type and next scheduled runs."""
    sync_types = ["dividends", "prices", "status_update"]
    last_syncs = {}

    for st in sync_types:
        last = (
            db.query(SyncLog)
            .filter(SyncLog.sync_type == st)
            .order_by(SyncLog.started_at.desc())
            .first()
        )
        last_syncs[st] = _log_to_dict(last) if last else None

    # Get next scheduled run times
    next_runs = {}
    for job in scheduler.get_jobs():
        next_run = job.next_run_time
        next_runs[job.id] = next_run.isoformat() if next_run else None

    return {
        "last_syncs": last_syncs,
        "next_scheduled_runs": next_runs,
    }


def _log_to_dict(log: SyncLog) -> dict:
    return {
        "id": log.id,
        "sync_type": log.sync_type,
        "status": log.status,
        "records_found": log.records_found,
        "records_created": log.records_created,
        "records_updated": log.records_updated,
        "records_skipped": log.records_skipped,
        "error_message": log.error_message,
        "started_at": log.started_at.isoformat() if log.started_at else None,
        "completed_at": log.completed_at.isoformat() if log.completed_at else None,
        "triggered_by": log.triggered_by,
    }
