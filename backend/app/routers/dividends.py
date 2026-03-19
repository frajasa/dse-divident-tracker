from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import dividend_service

router = APIRouter(prefix="/api/dividends", tags=["dividends"])


@router.get("")
def list_dividends(year: str | None = None, db: Session = Depends(get_db)):
    """List all dividend announcements, optionally filtered by year."""
    return dividend_service.get_all_dividends(db, year=year)


@router.get("/upcoming")
def upcoming_dividends(
    days: int = Query(60, ge=1, le=365), db: Session = Depends(get_db)
):
    """Dividends with books closing in the next N days."""
    return dividend_service.get_upcoming_dividends(db, days_ahead=days)


@router.get("/yields")
def dividend_yields(db: Session = Depends(get_db)):
    """Current dividend yield for all DSE companies."""
    return dividend_service.get_dividend_yields(db)


@router.get("/history/{symbol}")
def company_dividend_history(symbol: str, db: Session = Depends(get_db)):
    """Full dividend history for a specific company."""
    return dividend_service.get_dividend_history(db, symbol)


@router.get("/alerts")
def check_alerts(
    days: int = Query(7, ge=1, le=30), db: Session = Depends(get_db)
):
    """Check for upcoming book closure alerts."""
    return dividend_service.get_alerts_due(db, days_before=days)
