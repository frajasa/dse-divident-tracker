from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Company, Dividend

router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.get("/")
def list_companies(
    q: str | None = None,
    sector: str | None = None,
    db: Session = Depends(get_db),
):
    """List all DSE-listed companies, optionally filtered by search query or sector."""
    query = db.query(Company).order_by(Company.symbol)

    if q:
        pattern = f"%{q}%"
        query = query.filter(
            Company.symbol.ilike(pattern) | Company.name.ilike(pattern)
        )

    if sector:
        query = query.filter(Company.sector.ilike(f"%{sector}%"))

    companies = query.all()
    return [
        {
            "id": c.id,
            "symbol": c.symbol,
            "name": c.name,
            "sector": c.sector,
            "total_shares": c.total_shares,
            "current_price": str(c.current_price) if c.current_price else None,
        }
        for c in companies
    ]


@router.get("/sectors")
def list_sectors(db: Session = Depends(get_db)):
    """List all unique sectors."""
    sectors = (
        db.query(Company.sector)
        .filter(Company.sector.isnot(None))
        .distinct()
        .order_by(Company.sector)
        .all()
    )
    return [s[0] for s in sectors]


@router.get("/{symbol}")
def get_company(symbol: str, db: Session = Depends(get_db)):
    """Get enriched details for a specific company."""
    company = db.query(Company).filter(Company.symbol == symbol.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{symbol}' not found")

    # Get all dividends
    divs = (
        db.query(Dividend)
        .filter(Dividend.company_id == company.id)
        .order_by(desc(Dividend.financial_year))
        .all()
    )

    latest_div = divs[0] if divs else None

    # Calculate dividend yield
    div_yield = Decimal("0")
    if latest_div and company.current_price and company.current_price > 0:
        div_yield = (latest_div.dividend_per_share / company.current_price * 100).quantize(Decimal("0.01"))

    # Calculate 5-year average DPS
    recent_divs = divs[:5]
    avg_dps = Decimal("0")
    if recent_divs:
        avg_dps = (sum(d.dividend_per_share for d in recent_divs) / len(recent_divs)).quantize(Decimal("0.01"))

    # Calculate dividend growth rate (CAGR)
    growth_rate = None
    if len(divs) >= 2:
        first_dps = divs[-1].dividend_per_share
        last_dps = divs[0].dividend_per_share
        years = len(divs) - 1
        if first_dps > 0 and years > 0:
            ratio = float(last_dps / first_dps)
            cagr = (ratio ** (1.0 / years) - 1) * 100
            growth_rate = str(Decimal(str(round(cagr, 2))))

    # Sector peers
    peers = (
        db.query(Company)
        .filter(Company.sector == company.sector, Company.id != company.id, Company.current_price > 0)
        .all()
    )
    peer_list = []
    for p in peers:
        p_latest = (
            db.query(Dividend)
            .filter(Dividend.company_id == p.id)
            .order_by(desc(Dividend.financial_year))
            .first()
        )
        p_yield = Decimal("0")
        if p_latest and p.current_price and p.current_price > 0:
            p_yield = (p_latest.dividend_per_share / p.current_price * 100).quantize(Decimal("0.01"))
        peer_list.append({
            "symbol": p.symbol,
            "name": p.name,
            "current_price": str(p.current_price),
            "dividend_yield": str(p_yield),
        })

    return {
        "id": company.id,
        "symbol": company.symbol,
        "name": company.name,
        "sector": company.sector,
        "total_shares": company.total_shares,
        "current_price": str(company.current_price) if company.current_price else None,
        "latest_dividend": str(latest_div.dividend_per_share) if latest_div else None,
        "latest_dividend_year": latest_div.financial_year if latest_div else None,
        "dividend_yield": str(div_yield),
        "avg_dividend_5yr": str(avg_dps),
        "dividend_growth_rate": growth_rate,
        "total_dividends_paid": len(divs),
        "payout_consistency": f"{len(divs)} years",
        "sector_peers": peer_list,
    }
