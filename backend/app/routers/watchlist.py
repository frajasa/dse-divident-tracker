from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Company, Dividend, User, Watchlist, PriceAlert, NotificationLog
from sqlalchemy import desc

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


class AddWatchlistRequest(BaseModel):
    symbol: str
    notes: str | None = None


class CreatePriceAlertRequest(BaseModel):
    symbol: str
    alert_type: str  # above, below, yield_above
    target_value: float


class MarkNotificationRequest(BaseModel):
    notification_ids: list[int]


# ─── Watchlist ──────────────────────────────────────────────────


@router.get("/")
def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's watchlist with current data."""
    items = db.query(Watchlist).filter(Watchlist.user_id == current_user.id).all()
    result = []
    for w in items:
        company = w.company
        latest_div = (
            db.query(Dividend)
            .filter(Dividend.company_id == company.id)
            .order_by(desc(Dividend.financial_year))
            .first()
        )
        div_yield = Decimal("0")
        if latest_div and company.current_price and company.current_price > 0:
            div_yield = (latest_div.dividend_per_share / company.current_price * 100).quantize(Decimal("0.01"))

        result.append({
            "id": w.id,
            "symbol": company.symbol,
            "name": company.name,
            "sector": company.sector,
            "current_price": str(company.current_price) if company.current_price else None,
            "latest_dividend": str(latest_div.dividend_per_share) if latest_div else None,
            "dividend_yield": str(div_yield),
            "notes": w.notes,
            "added_at": w.added_at.isoformat() if w.added_at else None,
        })
    return result


@router.post("/")
def add_to_watchlist(
    req: AddWatchlistRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(Company.symbol == req.symbol.upper()).first()
    if not company:
        raise HTTPException(404, f"Company {req.symbol} not found")

    existing = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == current_user.id, Watchlist.company_id == company.id)
        .first()
    )
    if existing:
        raise HTTPException(400, f"{req.symbol} is already in your watchlist")

    item = Watchlist(
        user_id=current_user.id,
        company_id=company.id,
        notes=req.notes,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"message": "Added to watchlist", "id": item.id}


@router.delete("/{item_id}")
def remove_from_watchlist(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(Watchlist).filter(Watchlist.id == item_id).first()
    if not item:
        raise HTTPException(404, "Watchlist item not found")
    if item.user_id != current_user.id:
        raise HTTPException(403, "Not your watchlist item")
    db.delete(item)
    db.commit()
    return {"message": "Removed from watchlist"}


# ─── Price Alerts ───────────────────────────────────────────────


@router.get("/price-alerts")
def get_price_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alerts = (
        db.query(PriceAlert)
        .filter(PriceAlert.user_id == current_user.id)
        .order_by(desc(PriceAlert.created_at))
        .all()
    )
    return [
        {
            "id": a.id,
            "symbol": a.company.symbol,
            "company_name": a.company.name,
            "alert_type": a.alert_type,
            "target_value": str(a.target_value),
            "is_active": a.is_active,
            "is_triggered": a.is_triggered,
            "triggered_at": a.triggered_at.isoformat() if a.triggered_at else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in alerts
    ]


@router.post("/price-alerts")
def create_price_alert(
    req: CreatePriceAlertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    valid_types = {"above", "below", "yield_above"}
    if req.alert_type not in valid_types:
        raise HTTPException(400, f"alert_type must be one of {valid_types}")

    company = db.query(Company).filter(Company.symbol == req.symbol.upper()).first()
    if not company:
        raise HTTPException(404, f"Company {req.symbol} not found")

    alert = PriceAlert(
        user_id=current_user.id,
        company_id=company.id,
        alert_type=req.alert_type,
        target_value=req.target_value,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return {"message": "Price alert created", "id": alert.id}


@router.delete("/price-alerts/{alert_id}")
def delete_price_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(404, "Price alert not found")
    if alert.user_id != current_user.id:
        raise HTTPException(403, "Not your alert")
    db.delete(alert)
    db.commit()
    return {"message": "Price alert deleted"}


# ─── Notifications ──────────────────────────────────────────────


@router.get("/notifications")
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    unread_only: bool = False,
):
    query = db.query(NotificationLog).filter(NotificationLog.user_id == current_user.id)
    if unread_only:
        query = query.filter(NotificationLog.is_read == False)
    notifications = query.order_by(desc(NotificationLog.created_at)).limit(50).all()
    return [
        {
            "id": n.id,
            "type": n.notification_type,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notifications
    ]


@router.post("/notifications/mark-read")
def mark_notifications_read(
    req: MarkNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(NotificationLog).filter(
        NotificationLog.id.in_(req.notification_ids),
        NotificationLog.user_id == current_user.id,
    ).update({"is_read": True}, synchronize_session=False)
    db.commit()
    return {"message": "Notifications marked as read"}
