"""
Market analytics — sector analysis, top payers, yield trends, growth leaders.
"""

from decimal import Decimal
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.models import Company, Dividend


def compute_market_overview(db: Session) -> dict:
    companies = db.query(Company).filter(Company.current_price > 0).all()
    total_market_cap = Decimal("0")
    paying_count = 0
    total_dividends_this_year = Decimal("0")
    increased = 0
    decreased = 0

    for c in companies:
        cap = (c.current_price or 0) * (c.total_shares or 0)
        total_market_cap += cap

        divs = (
            db.query(Dividend)
            .filter(Dividend.company_id == c.id)
            .order_by(desc(Dividend.financial_year))
            .limit(2)
            .all()
        )
        if divs:
            paying_count += 1
            total_dividends_this_year += divs[0].dividend_per_share * (c.total_shares or 0)
            if len(divs) == 2:
                if divs[0].dividend_per_share > divs[1].dividend_per_share:
                    increased += 1
                elif divs[0].dividend_per_share < divs[1].dividend_per_share:
                    decreased += 1

    avg_yield = Decimal("0")
    if companies:
        yields = []
        for c in companies:
            latest = (
                db.query(Dividend)
                .filter(Dividend.company_id == c.id)
                .order_by(desc(Dividend.financial_year))
                .first()
            )
            if latest and c.current_price and c.current_price > 0:
                yields.append(latest.dividend_per_share / c.current_price * 100)
        if yields:
            avg_yield = (sum(yields) / len(yields)).quantize(Decimal("0.01"))

    return {
        "total_companies": len(companies),
        "companies_paying_dividends": paying_count,
        "total_market_cap": str(total_market_cap.quantize(Decimal("1"))),
        "average_yield": str(avg_yield),
        "total_dividends_paid": str(total_dividends_this_year.quantize(Decimal("1"))),
        "dividend_increased": increased,
        "dividend_decreased": decreased,
        "dividend_unchanged": paying_count - increased - decreased,
    }


def compute_sector_analysis(db: Session) -> list[dict]:
    sectors: dict[str, dict] = {}
    companies = db.query(Company).filter(Company.current_price > 0).all()

    for c in companies:
        sector = c.sector or "Other"
        if sector not in sectors:
            sectors[sector] = {
                "sector": sector,
                "company_count": 0,
                "total_market_cap": Decimal("0"),
                "yields": [],
                "best_symbol": None,
                "best_yield": Decimal("0"),
            }

        s = sectors[sector]
        s["company_count"] += 1
        s["total_market_cap"] += (c.current_price or 0) * (c.total_shares or 0)

        latest = (
            db.query(Dividend)
            .filter(Dividend.company_id == c.id)
            .order_by(desc(Dividend.financial_year))
            .first()
        )
        if latest and c.current_price and c.current_price > 0:
            y = latest.dividend_per_share / c.current_price * 100
            s["yields"].append(y)
            if y > s["best_yield"]:
                s["best_yield"] = y
                s["best_symbol"] = c.symbol

    results = []
    for s in sectors.values():
        avg = (
            (sum(s["yields"]) / len(s["yields"])).quantize(Decimal("0.01"))
            if s["yields"]
            else Decimal("0")
        )
        results.append({
            "sector": s["sector"],
            "company_count": s["company_count"],
            "total_market_cap": str(s["total_market_cap"].quantize(Decimal("1"))),
            "average_yield": str(avg),
            "best_performer": s["best_symbol"],
            "best_yield": str(s["best_yield"].quantize(Decimal("0.01"))),
        })

    results.sort(key=lambda x: Decimal(x["average_yield"]), reverse=True)
    return results


def compute_top_payers(db: Session, limit: int = 10) -> list[dict]:
    companies = db.query(Company).filter(Company.current_price > 0).all()
    payers = []

    for c in companies:
        latest = (
            db.query(Dividend)
            .filter(Dividend.company_id == c.id)
            .order_by(desc(Dividend.financial_year))
            .first()
        )
        if not latest:
            continue

        total_payout = latest.dividend_per_share * (c.total_shares or 0)
        div_yield = (
            latest.dividend_per_share / c.current_price * 100
            if c.current_price and c.current_price > 0
            else Decimal("0")
        )

        payers.append({
            "symbol": c.symbol,
            "name": c.name,
            "sector": c.sector,
            "dividend_per_share": str(latest.dividend_per_share),
            "total_payout": str(total_payout.quantize(Decimal("1"))),
            "dividend_yield": str(div_yield.quantize(Decimal("0.01"))),
            "financial_year": latest.financial_year,
        })

    payers.sort(key=lambda x: Decimal(x["total_payout"]), reverse=True)
    return payers[:limit]


def compute_yield_trends(db: Session) -> list[dict]:
    """Year-over-year yield data for companies with 3+ years of dividends."""
    companies = db.query(Company).filter(Company.current_price > 0).all()
    results = []

    for c in companies:
        divs = (
            db.query(Dividend)
            .filter(Dividend.company_id == c.id)
            .order_by(Dividend.financial_year)
            .all()
        )
        if len(divs) < 3:
            continue

        yearly = {}
        for d in divs:
            yearly[d.financial_year] = str(d.dividend_per_share)

        results.append({
            "symbol": c.symbol,
            "name": c.name,
            "current_price": str(c.current_price),
            "yearly_dividends": yearly,
            "years_of_data": len(yearly),
        })

    results.sort(key=lambda x: x["years_of_data"], reverse=True)
    return results


def compute_growth_leaders(db: Session) -> list[dict]:
    """Companies ranked by dividend growth rate (CAGR)."""
    companies = db.query(Company).filter(Company.current_price > 0).all()
    leaders = []

    for c in companies:
        divs = (
            db.query(Dividend)
            .filter(Dividend.company_id == c.id)
            .order_by(Dividend.financial_year)
            .all()
        )
        if len(divs) < 2:
            continue

        first_dps = divs[0].dividend_per_share
        last_dps = divs[-1].dividend_per_share
        years = len(divs) - 1

        if first_dps <= 0 or years <= 0:
            continue

        # CAGR = (end/start)^(1/years) - 1
        ratio = float(last_dps / first_dps)
        cagr = (ratio ** (1.0 / years) - 1) * 100

        leaders.append({
            "symbol": c.symbol,
            "name": c.name,
            "sector": c.sector,
            "first_dividend": str(first_dps),
            "latest_dividend": str(last_dps),
            "years": years,
            "cagr": str(Decimal(str(round(cagr, 2)))),
            "current_yield": str(
                (last_dps / c.current_price * 100).quantize(Decimal("0.01"))
                if c.current_price and c.current_price > 0
                else Decimal("0")
            ),
        })

    leaders.sort(key=lambda x: float(x["cagr"]), reverse=True)
    return leaders


def compute_dividend_aristocrats(db: Session) -> list[dict]:
    """Companies with 3+ years of consecutive dividend increases."""
    companies = db.query(Company).filter(Company.current_price > 0).all()
    aristocrats = []

    for c in companies:
        divs = (
            db.query(Dividend)
            .filter(Dividend.company_id == c.id)
            .order_by(Dividend.financial_year)
            .all()
        )
        if len(divs) < 3:
            continue

        # Check consecutive increases
        consecutive = 0
        max_streak = 0
        for i in range(1, len(divs)):
            if divs[i].dividend_per_share > divs[i - 1].dividend_per_share:
                consecutive += 1
                max_streak = max(max_streak, consecutive)
            else:
                consecutive = 0

        if max_streak < 2:
            continue

        first_dps = divs[0].dividend_per_share
        last_dps = divs[-1].dividend_per_share
        years = len(divs) - 1
        cagr = 0.0
        if first_dps > 0 and years > 0:
            cagr = (float(last_dps / first_dps) ** (1.0 / years) - 1) * 100

        div_yield = Decimal("0")
        if c.current_price and c.current_price > 0:
            div_yield = (last_dps / c.current_price * 100).quantize(Decimal("0.01"))

        aristocrats.append({
            "symbol": c.symbol,
            "name": c.name,
            "sector": c.sector,
            "consecutive_increases": max_streak,
            "years_of_data": len(divs),
            "latest_dividend": str(last_dps),
            "dividend_yield": str(div_yield),
            "cagr": str(Decimal(str(round(cagr, 2)))),
        })

    aristocrats.sort(key=lambda x: x["consecutive_increases"], reverse=True)
    return aristocrats


def compute_market_movers(db: Session) -> dict:
    """Companies with biggest dividend changes (increases and cuts)."""
    companies = db.query(Company).filter(Company.current_price > 0).all()
    increases = []
    decreases = []

    for c in companies:
        divs = (
            db.query(Dividend)
            .filter(Dividend.company_id == c.id)
            .order_by(desc(Dividend.financial_year))
            .limit(2)
            .all()
        )
        if len(divs) < 2:
            continue

        latest = divs[0].dividend_per_share
        previous = divs[1].dividend_per_share
        if previous <= 0:
            continue

        change_pct = float((latest - previous) / previous * 100)
        entry = {
            "symbol": c.symbol,
            "name": c.name,
            "sector": c.sector,
            "previous_dividend": str(previous),
            "latest_dividend": str(latest),
            "change_pct": str(round(change_pct, 2)),
        }

        if change_pct > 0:
            increases.append(entry)
        elif change_pct < 0:
            decreases.append(entry)

    increases.sort(key=lambda x: float(x["change_pct"]), reverse=True)
    decreases.sort(key=lambda x: float(x["change_pct"]))

    return {
        "biggest_increases": increases[:10],
        "biggest_decreases": decreases[:10],
    }


def compute_risk_metrics(db: Session) -> list[dict]:
    """Simple risk scoring for DSE stocks based on dividend consistency and yield."""
    companies = db.query(Company).filter(Company.current_price > 0).all()
    metrics = []

    for c in companies:
        divs = (
            db.query(Dividend)
            .filter(Dividend.company_id == c.id)
            .order_by(Dividend.financial_year)
            .all()
        )
        if not divs:
            continue

        # Consistency score (0-100)
        years_paid = len(divs)
        consistency = min(years_paid * 20, 100)  # 5+ years = 100

        # Growth score
        growth_score = 50  # neutral
        if len(divs) >= 2:
            increases = sum(
                1 for i in range(1, len(divs))
                if divs[i].dividend_per_share > divs[i - 1].dividend_per_share
            )
            growth_score = int(increases / (len(divs) - 1) * 100)

        # Yield score
        div_yield = Decimal("0")
        latest = divs[-1]
        if c.current_price and c.current_price > 0:
            div_yield = (latest.dividend_per_share / c.current_price * 100)

        yield_score = min(int(float(div_yield) * 15), 100)

        # Overall score (weighted average)
        overall = int(consistency * 0.4 + growth_score * 0.3 + yield_score * 0.3)

        risk_level = "Low" if overall >= 70 else "Medium" if overall >= 40 else "High"

        metrics.append({
            "symbol": c.symbol,
            "name": c.name,
            "sector": c.sector,
            "consistency_score": consistency,
            "growth_score": growth_score,
            "yield_score": yield_score,
            "overall_score": overall,
            "risk_level": risk_level,
            "dividend_yield": str(div_yield.quantize(Decimal("0.01"))),
            "years_of_data": years_paid,
        })

    metrics.sort(key=lambda x: x["overall_score"], reverse=True)
    return metrics
