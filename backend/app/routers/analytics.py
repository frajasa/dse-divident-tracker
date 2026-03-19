from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
def market_overview(db: Session = Depends(get_db)):
    return analytics_service.compute_market_overview(db)


@router.get("/sectors")
def sector_analysis(db: Session = Depends(get_db)):
    return analytics_service.compute_sector_analysis(db)


@router.get("/top-payers")
def top_payers(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    return analytics_service.compute_top_payers(db, limit=limit)


@router.get("/yield-trends")
def yield_trends(db: Session = Depends(get_db)):
    return analytics_service.compute_yield_trends(db)


@router.get("/growth-leaders")
def growth_leaders(db: Session = Depends(get_db)):
    return analytics_service.compute_growth_leaders(db)


@router.get("/aristocrats")
def dividend_aristocrats(db: Session = Depends(get_db)):
    """Companies with consecutive years of dividend increases."""
    return analytics_service.compute_dividend_aristocrats(db)


@router.get("/movers")
def market_movers(db: Session = Depends(get_db)):
    """Biggest dividend increases and decreases."""
    return analytics_service.compute_market_movers(db)


@router.get("/risk-metrics")
def risk_metrics(db: Session = Depends(get_db)):
    """Risk scoring based on dividend consistency, growth, and yield."""
    return analytics_service.compute_risk_metrics(db)
