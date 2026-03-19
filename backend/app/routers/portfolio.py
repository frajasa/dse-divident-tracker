from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Company, Dividend, User, UserHolding
from app.services import dividend_service

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


class AddHoldingRequest(BaseModel):
    symbol: str
    shares: int
    purchase_price: float | None = None
    purchase_date: str | None = None


class UpdateHoldingRequest(BaseModel):
    shares: int | None = None
    purchase_price: float | None = None


@router.get("")
def get_portfolio(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all holdings for the authenticated user."""
    holdings = db.query(UserHolding).filter(UserHolding.user_id == current_user.id).all()
    return [
        {
            "id": h.id,
            "symbol": h.company.symbol,
            "company_name": h.company.name,
            "sector": h.company.sector,
            "shares": h.shares_held,
            "purchase_price": str(h.purchase_price) if h.purchase_price else None,
            "current_price": str(h.company.current_price) if h.company.current_price else None,
        }
        for h in holdings
    ]


@router.post("/add")
def add_holding(
    req: AddHoldingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a stock holding to the authenticated user's portfolio."""
    company = db.query(Company).filter(Company.symbol == req.symbol.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {req.symbol} not found")

    holding = UserHolding(
        user_id=current_user.id,
        company_id=company.id,
        shares_held=req.shares,
        purchase_price=req.purchase_price,
    )
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return {"message": "Holding added", "id": holding.id}


@router.put("/{holding_id}")
def update_holding(
    holding_id: int,
    req: UpdateHoldingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update shares or purchase price on an existing holding."""
    holding = db.query(UserHolding).filter(UserHolding.id == holding_id).first()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    if holding.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your holding")

    if req.shares is not None:
        holding.shares_held = req.shares
    if req.purchase_price is not None:
        holding.purchase_price = req.purchase_price

    db.commit()
    db.refresh(holding)
    return {"message": "Holding updated"}


@router.delete("/{holding_id}")
def remove_holding(
    holding_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a holding — only if it belongs to the authenticated user."""
    holding = db.query(UserHolding).filter(UserHolding.id == holding_id).first()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    if holding.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your holding")
    db.delete(holding)
    db.commit()
    return {"message": "Holding removed"}


@router.get("/projections")
def project_dividends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Project annual dividend income for the authenticated user's portfolio."""
    return dividend_service.project_portfolio_dividends(db, current_user.id)


@router.get("/summary")
def portfolio_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Portfolio-level metrics: value, cost, gain/loss, sector breakdown."""
    holdings = db.query(UserHolding).filter(UserHolding.user_id == current_user.id).all()

    total_value = Decimal("0")
    total_cost = Decimal("0")
    total_dividend_income = Decimal("0")
    sectors: dict[str, Decimal] = {}

    for h in holdings:
        company = h.company
        market_value = Decimal(h.shares_held) * (company.current_price or Decimal("0"))
        cost_basis = Decimal(h.shares_held) * (h.purchase_price or company.current_price or Decimal("0"))
        total_value += market_value
        total_cost += cost_basis

        sector = company.sector or "Other"
        sectors[sector] = sectors.get(sector, Decimal("0")) + market_value

        # Sum all paid dividends for this company
        paid_divs = (
            db.query(Dividend)
            .filter(Dividend.company_id == company.id, Dividend.status == "paid")
            .all()
        )
        for d in paid_divs:
            total_dividend_income += Decimal(h.shares_held) * d.dividend_per_share

    gain_loss = total_value - total_cost
    gain_loss_pct = Decimal("0")
    if total_cost > 0:
        gain_loss_pct = (gain_loss / total_cost * 100).quantize(Decimal("0.01"))

    sector_breakdown = [
        {"sector": k, "value": str(v.quantize(Decimal("1"))), "percentage": str((v / total_value * 100).quantize(Decimal("0.01"))) if total_value > 0 else "0"}
        for k, v in sorted(sectors.items(), key=lambda x: x[1], reverse=True)
    ]

    return {
        "total_market_value": str(total_value.quantize(Decimal("1"))),
        "total_cost_basis": str(total_cost.quantize(Decimal("1"))),
        "unrealized_gain_loss": str(gain_loss.quantize(Decimal("1"))),
        "unrealized_gain_loss_pct": str(gain_loss_pct),
        "total_dividend_income": str(total_dividend_income.quantize(Decimal("1"))),
        "holdings_count": len(holdings),
        "sector_breakdown": sector_breakdown,
    }


@router.get("/dividend-history")
def dividend_income_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dividend income history — all paid dividends for held companies."""
    holdings = db.query(UserHolding).filter(UserHolding.user_id == current_user.id).all()

    history = []
    for h in holdings:
        company = h.company
        paid_divs = (
            db.query(Dividend)
            .filter(Dividend.company_id == company.id, Dividend.status == "paid")
            .order_by(desc(Dividend.payment_date))
            .all()
        )
        for d in paid_divs:
            gross = Decimal(h.shares_held) * d.dividend_per_share
            history.append({
                "symbol": company.symbol,
                "company_name": company.name,
                "financial_year": d.financial_year,
                "dividend_per_share": str(d.dividend_per_share),
                "shares": h.shares_held,
                "gross_income": str(gross.quantize(Decimal("0.01"))),
                "payment_date": d.payment_date.isoformat() if d.payment_date else None,
            })

    history.sort(key=lambda x: x["payment_date"] or "", reverse=True)
    return history


@router.get("/performance")
def portfolio_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Detailed portfolio performance: gain/loss per holding, risk score, top performers."""
    holdings = db.query(UserHolding).filter(UserHolding.user_id == current_user.id).all()

    if not holdings:
        return {"holdings": [], "summary": {}}

    performance = []
    total_value = Decimal("0")
    total_cost = Decimal("0")
    total_div_income = Decimal("0")

    for h in holdings:
        company = h.company
        market_value = Decimal(h.shares_held) * (company.current_price or Decimal("0"))
        cost_basis = Decimal(h.shares_held) * (h.purchase_price or company.current_price or Decimal("0"))
        capital_gain = market_value - cost_basis
        capital_gain_pct = Decimal("0")
        if cost_basis > 0:
            capital_gain_pct = (capital_gain / cost_basis * 100).quantize(Decimal("0.01"))

        # Dividend income from this holding
        paid_divs = (
            db.query(Dividend)
            .filter(Dividend.company_id == company.id, Dividend.status == "paid")
            .all()
        )
        div_income = sum(Decimal(h.shares_held) * d.dividend_per_share for d in paid_divs)
        total_div_income += div_income

        # Total return = capital gain + dividend income
        total_return = capital_gain + div_income
        total_return_pct = Decimal("0")
        if cost_basis > 0:
            total_return_pct = (total_return / cost_basis * 100).quantize(Decimal("0.01"))

        # Latest yield
        latest_div = (
            db.query(Dividend)
            .filter(Dividend.company_id == company.id)
            .order_by(desc(Dividend.financial_year))
            .first()
        )
        div_yield = Decimal("0")
        if latest_div and company.current_price and company.current_price > 0:
            div_yield = (latest_div.dividend_per_share / company.current_price * 100).quantize(Decimal("0.01"))

        # Yield on cost
        yield_on_cost = Decimal("0")
        if latest_div and h.purchase_price and h.purchase_price > 0:
            yield_on_cost = (latest_div.dividend_per_share / h.purchase_price * 100).quantize(Decimal("0.01"))

        total_value += market_value
        total_cost += cost_basis

        performance.append({
            "symbol": company.symbol,
            "company_name": company.name,
            "sector": company.sector,
            "shares": h.shares_held,
            "purchase_price": str(h.purchase_price) if h.purchase_price else None,
            "current_price": str(company.current_price) if company.current_price else None,
            "market_value": str(market_value.quantize(Decimal("1"))),
            "cost_basis": str(cost_basis.quantize(Decimal("1"))),
            "capital_gain": str(capital_gain.quantize(Decimal("1"))),
            "capital_gain_pct": str(capital_gain_pct),
            "dividend_income": str(div_income.quantize(Decimal("1"))),
            "total_return": str(total_return.quantize(Decimal("1"))),
            "total_return_pct": str(total_return_pct),
            "dividend_yield": str(div_yield),
            "yield_on_cost": str(yield_on_cost),
        })

    # Sort by total return
    performance.sort(key=lambda x: Decimal(x["total_return"]), reverse=True)

    # Portfolio-level metrics
    total_gain = total_value - total_cost
    total_gain_pct = Decimal("0")
    if total_cost > 0:
        total_gain_pct = (total_gain / total_cost * 100).quantize(Decimal("0.01"))

    total_return_all = total_gain + total_div_income
    total_return_pct = Decimal("0")
    if total_cost > 0:
        total_return_pct = (total_return_all / total_cost * 100).quantize(Decimal("0.01"))

    return {
        "holdings": performance,
        "summary": {
            "total_market_value": str(total_value.quantize(Decimal("1"))),
            "total_cost_basis": str(total_cost.quantize(Decimal("1"))),
            "capital_gain": str(total_gain.quantize(Decimal("1"))),
            "capital_gain_pct": str(total_gain_pct),
            "total_dividend_income": str(total_div_income.quantize(Decimal("1"))),
            "total_return": str(total_return_all.quantize(Decimal("1"))),
            "total_return_pct": str(total_return_pct),
            "holdings_count": len(holdings),
        },
    }
