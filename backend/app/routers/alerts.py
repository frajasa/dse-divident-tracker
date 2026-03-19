from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.database import get_db
from app.dependencies import get_current_user
from app.models import AlertPreference, Company, Dividend, User

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


class CreateAlertRequest(BaseModel):
    alert_type: str  # pre_closure, declared, payment, yield_opportunity
    channel: str = "whatsapp"  # sms, whatsapp, email
    days_before: int = 7
    company_symbol: str | None = None


class UpdateAlertRequest(BaseModel):
    channel: str | None = None
    days_before: int | None = None
    is_active: bool | None = None


def _alert_to_dict(alert: AlertPreference) -> dict:
    return {
        "id": alert.id,
        "alert_type": alert.alert_type,
        "channel": alert.channel,
        "days_before": alert.days_before,
        "company_symbol": alert.company.symbol if alert.company_id and alert.company else None,
        "is_active": alert.is_active,
    }


@router.get("/preferences")
def list_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prefs = (
        db.query(AlertPreference)
        .filter(AlertPreference.user_id == current_user.id)
        .all()
    )
    return [_alert_to_dict(p) for p in prefs]


@router.post("/preferences")
def create_preference(
    req: CreateAlertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    valid_types = {"pre_closure", "declared", "payment", "yield_opportunity"}
    if req.alert_type not in valid_types:
        raise HTTPException(400, f"alert_type must be one of {valid_types}")

    company_id = None
    if req.company_symbol:
        company = db.query(Company).filter(Company.symbol == req.company_symbol.upper()).first()
        if not company:
            raise HTTPException(404, f"Company {req.company_symbol} not found")
        company_id = company.id

    pref = AlertPreference(
        user_id=current_user.id,
        alert_type=req.alert_type,
        channel=req.channel,
        days_before=req.days_before,
        company_id=company_id,
        is_active=True,
    )
    db.add(pref)
    db.commit()
    db.refresh(pref)
    return _alert_to_dict(pref)


@router.put("/preferences/{pref_id}")
def update_preference(
    pref_id: int,
    req: UpdateAlertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pref = db.query(AlertPreference).filter(AlertPreference.id == pref_id).first()
    if not pref:
        raise HTTPException(404, "Alert preference not found")
    if pref.user_id != current_user.id:
        raise HTTPException(403, "Not your alert preference")

    if req.channel is not None:
        pref.channel = req.channel
    if req.days_before is not None:
        pref.days_before = req.days_before
    if req.is_active is not None:
        pref.is_active = req.is_active

    db.commit()
    db.refresh(pref)
    return _alert_to_dict(pref)


@router.delete("/preferences/{pref_id}")
def delete_preference(
    pref_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pref = db.query(AlertPreference).filter(AlertPreference.id == pref_id).first()
    if not pref:
        raise HTTPException(404, "Alert preference not found")
    if pref.user_id != current_user.id:
        raise HTTPException(403, "Not your alert preference")

    db.delete(pref)
    db.commit()
    return {"message": "Alert preference deleted"}


@router.get("/upcoming")
def upcoming_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cross-reference user's alert preferences with upcoming dividends."""
    prefs = (
        db.query(AlertPreference)
        .filter(AlertPreference.user_id == current_user.id, AlertPreference.is_active == True)
        .all()
    )

    if not prefs:
        return []

    today = date.today()
    max_days = max(p.days_before for p in prefs)
    cutoff = today + timedelta(days=max_days)

    upcoming_divs = (
        db.query(Dividend).join(Company)
        .filter(Dividend.books_closure_date >= today, Dividend.books_closure_date <= cutoff)
        .all()
    )

    alerts = []
    for div in upcoming_divs:
        days_until = (div.books_closure_date - today).days
        for pref in prefs:
            if pref.alert_type != "pre_closure":
                continue
            if pref.company_id and pref.company_id != div.company_id:
                continue
            if days_until <= pref.days_before:
                alerts.append({
                    "symbol": div.company.symbol,
                    "company_name": div.company.name,
                    "dividend_per_share": str(div.dividend_per_share),
                    "books_closure_date": div.books_closure_date.isoformat(),
                    "days_until": days_until,
                    "alert_type": pref.alert_type,
                    "channel": pref.channel,
                })

    alerts.sort(key=lambda x: x["days_until"])
    return alerts
