"""
Rule-based AI stock assistant — answers questions about DSE stocks
using keyword matching and database lookups.
"""

import re
from decimal import Decimal
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models import Company, Dividend, UserHolding
from app.services.tax_calculator import TAX_RATES, DTA_RATES


SUGGESTED_QUESTIONS = [
    "What is the highest yielding stock?",
    "Tell me about TBL",
    "When are the upcoming dividends?",
    "Compare TBL and NMB",
    "Which banking stocks pay dividends?",
    "What is the tax rate for residents?",
    "What are the best dividend stocks?",
    "Show me manufacturing sector stocks",
    "What is dividend yield?",
    "How do I start investing?",
    "Which stocks are safest?",
    "What is a dividend aristocrat?",
]

# Known symbols loaded once per request from DB
_SECTORS = [
    "banking", "manufacturing", "telecommunications", "insurance",
    "financial services", "media", "services", "hospitality",
    "agriculture", "real estate", "aviation", "energy",
]


def process_question(db: Session, question: str, user_id: int | None = None) -> dict:
    q = question.strip().lower()

    # Try each handler in order of specificity
    for handler in [
        _handle_comparison,
        _handle_stock_lookup,
        _handle_yield_query,
        _handle_sector_query,
        _handle_tax_query,
        _handle_upcoming_query,
        _handle_portfolio_query,
        _handle_best_stocks,
        _handle_education_query,
        _handle_risk_query,
        _handle_aristocrats_query,
        _handle_general,
    ]:
        result = handler(db, q, user_id)
        if result:
            return result

    return _fallback_response()


def _handle_comparison(db: Session, q: str, user_id: int | None) -> dict | None:
    """Handle 'compare X and Y' queries."""
    match = re.search(r"compare\s+(\w+)\s+(?:and|vs|with)\s+(\w+)", q)
    if not match:
        # Also try: "X vs Y"
        match = re.search(r"(\w+)\s+vs\s+(\w+)", q)
    if not match:
        return None

    sym1, sym2 = match.group(1).upper(), match.group(2).upper()
    c1 = db.query(Company).filter(Company.symbol == sym1).first()
    c2 = db.query(Company).filter(Company.symbol == sym2).first()

    if not c1 or not c2:
        missing = sym1 if not c1 else sym2
        return {
            "answer": f"I couldn't find {missing} on the DSE. Please check the symbol.",
            "data": None,
            "suggestions": SUGGESTED_QUESTIONS[:3],
        }

    def _company_stats(company):
        latest = (
            db.query(Dividend).filter(Dividend.company_id == company.id)
            .order_by(desc(Dividend.financial_year)).first()
        )
        div_yield = Decimal("0")
        if latest and company.current_price and company.current_price > 0:
            div_yield = (latest.dividend_per_share / company.current_price * 100).quantize(Decimal("0.01"))

        divs = (
            db.query(Dividend).filter(Dividend.company_id == company.id)
            .order_by(Dividend.financial_year).all()
        )
        growth = "N/A"
        if len(divs) >= 2:
            first, last = divs[0].dividend_per_share, divs[-1].dividend_per_share
            if first > 0:
                years = len(divs) - 1
                cagr = (float(last / first) ** (1.0 / years) - 1) * 100
                growth = f"{cagr:.1f}%"

        return {
            "symbol": company.symbol,
            "name": company.name,
            "sector": company.sector,
            "price": str(company.current_price),
            "latest_dividend": str(latest.dividend_per_share) if latest else "N/A",
            "dividend_yield": str(div_yield),
            "dividend_growth_cagr": growth,
            "years_of_dividends": len(divs),
        }

    stats1 = _company_stats(c1)
    stats2 = _company_stats(c2)

    y1 = Decimal(stats1["dividend_yield"])
    y2 = Decimal(stats2["dividend_yield"])
    better = stats1["symbol"] if y1 > y2 else stats2["symbol"]

    answer = (
        f"**{stats1['symbol']} vs {stats2['symbol']}**\n\n"
        f"- **{stats1['symbol']}** ({stats1['sector']}): Price TZS {stats1['price']}, "
        f"Dividend TZS {stats1['latest_dividend']}/share, Yield {stats1['dividend_yield']}%, "
        f"Growth {stats1['dividend_growth_cagr']}\n"
        f"- **{stats2['symbol']}** ({stats2['sector']}): Price TZS {stats2['price']}, "
        f"Dividend TZS {stats2['latest_dividend']}/share, Yield {stats2['dividend_yield']}%, "
        f"Growth {stats2['dividend_growth_cagr']}\n\n"
        f"By yield, **{better}** currently offers the higher dividend return."
    )

    return {
        "answer": answer,
        "data": {"comparison": [stats1, stats2]},
        "suggestions": [
            f"Tell me more about {stats1['symbol']}",
            f"Tell me more about {stats2['symbol']}",
            "What is the highest yielding stock?",
        ],
    }


def _handle_stock_lookup(db: Session, q: str, user_id: int | None) -> dict | None:
    """Handle queries about a specific stock symbol."""
    # Find any known symbol in the question
    symbols = [c.symbol for c in db.query(Company.symbol).all()]
    found = None
    for sym in symbols:
        if sym.lower() in q.split() or f"about {sym.lower()}" in q:
            found = sym
            break

    if not found:
        return None

    company = db.query(Company).filter(Company.symbol == found).first()
    if not company:
        return None

    divs = (
        db.query(Dividend).filter(Dividend.company_id == company.id)
        .order_by(desc(Dividend.financial_year)).all()
    )
    latest = divs[0] if divs else None

    div_yield = Decimal("0")
    if latest and company.current_price and company.current_price > 0:
        div_yield = (latest.dividend_per_share / company.current_price * 100).quantize(Decimal("0.01"))

    history_summary = ", ".join(
        f"{d.financial_year}: TZS {d.dividend_per_share}" for d in divs[:5]
    )

    answer = (
        f"**{company.symbol} — {company.name}**\n\n"
        f"- **Sector:** {company.sector}\n"
        f"- **Current Price:** TZS {company.current_price:,.0f}\n"
        f"- **Latest Dividend:** TZS {latest.dividend_per_share}/share ({latest.financial_year})\n"
        f"- **Dividend Yield:** {div_yield}%\n"
        f"- **Dividend History:** {history_summary}\n"
        f"- **Total Shares:** {company.total_shares:,}" if company.total_shares else ""
    )

    data = {
        "company": {
            "symbol": company.symbol,
            "name": company.name,
            "sector": company.sector,
            "price": str(company.current_price),
            "dividend_yield": str(div_yield),
            "latest_dividend": str(latest.dividend_per_share) if latest else None,
            "dividends_count": len(divs),
        }
    }

    return {
        "answer": answer,
        "data": data,
        "suggestions": [
            f"Compare {company.symbol} with another stock",
            "What is the highest yielding stock?",
            f"What sector is {company.symbol} in?",
        ],
    }


def _handle_yield_query(db: Session, q: str, user_id: int | None) -> dict | None:
    """Handle 'highest yield', 'best yield', 'top yield' queries."""
    yield_keywords = ["highest yield", "best yield", "top yield", "highest dividend yield"]
    if not any(k in q for k in yield_keywords):
        return None

    companies = db.query(Company).filter(Company.current_price > 0).all()
    yields = []
    for c in companies:
        latest = (
            db.query(Dividend).filter(Dividend.company_id == c.id)
            .order_by(desc(Dividend.financial_year)).first()
        )
        if latest and c.current_price > 0:
            y = (latest.dividend_per_share / c.current_price * 100).quantize(Decimal("0.01"))
            yields.append({"symbol": c.symbol, "name": c.name, "yield": str(y), "dps": str(latest.dividend_per_share)})

    yields.sort(key=lambda x: Decimal(x["yield"]), reverse=True)
    top3 = yields[:3]

    answer = "**Top 3 Highest Yielding DSE Stocks:**\n\n"
    for i, s in enumerate(top3, 1):
        answer += f"{i}. **{s['symbol']}** — {s['yield']}% yield (TZS {s['dps']}/share)\n"

    return {
        "answer": answer,
        "data": {"top_yields": top3},
        "suggestions": [
            f"Tell me about {top3[0]['symbol']}",
            f"Compare {top3[0]['symbol']} and {top3[1]['symbol']}",
            "Show me banking sector stocks",
        ],
    }


def _handle_sector_query(db: Session, q: str, user_id: int | None) -> dict | None:
    """Handle sector-related queries."""
    found_sector = None
    for sector in _SECTORS:
        if sector in q:
            found_sector = sector
            break

    if not found_sector:
        return None

    companies = (
        db.query(Company)
        .filter(func.lower(Company.sector).contains(found_sector))
        .all()
    )

    if not companies:
        return {"answer": f"No companies found in the {found_sector} sector.", "data": None, "suggestions": SUGGESTED_QUESTIONS[:3]}

    items = []
    for c in companies:
        latest = (
            db.query(Dividend).filter(Dividend.company_id == c.id)
            .order_by(desc(Dividend.financial_year)).first()
        )
        div_yield = Decimal("0")
        if latest and c.current_price and c.current_price > 0:
            div_yield = (latest.dividend_per_share / c.current_price * 100).quantize(Decimal("0.01"))

        items.append({
            "symbol": c.symbol,
            "name": c.name,
            "price": str(c.current_price),
            "dividend_yield": str(div_yield),
            "latest_dividend": str(latest.dividend_per_share) if latest else "N/A",
        })

    items.sort(key=lambda x: Decimal(x["dividend_yield"]) if x["dividend_yield"] != "N/A" else Decimal("0"), reverse=True)

    answer = f"**{found_sector.title()} Sector Stocks:**\n\n"
    for s in items:
        answer += f"- **{s['symbol']}** ({s['name']}): Yield {s['dividend_yield']}%, Dividend TZS {s['latest_dividend']}/share\n"

    return {
        "answer": answer,
        "data": {"sector": found_sector, "companies": items},
        "suggestions": [
            f"Tell me about {items[0]['symbol']}" if items else "What is the highest yielding stock?",
            "Compare two stocks",
            "What are the best dividend stocks?",
        ],
    }


from sqlalchemy import func


def _handle_tax_query(db: Session, q: str, user_id: int | None) -> dict | None:
    """Handle tax-related questions."""
    tax_keywords = ["tax", "withholding", "kodi"]
    if not any(k in q for k in tax_keywords):
        return None

    rates_text = "\n".join(
        f"- {res.replace('_', '-').title()} {inv.title()}: {int(rate * 100)}%"
        for (res, inv), rate in TAX_RATES.items()
    )

    dta_text = "\n".join(
        f"- {country}: {int(rate * 100)}%"
        for country, rate in DTA_RATES.items()
    )

    answer = (
        "**Tanzania Dividend Tax Rates:**\n\n"
        f"{rates_text}\n\n"
        "**Double Taxation Agreement (DTA) Rates:**\n\n"
        f"{dta_text}\n\n"
        "Tax is withheld at source by the paying company. "
        "Use the Tax Calculator for detailed calculations."
    )

    return {
        "answer": answer,
        "data": {
            "tax_rates": {f"{k[0]}_{k[1]}": str(v) for k, v in TAX_RATES.items()},
            "dta_rates": {k: str(v) for k, v in DTA_RATES.items()},
        },
        "suggestions": [
            "What is the highest yielding stock?",
            "Tell me about TBL",
            "Show me banking sector stocks",
        ],
    }


def _handle_upcoming_query(db: Session, q: str, user_id: int | None) -> dict | None:
    """Handle upcoming dividend queries."""
    upcoming_keywords = ["upcoming", "next dividend", "when", "soon", "calendar"]
    if not any(k in q for k in upcoming_keywords):
        return None

    from datetime import date, timedelta
    today = date.today()
    cutoff = today + timedelta(days=90)

    divs = (
        db.query(Dividend).join(Company)
        .filter(Dividend.books_closure_date >= today, Dividend.books_closure_date <= cutoff)
        .order_by(Dividend.books_closure_date).all()
    )

    if not divs:
        answer = "There are no upcoming book closures in the next 90 days. Check back later for new announcements."
    else:
        answer = "**Upcoming Dividends (next 90 days):**\n\n"
        for d in divs:
            days_left = (d.books_closure_date - today).days
            answer += (
                f"- **{d.company.symbol}** — TZS {d.dividend_per_share}/share, "
                f"Books close: {d.books_closure_date.isoformat()} ({days_left} days)\n"
            )

    return {
        "answer": answer,
        "data": {
            "upcoming": [
                {
                    "symbol": d.company.symbol,
                    "dividend_per_share": str(d.dividend_per_share),
                    "books_closure_date": d.books_closure_date.isoformat(),
                }
                for d in divs
            ]
        },
        "suggestions": [
            "What is the highest yielding stock?",
            "Tell me about TBL",
            "What are the best dividend stocks?",
        ],
    }


def _handle_portfolio_query(db: Session, q: str, user_id: int | None) -> dict | None:
    """Handle portfolio-related queries for authenticated users."""
    portfolio_keywords = ["my portfolio", "my holdings", "my stocks", "my dividends"]
    if not any(k in q for k in portfolio_keywords):
        return None

    if not user_id:
        return {
            "answer": "Please log in to see your portfolio information. You can manage your holdings in the Portfolio section.",
            "data": None,
            "suggestions": ["What is the highest yielding stock?", "Tell me about TBL"],
        }

    holdings = db.query(UserHolding).filter(UserHolding.user_id == user_id).all()
    if not holdings:
        return {
            "answer": "Your portfolio is empty. Add some stocks in the Portfolio section to get started!",
            "data": None,
            "suggestions": ["What are the best dividend stocks?", "What is the highest yielding stock?"],
        }

    total_value = Decimal("0")
    total_div = Decimal("0")
    items = []

    for h in holdings:
        c = h.company
        latest = (
            db.query(Dividend).filter(Dividend.company_id == c.id)
            .order_by(desc(Dividend.financial_year)).first()
        )
        value = Decimal(h.shares_held) * (c.current_price or 0)
        div_income = Decimal(h.shares_held) * (latest.dividend_per_share if latest else 0)
        total_value += value
        total_div += div_income
        items.append({
            "symbol": c.symbol,
            "shares": h.shares_held,
            "value": str(value.quantize(Decimal("1"))),
            "projected_dividend": str(div_income.quantize(Decimal("1"))),
        })

    answer = (
        f"**Your Portfolio Summary:**\n\n"
        f"- **Total Value:** TZS {total_value:,.0f}\n"
        f"- **Projected Annual Dividends:** TZS {total_div:,.0f}\n"
        f"- **Holdings:** {len(holdings)} stocks\n\n"
    )
    for item in items:
        answer += f"- {item['symbol']}: {item['shares']} shares, Value TZS {Decimal(item['value']):,.0f}\n"

    return {
        "answer": answer,
        "data": {"holdings": items, "total_value": str(total_value.quantize(Decimal("1"))), "total_dividends": str(total_div.quantize(Decimal("1")))},
        "suggestions": ["What is the highest yielding stock?", "Compare two stocks"],
    }


def _handle_best_stocks(db: Session, q: str, user_id: int | None) -> dict | None:
    """Handle 'best stocks', 'good stocks', 'recommend' queries."""
    keywords = ["best stock", "best dividend", "good stock", "recommend", "should i buy", "which stock"]
    if not any(k in q for k in keywords):
        return None

    # Return top 5 by yield as a starting point
    companies = db.query(Company).filter(Company.current_price > 0).all()
    yields = []
    for c in companies:
        latest = (
            db.query(Dividend).filter(Dividend.company_id == c.id)
            .order_by(desc(Dividend.financial_year)).first()
        )
        if latest and c.current_price > 0:
            y = (latest.dividend_per_share / c.current_price * 100).quantize(Decimal("0.01"))
            divs = db.query(Dividend).filter(Dividend.company_id == c.id).count()
            yields.append({"symbol": c.symbol, "name": c.name, "yield": str(y), "consistency": divs})

    yields.sort(key=lambda x: Decimal(x["yield"]), reverse=True)
    top5 = yields[:5]

    answer = (
        "**Top DSE Dividend Stocks by Yield:**\n\n"
        "Here are the highest-yielding stocks based on their latest dividend:\n\n"
    )
    for i, s in enumerate(top5, 1):
        answer += f"{i}. **{s['symbol']}** ({s['name']}) — {s['yield']}% yield, {s['consistency']} years of data\n"

    answer += (
        "\n*Note: Higher yield doesn't always mean better investment. Consider dividend "
        "consistency, growth rate, and sector diversification. This is not financial advice.*"
    )

    return {
        "answer": answer,
        "data": {"top_stocks": top5},
        "suggestions": [
            f"Tell me about {top5[0]['symbol']}",
            f"Compare {top5[0]['symbol']} and {top5[1]['symbol']}",
            "Show me banking sector stocks",
        ],
    }


def _handle_education_query(db: Session, q: str, user_id: int | None) -> dict | None:
    """Handle investment education questions."""
    education_topics = {
        "what is dividend yield": {
            "answer": (
                "**Dividend Yield Explained:**\n\n"
                "Dividend yield measures how much income a stock pays relative to its price.\n\n"
                "**Formula:** Yield = (Annual Dividend / Share Price) x 100\n\n"
                "**On the DSE:**\n"
                "- **Above 5%** = High yield (great for income)\n"
                "- **2% to 5%** = Moderate yield\n"
                "- **Below 2%** = Low yield\n\n"
                "Visit the **Education** section to learn more about dividend analysis!"
            ),
            "suggestions": ["What are the best dividend stocks?", "What is a payout ratio?", "How do I start investing?"],
        },
        "how do i start investing": {
            "answer": (
                "**How to Start Investing on the DSE:**\n\n"
                "1. **Open a CDS account** through a licensed broker (e.g., Orbit Securities, Core Securities)\n"
                "2. **Fund your account** via bank transfer or mobile money\n"
                "3. **Research stocks** — use this app's Yields and Analytics sections\n"
                "4. **Start small** — begin with 1-2 stocks you understand\n"
                "5. **Diversify** — spread across 5-8 stocks in different sectors\n\n"
                "**Minimum investment:** No official minimum, but most brokers suggest starting with TZS 100,000+\n\n"
                "Visit the **Education** section for detailed beginner guides!"
            ),
            "suggestions": ["What are the best dividend stocks?", "What is dividend yield?", "Which stocks are safest?"],
        },
        "what is payout ratio": {
            "answer": (
                "**Payout Ratio:**\n\n"
                "The percentage of earnings a company pays as dividends.\n\n"
                "**Formula:** Payout Ratio = (Dividend Per Share / Earnings Per Share) x 100\n\n"
                "**Interpretation:**\n"
                "- **Below 50%** — Conservative, sustainable\n"
                "- **50-75%** — Balanced\n"
                "- **Above 75%** — Aggressive, may not be sustainable\n"
                "- **Above 100%** — Red flag! Paying more than earned"
            ),
            "suggestions": ["What is dividend yield?", "Which stocks are safest?", "What are the best dividend stocks?"],
        },
    }

    for keywords, response in education_topics.items():
        if all(word in q for word in keywords.split()):
            return {
                "answer": response["answer"],
                "data": None,
                "suggestions": response["suggestions"],
            }

    # General education keywords
    edu_keywords = ["learn", "education", "teach", "explain", "course", "beginner", "how to invest"]
    if any(k in q for k in edu_keywords):
        return {
            "answer": (
                "**Investment Education:**\n\n"
                "I can help you learn about investing! Visit the **Education** section for structured lessons.\n\n"
                "**Available topics:**\n"
                "- Investment Basics (What is DSE, Shares, Dividends)\n"
                "- Stock Analysis (Yield, Payout Ratio, Growth Rate)\n"
                "- Investment Strategies (Dividend Investing, Risk Management, Tax Optimization)\n"
                "- Glossary of key terms\n\n"
                "Or ask me directly about specific topics!"
            ),
            "data": None,
            "suggestions": ["What is dividend yield?", "How do I start investing?", "What are the best dividend stocks?"],
        }

    return None


def _handle_risk_query(db: Session, q: str, user_id: int | None) -> dict | None:
    """Handle risk and safety queries."""
    risk_keywords = ["safe", "safest", "risk", "reliable", "stable", "consistent"]
    if not any(k in q for k in risk_keywords):
        return None

    companies = db.query(Company).filter(Company.current_price > 0).all()
    scored = []

    for c in companies:
        divs = (
            db.query(Dividend).filter(Dividend.company_id == c.id)
            .order_by(Dividend.financial_year).all()
        )
        if len(divs) < 2:
            continue

        years = len(divs)
        increases = sum(
            1 for i in range(1, len(divs))
            if divs[i].dividend_per_share > divs[i - 1].dividend_per_share
        )
        consistency = increases / (years - 1) if years > 1 else 0

        div_yield = Decimal("0")
        if c.current_price and c.current_price > 0:
            div_yield = (divs[-1].dividend_per_share / c.current_price * 100).quantize(Decimal("0.01"))

        score = int(consistency * 60 + min(years * 8, 40))
        scored.append({
            "symbol": c.symbol,
            "name": c.name,
            "sector": c.sector,
            "years_paying": years,
            "consistency": f"{consistency:.0%}",
            "dividend_yield": str(div_yield),
            "score": score,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    top5 = scored[:5]

    answer = "**Most Reliable DSE Dividend Stocks:**\n\n"
    for i, s in enumerate(top5, 1):
        answer += (
            f"{i}. **{s['symbol']}** ({s['name']}) — {s['years_paying']} years of dividends, "
            f"{s['consistency']} increases, {s['dividend_yield']}% yield\n"
        )
    answer += (
        "\n*Reliability is based on dividend consistency and track record. "
        "Past performance does not guarantee future results.*"
    )

    return {
        "answer": answer,
        "data": {"reliable_stocks": top5},
        "suggestions": ["What is the highest yielding stock?", "Compare two of these stocks", "What is dividend yield?"],
    }


def _handle_aristocrats_query(db: Session, q: str, user_id: int | None) -> dict | None:
    """Handle dividend aristocrat queries."""
    keywords = ["aristocrat", "consecutive increase", "growing dividend", "consistent growth"]
    if not any(k in q for k in keywords):
        return None

    from app.services.analytics_service import compute_dividend_aristocrats
    aristocrats = compute_dividend_aristocrats(db)

    if not aristocrats:
        return {
            "answer": "No dividend aristocrats found yet. This requires companies with 2+ consecutive years of dividend increases.",
            "data": None,
            "suggestions": SUGGESTED_QUESTIONS[:3],
        }

    answer = "**DSE Dividend Aristocrats** (consecutive dividend increases):\n\n"
    for i, a in enumerate(aristocrats[:5], 1):
        answer += (
            f"{i}. **{a['symbol']}** ({a['name']}) — {a['consecutive_increases']} consecutive increases, "
            f"Yield {a['dividend_yield']}%, CAGR {a['cagr']}%\n"
        )
    answer += "\n*Dividend aristocrats have the strongest track record of rewarding shareholders.*"

    return {
        "answer": answer,
        "data": {"aristocrats": aristocrats[:5]},
        "suggestions": ["Tell me about " + aristocrats[0]["symbol"], "Which stocks are safest?", "What is dividend yield?"],
    }


def _handle_general(db: Session, q: str, user_id: int | None) -> dict | None:
    """Handle general greetings and simple questions."""
    greetings = ["hello", "hi", "hey", "habari", "mambo", "help"]
    if any(g in q for g in greetings):
        return {
            "answer": (
                "Hello! I'm your DSE Stock Assistant. I can help you with:\n\n"
                "- **Stock information** — Ask about any DSE stock (e.g., 'Tell me about TBL')\n"
                "- **Yield rankings** — 'What is the highest yielding stock?'\n"
                "- **Sector analysis** — 'Show me banking stocks'\n"
                "- **Comparisons** — 'Compare TBL and NMB'\n"
                "- **Tax info** — 'What is the tax rate?'\n"
                "- **Upcoming dividends** — 'When are the next dividends?'\n"
                "- **Portfolio** — 'Show my portfolio' (when logged in)\n"
                "- **Investment education** — 'How do I start investing?'\n"
                "- **Risk analysis** — 'Which stocks are safest?'\n"
                "- **Dividend aristocrats** — 'What is a dividend aristocrat?'\n\n"
                "Try one of the suggestions below!"
            ),
            "data": None,
            "suggestions": SUGGESTED_QUESTIONS[:4],
        }
    return None


def _fallback_response() -> dict:
    return {
        "answer": (
            "I'm not sure I understand that question. I can help with:\n\n"
            "- Stock information (e.g., 'Tell me about CRDB')\n"
            "- Yield rankings (e.g., 'What is the highest yielding stock?')\n"
            "- Sector analysis (e.g., 'Show me banking stocks')\n"
            "- Stock comparisons (e.g., 'Compare TBL and NMB')\n"
            "- Tax information (e.g., 'What is the dividend tax rate?')\n"
            "- Upcoming dividends (e.g., 'When are the next dividends?')\n\n"
            "Try one of the suggestions below!"
        ),
        "data": None,
        "suggestions": SUGGESTED_QUESTIONS[:4],
    }
