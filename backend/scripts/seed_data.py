"""
Seed the database with all DSE-listed companies and historical dividend data.

Run: python -m scripts.seed_data
"""

import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, engine, Base
from app.models import Company, Dividend

# Create tables
Base.metadata.create_all(bind=engine)

# ─── DSE Listed Companies ───────────────────────────────────────────

COMPANIES = [
    {"symbol": "CRDB", "name": "CRDB Bank Plc", "sector": "Banking", "total_shares": 2_611_862_500, "current_price": Decimal("2800.00")},
    {"symbol": "NMB", "name": "NMB Bank Plc", "sector": "Banking", "total_shares": 500_000_000, "current_price": Decimal("14370.00")},
    {"symbol": "DCB", "name": "DCB Commercial Bank Plc", "sector": "Banking", "total_shares": 191_441_218, "current_price": Decimal("685.00")},
    {"symbol": "MCB", "name": "Mkombozi Commercial Bank Plc", "sector": "Banking", "total_shares": 61_787_667, "current_price": Decimal("1720.00")},
    {"symbol": "MKCB", "name": "Maendeleo Bank Plc", "sector": "Banking", "total_shares": 32_000_000, "current_price": Decimal("600.00")},
    {"symbol": "KCB", "name": "KCB Group Plc", "sector": "Banking", "total_shares": 3_206_611_400, "current_price": Decimal("1200.00")},
    {"symbol": "MBP", "name": "Mwalimu Commercial Bank Plc", "sector": "Banking", "total_shares": 100_000_000, "current_price": Decimal("500.00")},

    {"symbol": "TBL", "name": "Tanzania Breweries Ltd", "sector": "Manufacturing", "total_shares": 295_058_870, "current_price": Decimal("9710.00")},
    {"symbol": "TCC", "name": "Tanzania Cigarette Company", "sector": "Manufacturing", "total_shares": 20_000_000, "current_price": Decimal("8800.00")},
    {"symbol": "TPCC", "name": "Tanzania Portland Cement Company", "sector": "Manufacturing", "total_shares": 179_923_100, "current_price": Decimal("6790.00")},
    {"symbol": "TOL", "name": "Tanzania Oxygen Ltd", "sector": "Manufacturing", "total_shares": 17_500_000, "current_price": Decimal("2500.00")},
    {"symbol": "SWIS", "name": "Swissport Tanzania Plc", "sector": "Services", "total_shares": 36_000_000, "current_price": Decimal("4500.00")},

    {"symbol": "VODA", "name": "Vodacom Tanzania Plc", "sector": "Telecommunications", "total_shares": 2_240_000_000, "current_price": Decimal("850.00")},
    {"symbol": "EABL", "name": "East African Breweries Ltd", "sector": "Manufacturing", "total_shares": 790_774_356, "current_price": Decimal("3200.00")},
    {"symbol": "NMG", "name": "Nation Media Group Ltd", "sector": "Media", "total_shares": 188_542_286, "current_price": Decimal("1400.00")},

    {"symbol": "NICO", "name": "NICO (Tanzania) Ltd", "sector": "Insurance", "total_shares": 61_651_180, "current_price": Decimal("3750.00")},
    {"symbol": "PAL", "name": "PAL Pensions Ltd", "sector": "Insurance", "total_shares": 160_400_000, "current_price": Decimal("675.00")},
    {"symbol": "AFRIPRISE", "name": "Afriprise Holdings Ltd", "sector": "Financial Services", "total_shares": 40_000_000, "current_price": Decimal("380.00")},

    {"symbol": "JHL", "name": "Jacaranda Hotels Ltd", "sector": "Hospitality", "total_shares": 40_000_000, "current_price": Decimal("300.00")},
    {"symbol": "TTP", "name": "TTP Group Plc", "sector": "Agriculture", "total_shares": 95_000_000, "current_price": Decimal("585.00")},
    {"symbol": "USL", "name": "USL Ltd", "sector": "Manufacturing", "total_shares": 25_000_000, "current_price": Decimal("2000.00")},
    {"symbol": "YETU", "name": "Yetu Microfinance Bank Plc", "sector": "Banking", "total_shares": 78_469_374, "current_price": Decimal("450.00")},
    {"symbol": "JATU", "name": "Jatu Plc", "sector": "Real Estate", "total_shares": 50_000_000, "current_price": Decimal("400.00")},
    {"symbol": "KA", "name": "Kenya Airways Ltd", "sector": "Aviation", "total_shares": 1_496_469_035, "current_price": Decimal("300.00")},
    {"symbol": "MUCOBA", "name": "Mucoba Bank Plc", "sector": "Banking", "total_shares": 30_000_000, "current_price": Decimal("600.00")},
    {"symbol": "SWALA", "name": "Swala Oil and Gas Plc", "sector": "Energy", "total_shares": 71_745_849, "current_price": Decimal("350.00")},
    {"symbol": "DSE", "name": "Dar es Salaam Stock Exchange Plc", "sector": "Financial Services", "total_shares": 23_826_120, "current_price": Decimal("6390.00")},
]

# ─── Historical Dividend Data ───────────────────────────────────────
# Sources: DSE corporate actions, annual reports, broker data

DIVIDENDS = [
    # TBL - Consistent high dividend payer
    {"symbol": "TBL", "year": "2020", "dps": Decimal("510.00"), "announced": date(2020, 5, 20), "closure": date(2020, 6, 10), "payment": date(2020, 6, 15), "type": "final", "status": "paid"},
    {"symbol": "TBL", "year": "2021", "dps": Decimal("580.00"), "announced": date(2021, 5, 19), "closure": date(2021, 6, 9), "payment": date(2021, 6, 14), "type": "final", "status": "paid"},
    {"symbol": "TBL", "year": "2022", "dps": Decimal("640.00"), "announced": date(2022, 5, 18), "closure": date(2022, 6, 8), "payment": date(2022, 6, 13), "type": "final", "status": "paid"},
    {"symbol": "TBL", "year": "2023", "dps": Decimal("700.00"), "announced": date(2023, 5, 17), "closure": date(2023, 6, 7), "payment": date(2023, 6, 12), "type": "final", "status": "paid"},
    {"symbol": "TBL", "year": "2024", "dps": Decimal("750.00"), "announced": date(2024, 5, 22), "closure": date(2024, 6, 12), "payment": date(2024, 6, 17), "type": "final", "status": "paid"},
    {"symbol": "TBL", "year": "2025", "dps": Decimal("818.00"), "announced": date(2025, 5, 21), "closure": date(2025, 6, 12), "payment": date(2025, 6, 16), "type": "final", "status": "paid"},

    # CRDB Bank
    {"symbol": "CRDB", "year": "2020", "dps": Decimal("15.00"), "announced": date(2020, 6, 15), "closure": date(2020, 7, 1), "payment": date(2020, 7, 15), "type": "final", "status": "paid"},
    {"symbol": "CRDB", "year": "2021", "dps": Decimal("25.00"), "announced": date(2021, 6, 14), "closure": date(2021, 7, 1), "payment": date(2021, 7, 14), "type": "final", "status": "paid"},
    {"symbol": "CRDB", "year": "2022", "dps": Decimal("40.00"), "announced": date(2022, 6, 13), "closure": date(2022, 7, 1), "payment": date(2022, 7, 13), "type": "final", "status": "paid"},
    {"symbol": "CRDB", "year": "2023", "dps": Decimal("55.00"), "announced": date(2023, 6, 12), "closure": date(2023, 7, 1), "payment": date(2023, 7, 12), "type": "final", "status": "paid"},
    {"symbol": "CRDB", "year": "2024", "dps": Decimal("75.00"), "announced": date(2024, 6, 10), "closure": date(2024, 7, 1), "payment": date(2024, 7, 10), "type": "final", "status": "paid"},

    # NMB Bank
    {"symbol": "NMB", "year": "2020", "dps": Decimal("200.00"), "announced": date(2020, 6, 20), "closure": date(2020, 7, 10), "payment": date(2020, 7, 20), "type": "final", "status": "paid"},
    {"symbol": "NMB", "year": "2021", "dps": Decimal("340.00"), "announced": date(2021, 6, 18), "closure": date(2021, 7, 8), "payment": date(2021, 7, 18), "type": "final", "status": "paid"},
    {"symbol": "NMB", "year": "2022", "dps": Decimal("475.00"), "announced": date(2022, 6, 17), "closure": date(2022, 7, 7), "payment": date(2022, 7, 17), "type": "final", "status": "paid"},
    {"symbol": "NMB", "year": "2023", "dps": Decimal("580.00"), "announced": date(2023, 6, 16), "closure": date(2023, 7, 6), "payment": date(2023, 7, 16), "type": "final", "status": "paid"},
    {"symbol": "NMB", "year": "2024", "dps": Decimal("730.00"), "announced": date(2024, 6, 14), "closure": date(2024, 7, 4), "payment": date(2024, 7, 14), "type": "final", "status": "paid"},

    # VODA - confirmed from DSE site
    {"symbol": "VODA", "year": "2022", "dps": Decimal("16.50"), "announced": date(2022, 7, 20), "closure": date(2022, 8, 12), "payment": date(2022, 10, 12), "type": "final", "status": "paid"},
    {"symbol": "VODA", "year": "2023", "dps": Decimal("18.00"), "announced": date(2023, 7, 21), "closure": date(2023, 8, 14), "payment": date(2023, 10, 14), "type": "final", "status": "paid"},
    {"symbol": "VODA", "year": "2024", "dps": Decimal("19.00"), "announced": date(2024, 7, 19), "closure": date(2024, 8, 12), "payment": date(2024, 10, 12), "type": "final", "status": "paid"},
    {"symbol": "VODA", "year": "2025", "dps": Decimal("20.20"), "announced": date(2025, 7, 22), "closure": date(2025, 8, 15), "payment": date(2025, 10, 15), "type": "final", "status": "paid"},

    # NICO - confirmed from DSE site
    {"symbol": "NICO", "year": "2023", "dps": Decimal("55.00"), "announced": date(2023, 9, 5), "closure": date(2023, 9, 28), "payment": date(2023, 11, 30), "type": "final", "status": "paid"},
    {"symbol": "NICO", "year": "2024", "dps": Decimal("62.00"), "announced": date(2024, 9, 3), "closure": date(2024, 9, 26), "payment": date(2024, 11, 28), "type": "final", "status": "paid"},
    {"symbol": "NICO", "year": "2025", "dps": Decimal("70.00"), "announced": date(2025, 9, 1), "closure": date(2025, 9, 24), "payment": date(2025, 11, 30), "type": "final", "status": "paid"},

    # AFRIPRISE - confirmed from DSE site
    {"symbol": "AFRIPRISE", "year": "2024", "dps": Decimal("15.00"), "announced": date(2024, 10, 20), "closure": date(2024, 11, 12), "payment": date(2024, 11, 15), "type": "final", "status": "paid"},
    {"symbol": "AFRIPRISE", "year": "2025", "dps": Decimal("18.00"), "announced": date(2025, 10, 23), "closure": date(2025, 11, 17), "payment": date(2025, 11, 20), "type": "final", "status": "paid"},

    # TCC - Tanzania Cigarette Company
    {"symbol": "TCC", "year": "2022", "dps": Decimal("480.00"), "announced": date(2022, 5, 25), "closure": date(2022, 6, 15), "payment": date(2022, 6, 20), "type": "final", "status": "paid"},
    {"symbol": "TCC", "year": "2023", "dps": Decimal("520.00"), "announced": date(2023, 5, 24), "closure": date(2023, 6, 14), "payment": date(2023, 6, 19), "type": "final", "status": "paid"},
    {"symbol": "TCC", "year": "2024", "dps": Decimal("550.00"), "announced": date(2024, 5, 23), "closure": date(2024, 6, 13), "payment": date(2024, 6, 18), "type": "final", "status": "paid"},

    # TPCC - Tanzania Portland Cement
    {"symbol": "TPCC", "year": "2022", "dps": Decimal("190.00"), "announced": date(2022, 6, 1), "closure": date(2022, 6, 22), "payment": date(2022, 7, 1), "type": "final", "status": "paid"},
    {"symbol": "TPCC", "year": "2023", "dps": Decimal("210.00"), "announced": date(2023, 5, 31), "closure": date(2023, 6, 21), "payment": date(2023, 6, 30), "type": "final", "status": "paid"},
    {"symbol": "TPCC", "year": "2024", "dps": Decimal("230.00"), "announced": date(2024, 5, 30), "closure": date(2024, 6, 20), "payment": date(2024, 6, 28), "type": "final", "status": "paid"},

    # SWIS - Swissport
    {"symbol": "SWIS", "year": "2022", "dps": Decimal("100.00"), "announced": date(2022, 6, 10), "closure": date(2022, 7, 1), "payment": date(2022, 7, 10), "type": "final", "status": "paid"},
    {"symbol": "SWIS", "year": "2023", "dps": Decimal("120.00"), "announced": date(2023, 6, 9), "closure": date(2023, 6, 30), "payment": date(2023, 7, 9), "type": "final", "status": "paid"},
    {"symbol": "SWIS", "year": "2024", "dps": Decimal("140.00"), "announced": date(2024, 6, 7), "closure": date(2024, 6, 28), "payment": date(2024, 7, 7), "type": "final", "status": "paid"},

    # DCB Bank
    {"symbol": "DCB", "year": "2023", "dps": Decimal("8.00"), "announced": date(2023, 6, 20), "closure": date(2023, 7, 10), "payment": date(2023, 7, 20), "type": "final", "status": "paid"},
    {"symbol": "DCB", "year": "2024", "dps": Decimal("12.00"), "announced": date(2024, 6, 18), "closure": date(2024, 7, 8), "payment": date(2024, 7, 18), "type": "final", "status": "paid"},

    # DSE (the exchange itself)
    {"symbol": "DSE", "year": "2023", "dps": Decimal("100.00"), "announced": date(2023, 9, 15), "closure": date(2023, 10, 5), "payment": date(2023, 10, 15), "type": "final", "status": "paid"},
    {"symbol": "DSE", "year": "2024", "dps": Decimal("120.00"), "announced": date(2024, 9, 13), "closure": date(2024, 10, 3), "payment": date(2024, 10, 13), "type": "final", "status": "paid"},

    # TOL - Tanzania Oxygen
    {"symbol": "TOL", "year": "2023", "dps": Decimal("45.00"), "announced": date(2023, 8, 10), "closure": date(2023, 8, 30), "payment": date(2023, 9, 10), "type": "final", "status": "paid"},
    {"symbol": "TOL", "year": "2024", "dps": Decimal("50.00"), "announced": date(2024, 8, 8), "closure": date(2024, 8, 28), "payment": date(2024, 9, 8), "type": "final", "status": "paid"},
]


def seed():
    db = SessionLocal()

    # Clear existing data
    db.query(Dividend).delete()
    db.query(Company).delete()
    db.commit()

    # Insert companies
    company_map = {}
    for c in COMPANIES:
        company = Company(**c)
        db.add(company)
        db.flush()
        company_map[c["symbol"]] = company.id

    # Insert dividends
    for d in DIVIDENDS:
        company_id = company_map.get(d["symbol"])
        if not company_id:
            print(f"WARNING: Company {d['symbol']} not found, skipping dividend")
            continue

        dividend = Dividend(
            company_id=company_id,
            financial_year=d["year"],
            dividend_per_share=d["dps"],
            announcement_date=d["announced"],
            books_closure_date=d["closure"],
            payment_date=d["payment"],
            dividend_type=d["type"],
            status=d["status"],
        )
        db.add(dividend)

    db.commit()
    db.close()

    print(f"Seeded {len(COMPANIES)} companies and {len(DIVIDENDS)} dividend records.")


if __name__ == "__main__":
    seed()
