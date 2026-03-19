"""
Seed the database with DSE-listed companies using LIVE data from the DSE website.

Fetches real-time prices from the DSE API and scrapes dividend data from
the corporate actions page. Company names and sectors are maintained as a
lookup since the DSE API only provides ticker symbols.

Run: python scripts/seed_data.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from decimal import Decimal

from app.database import SessionLocal, engine, Base
from app.models import Company, Dividend
from app.scrapers.dse_price_scraper import DSEPriceScraper
from app.scrapers.dse_dividend_scraper import DSEDividendScraper

# Create tables
Base.metadata.create_all(bind=engine)

# ─── Company metadata (name, sector, shares) ──────────────────────
# The DSE API only returns symbols + prices. Names, sectors, and share
# counts come from this lookup, sourced from DSE listed company profiles.
# Update this when new companies are listed on the DSE.

COMPANY_META = {
    "CRDB":      {"name": "CRDB Bank Plc",                        "sector": "Banking",              "total_shares": 2_611_862_500},
    "NMB":       {"name": "NMB Bank Plc",                         "sector": "Banking",              "total_shares": 500_000_000},
    "DCB":       {"name": "DCB Commercial Bank Plc",              "sector": "Banking",              "total_shares": 191_441_218},
    "MCB":       {"name": "Mkombozi Commercial Bank Plc",         "sector": "Banking",              "total_shares": 61_787_667},
    "MKCB":      {"name": "Maendeleo Bank Plc",                   "sector": "Banking",              "total_shares": 32_000_000},
    "KCB":       {"name": "KCB Group Plc",                        "sector": "Banking",              "total_shares": 3_206_611_400},
    "MBP":       {"name": "Mwalimu Commercial Bank Plc",          "sector": "Banking",              "total_shares": 100_000_000},
    "YETU":      {"name": "Yetu Microfinance Bank Plc",           "sector": "Banking",              "total_shares": 78_469_374},
    "MUCOBA":    {"name": "Mucoba Bank Plc",                      "sector": "Banking",              "total_shares": 30_000_000},
    "TBL":       {"name": "Tanzania Breweries Ltd",               "sector": "Manufacturing",        "total_shares": 295_058_870},
    "TCC":       {"name": "Tanzania Cigarette Company",           "sector": "Manufacturing",        "total_shares": 20_000_000},
    "TPCC":      {"name": "Tanzania Portland Cement Company",     "sector": "Manufacturing",        "total_shares": 179_923_100},
    "TOL":       {"name": "Tanzania Oxygen Ltd",                  "sector": "Manufacturing",        "total_shares": 17_500_000},
    "USL":       {"name": "USL Ltd",                              "sector": "Manufacturing",        "total_shares": 25_000_000},
    "EABL":      {"name": "East African Breweries Ltd",           "sector": "Manufacturing",        "total_shares": 790_774_356},
    "TCCL":      {"name": "Tanzania China Clay Ltd",              "sector": "Manufacturing",        "total_shares": 98_000_000},
    "SWIS":      {"name": "Swissport Tanzania Plc",               "sector": "Services",             "total_shares": 36_000_000},
    "VODA":      {"name": "Vodacom Tanzania Plc",                 "sector": "Telecommunications",   "total_shares": 2_240_000_000},
    "NMG":       {"name": "Nation Media Group Ltd",               "sector": "Media",                "total_shares": 188_542_286},
    "NICO":      {"name": "NICO (Tanzania) Ltd",                  "sector": "Insurance",            "total_shares": 61_651_180},
    "PAL":       {"name": "PAL Pensions Ltd",                     "sector": "Insurance",            "total_shares": 160_400_000},
    "AFRIPRISE": {"name": "Afriprise Holdings Ltd",               "sector": "Financial Services",   "total_shares": 40_000_000},
    "DSE":       {"name": "Dar es Salaam Stock Exchange Plc",     "sector": "Financial Services",   "total_shares": 23_826_120},
    "JHL":       {"name": "Jacaranda Hotels Ltd",                 "sector": "Hospitality",          "total_shares": 40_000_000},
    "TTP":       {"name": "TTP Group Plc",                        "sector": "Agriculture",          "total_shares": 95_000_000},
    "JATU":      {"name": "Jatu Plc",                             "sector": "Real Estate",          "total_shares": 50_000_000},
    "KA":        {"name": "Kenya Airways Ltd",                    "sector": "Aviation",             "total_shares": 1_496_469_035},
    "SWALA":     {"name": "Swala Oil and Gas Plc",                "sector": "Energy",               "total_shares": 71_745_849},
}


def seed():
    db = SessionLocal()

    print("Fetching live prices from DSE API...")
    price_scraper = DSEPriceScraper()
    price_records = price_scraper.scrape_market_prices()
    print(f"  Got {len(price_records)} price records")

    print("Fetching dividend data from DSE corporate actions...")
    dividend_scraper = DSEDividendScraper()
    dividend_records = dividend_scraper.scrape_corporate_actions()
    print(f"  Got {len(dividend_records)} dividend records")

    # Build price lookup from live API
    live_prices = {r.symbol: r.price for r in price_records}

    # Clear existing data (respect FK order)
    db.query(Dividend).delete()
    db.query(Company).delete()
    db.commit()

    # Insert companies — use live prices, fall back to metadata
    company_map = {}
    symbols_inserted = set()

    # First: insert companies we have metadata for
    for symbol, meta in COMPANY_META.items():
        price = live_prices.pop(symbol, None)
        company = Company(
            symbol=symbol,
            name=meta["name"],
            sector=meta["sector"],
            total_shares=meta["total_shares"],
            current_price=price,
        )
        db.add(company)
        db.flush()
        company_map[symbol] = company.id
        symbols_inserted.add(symbol)

    # Second: insert any companies from the API that aren't in our metadata
    for symbol, price in live_prices.items():
        if symbol not in symbols_inserted:
            print(f"  New company from API (no metadata): {symbol} @ {price}")
            company = Company(
                symbol=symbol,
                name=symbol,  # Use symbol as placeholder name
                sector=None,
                total_shares=None,
                current_price=price,
            )
            db.add(company)
            db.flush()
            company_map[symbol] = company.id
            symbols_inserted.add(symbol)

    db.commit()
    print(f"Inserted {len(symbols_inserted)} companies with live prices")

    # Insert dividends from scraped data
    created = 0
    skipped = 0
    for rec in dividend_records:
        company_id = company_map.get(rec.symbol)
        if not company_id:
            print(f"  WARNING: dividend for unknown symbol {rec.symbol}, skipping")
            skipped += 1
            continue

        dividend = Dividend(
            company_id=company_id,
            financial_year=rec.financial_year,
            dividend_per_share=rec.dividend_per_share,
            announcement_date=rec.announcement_date,
            books_closure_date=rec.books_closure_date,
            payment_date=rec.payment_date,
            dividend_type=rec.dividend_type,
            status=_infer_status(rec),
            source_url=rec.source_url,
        )
        db.add(dividend)
        created += 1

    db.commit()
    db.close()

    print(f"Inserted {created} dividend records ({skipped} skipped)")
    print("Done! Database seeded with live DSE data.")


def _infer_status(rec):
    """Infer dividend status based on dates relative to today."""
    from datetime import date
    today = date.today()

    if rec.payment_date and rec.payment_date <= today:
        return "paid"
    if rec.books_closure_date and rec.books_closure_date <= today:
        return "books_closed"
    return "announced"


if __name__ == "__main__":
    seed()
