"""
Dividend data service — queries, projections, and calendar logic.
"""

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models import Company, Dividend, UserHolding


def get_all_dividends(db: Session, year: str | None = None) -> list[dict]:
    query = db.query(Dividend).join(Company).order_by(desc(Dividend.announcement_date))
    if year:
        query = query.filter(Dividend.financial_year == year)

    results = []
    for div in query.all():
        results.append(_dividend_to_dict(div))
    return results


def get_upcoming_dividends(db: Session, days_ahead: int = 60) -> list[dict]:
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)

    dividends = (
        db.query(Dividend)
        .join(Company)
        .filter(
            Dividend.books_closure_date >= today,
            Dividend.books_closure_date <= cutoff,
        )
        .order_by(Dividend.books_closure_date)
        .all()
    )

    return [_dividend_to_dict(d) for d in dividends]


def get_dividend_history(db: Session, symbol: str) -> list[dict]:
    company = db.query(Company).filter(Company.symbol == symbol.upper()).first()
    if not company:
        return []

    dividends = (
        db.query(Dividend)
        .filter(Dividend.company_id == company.id)
        .order_by(desc(Dividend.financial_year))
        .all()
    )

    return [_dividend_to_dict(d) for d in dividends]


def get_dividend_yields(db: Session) -> list[dict]:
    """Calculate current dividend yield for all companies with dividend history."""
    companies = db.query(Company).filter(Company.current_price > 0).all()
    results = []

    for company in companies:
        latest_div = (
            db.query(Dividend)
            .filter(Dividend.company_id == company.id)
            .order_by(desc(Dividend.financial_year))
            .first()
        )

        if not latest_div:
            continue

        div_yield = (
            latest_div.dividend_per_share / company.current_price * 100
        )

        results.append(
            {
                "symbol": company.symbol,
                "name": company.name,
                "sector": company.sector,
                "current_price": str(company.current_price),
                "last_dividend": str(latest_div.dividend_per_share),
                "financial_year": latest_div.financial_year,
                "dividend_yield": str(div_yield.quantize(Decimal("0.01"))),
                "status": latest_div.status,
            }
        )

    results.sort(key=lambda x: Decimal(x["dividend_yield"]), reverse=True)
    return results


def project_portfolio_dividends(db: Session, user_id: int) -> dict:
    """Project annual dividends for a user's portfolio."""
    holdings = (
        db.query(UserHolding)
        .filter(UserHolding.user_id == user_id)
        .all()
    )

    projections = []
    total_gross = Decimal("0")
    total_invested = Decimal("0")

    for holding in holdings:
        company = db.query(Company).get(holding.company_id)
        latest_div = (
            db.query(Dividend)
            .filter(Dividend.company_id == company.id)
            .order_by(desc(Dividend.financial_year))
            .first()
        )

        if not latest_div:
            continue

        gross = Decimal(holding.shares_held) * latest_div.dividend_per_share
        invested = Decimal(holding.shares_held) * (
            holding.purchase_price or company.current_price or Decimal("0")
        )

        total_gross += gross
        total_invested += invested

        projections.append(
            {
                "symbol": company.symbol,
                "name": company.name,
                "shares": holding.shares_held,
                "last_dividend_per_share": str(latest_div.dividend_per_share),
                "projected_gross": str(gross),
                "last_payment_date": (
                    latest_div.payment_date.isoformat()
                    if latest_div.payment_date
                    else None
                ),
            }
        )

    portfolio_yield = Decimal("0")
    if total_invested > 0:
        portfolio_yield = (total_gross / total_invested * 100).quantize(
            Decimal("0.01")
        )

    return {
        "projections": projections,
        "total_projected_gross": str(total_gross),
        "total_invested": str(total_invested),
        "portfolio_yield_gross": str(portfolio_yield),
        "monthly_income_equivalent": str(
            (total_gross / 12).quantize(Decimal("0.01"))
        ),
    }


def get_alerts_due(db: Session, days_before: int = 7) -> list[dict]:
    """Find dividends with books closing within N days — for alert engine."""
    today = date.today()
    target = today + timedelta(days=days_before)

    dividends = (
        db.query(Dividend)
        .join(Company)
        .filter(
            Dividend.books_closure_date == target,
            Dividend.status == "announced",
        )
        .all()
    )

    return [
        {
            "symbol": d.company.symbol,
            "name": d.company.name,
            "dividend_per_share": str(d.dividend_per_share),
            "books_closure_date": d.books_closure_date.isoformat(),
            "days_until_closure": days_before,
        }
        for d in dividends
    ]


def _dividend_to_dict(div: Dividend) -> dict:
    return {
        "id": div.id,
        "symbol": div.company.symbol,
        "company_name": div.company.name,
        "financial_year": div.financial_year,
        "dividend_per_share": str(div.dividend_per_share),
        "announcement_date": (
            div.announcement_date.isoformat() if div.announcement_date else None
        ),
        "books_closure_date": (
            div.books_closure_date.isoformat() if div.books_closure_date else None
        ),
        "payment_date": (
            div.payment_date.isoformat() if div.payment_date else None
        ),
        "dividend_type": div.dividend_type,
        "status": div.status,
    }
