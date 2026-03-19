"""
DSE Dividend Tax Calculator

Tanzania tax rules for dividend income:
- Resident individuals: 10% withholding tax (final)
- Resident companies: 10% withholding tax
- Non-resident individuals: 15% withholding tax (final)
- Non-resident companies: 15% withholding tax

Double Taxation Agreements (DTAs) may reduce non-resident rates.
Tanzania has DTAs with: Canada, Denmark, Finland, India, Italy, Norway,
South Africa, Sweden, Zambia, and others.

References:
- Income Tax Act, 2004 (Tanzania)
- CMSA regulations
"""

from dataclasses import dataclass
from decimal import Decimal

# Withholding tax rates
TAX_RATES = {
    ("resident", "individual"): Decimal("0.10"),
    ("resident", "company"): Decimal("0.10"),
    ("non_resident", "individual"): Decimal("0.15"),
    ("non_resident", "company"): Decimal("0.15"),
}

# DTA reduced rates (country -> max withholding rate on dividends)
DTA_RATES: dict[str, Decimal] = {
    "Canada": Decimal("0.15"),
    "Denmark": Decimal("0.15"),
    "Finland": Decimal("0.15"),
    "India": Decimal("0.10"),
    "Italy": Decimal("0.15"),
    "Norway": Decimal("0.15"),
    "South Africa": Decimal("0.10"),
    "Sweden": Decimal("0.15"),
    "Zambia": Decimal("0.15"),
}


@dataclass
class TaxResult:
    gross_dividend: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    net_dividend: Decimal
    effective_yield: Decimal  # net dividend / investment cost
    dta_applied: bool
    dta_country: str | None


def calculate_dividend_tax(
    shares: int,
    dividend_per_share: Decimal,
    residency: str = "resident",
    investor_type: str = "individual",
    country: str | None = None,
    purchase_price: Decimal | None = None,
) -> TaxResult:
    """
    Calculate dividend tax for a DSE stock holding.

    Args:
        shares: Number of shares held
        dividend_per_share: Dividend declared per share (TZS)
        residency: 'resident' or 'non_resident'
        investor_type: 'individual' or 'company'
        country: Country of residence (for DTA lookup)
        purchase_price: Price per share when bought (for yield calculation)
    """
    gross = Decimal(shares) * dividend_per_share

    # Determine base tax rate
    tax_rate = TAX_RATES.get(
        (residency, investor_type), Decimal("0.15")
    )

    # Check for DTA reduction (only for non-residents)
    dta_applied = False
    dta_country = None
    if residency == "non_resident" and country and country in DTA_RATES:
        dta_rate = DTA_RATES[country]
        if dta_rate < tax_rate:
            tax_rate = dta_rate
            dta_applied = True
            dta_country = country

    tax_amount = (gross * tax_rate).quantize(Decimal("0.01"))
    net_dividend = gross - tax_amount

    # Calculate effective yield if purchase price is known
    if purchase_price and purchase_price > 0:
        investment_cost = Decimal(shares) * purchase_price
        effective_yield = (net_dividend / investment_cost * 100).quantize(
            Decimal("0.01")
        )
    else:
        effective_yield = Decimal("0")

    return TaxResult(
        gross_dividend=gross,
        tax_rate=tax_rate,
        tax_amount=tax_amount,
        net_dividend=net_dividend,
        effective_yield=effective_yield,
        dta_applied=dta_applied,
        dta_country=dta_country,
    )


def calculate_portfolio_tax(
    holdings: list[dict],
    residency: str = "resident",
    investor_type: str = "individual",
    country: str | None = None,
) -> dict:
    """
    Calculate total dividend tax across a portfolio.

    Args:
        holdings: List of dicts with keys:
            - shares: int
            - dividend_per_share: Decimal
            - purchase_price: Decimal (optional)
            - symbol: str
            - company_name: str
    """
    results = []
    total_gross = Decimal("0")
    total_tax = Decimal("0")
    total_net = Decimal("0")
    total_invested = Decimal("0")

    for h in holdings:
        result = calculate_dividend_tax(
            shares=h["shares"],
            dividend_per_share=h["dividend_per_share"],
            residency=residency,
            investor_type=investor_type,
            country=country,
            purchase_price=h.get("purchase_price"),
        )

        invested = Decimal(h["shares"]) * h.get("purchase_price", Decimal("0"))
        total_invested += invested
        total_gross += result.gross_dividend
        total_tax += result.tax_amount
        total_net += result.net_dividend

        results.append(
            {
                "symbol": h["symbol"],
                "company_name": h.get("company_name", ""),
                "shares": h["shares"],
                "dividend_per_share": str(h["dividend_per_share"]),
                "gross_dividend": str(result.gross_dividend),
                "tax_rate": str(result.tax_rate),
                "tax_amount": str(result.tax_amount),
                "net_dividend": str(result.net_dividend),
                "effective_yield": str(result.effective_yield),
            }
        )

    portfolio_yield = Decimal("0")
    if total_invested > 0:
        portfolio_yield = (total_net / total_invested * 100).quantize(Decimal("0.01"))

    return {
        "holdings": results,
        "summary": {
            "total_gross_dividend": str(total_gross),
            "total_tax": str(total_tax),
            "total_net_dividend": str(total_net),
            "total_invested": str(total_invested),
            "portfolio_yield": str(portfolio_yield),
            "tax_rate_applied": str(
                TAX_RATES.get((residency, investor_type), Decimal("0.15"))
            ),
            "residency": residency,
            "investor_type": investor_type,
        },
    }
