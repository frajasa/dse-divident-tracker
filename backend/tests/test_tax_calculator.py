"""Tests for the DSE dividend tax calculator."""

from decimal import Decimal

import pytest

from app.services.tax_calculator import (
    DTA_RATES,
    TAX_RATES,
    calculate_dividend_tax,
    calculate_portfolio_tax,
)


# ─── Single holding tax tests ─────────────────────────────────────

class TestCalculateDividendTax:
    def test_resident_individual_10_percent(self):
        result = calculate_dividend_tax(
            shares=1000,
            dividend_per_share=Decimal("500"),
            residency="resident",
            investor_type="individual",
        )
        assert result.gross_dividend == Decimal("500000")
        assert result.tax_rate == Decimal("0.10")
        assert result.tax_amount == Decimal("50000.00")
        assert result.net_dividend == Decimal("450000.00")
        assert result.dta_applied is False

    def test_resident_company_10_percent(self):
        result = calculate_dividend_tax(
            shares=5000,
            dividend_per_share=Decimal("818"),
            residency="resident",
            investor_type="company",
        )
        assert result.gross_dividend == Decimal("4090000")
        assert result.tax_rate == Decimal("0.10")
        assert result.tax_amount == Decimal("409000.00")
        assert result.net_dividend == Decimal("3681000.00")

    def test_non_resident_individual_15_percent(self):
        result = calculate_dividend_tax(
            shares=1000,
            dividend_per_share=Decimal("500"),
            residency="non_resident",
            investor_type="individual",
        )
        assert result.tax_rate == Decimal("0.15")
        assert result.tax_amount == Decimal("75000.00")
        assert result.net_dividend == Decimal("425000.00")

    def test_non_resident_company_15_percent(self):
        result = calculate_dividend_tax(
            shares=2000,
            dividend_per_share=Decimal("200"),
            residency="non_resident",
            investor_type="company",
        )
        assert result.tax_rate == Decimal("0.15")
        assert result.tax_amount == Decimal("60000.00")

    def test_dta_india_reduces_to_10_percent(self):
        result = calculate_dividend_tax(
            shares=1000,
            dividend_per_share=Decimal("500"),
            residency="non_resident",
            investor_type="individual",
            country="India",
        )
        assert result.tax_rate == Decimal("0.10")
        assert result.dta_applied is True
        assert result.dta_country == "India"
        assert result.tax_amount == Decimal("50000.00")

    def test_dta_canada_stays_at_15_percent(self):
        """Canada DTA rate is 15% — same as non-resident, so no reduction."""
        result = calculate_dividend_tax(
            shares=1000,
            dividend_per_share=Decimal("500"),
            residency="non_resident",
            investor_type="individual",
            country="Canada",
        )
        # Canada DTA is 15%, same as base — no DTA benefit
        assert result.tax_rate == Decimal("0.15")
        assert result.dta_applied is False

    def test_dta_not_applied_for_residents(self):
        result = calculate_dividend_tax(
            shares=1000,
            dividend_per_share=Decimal("500"),
            residency="resident",
            investor_type="individual",
            country="India",
        )
        assert result.tax_rate == Decimal("0.10")
        assert result.dta_applied is False

    def test_dta_unknown_country_no_reduction(self):
        result = calculate_dividend_tax(
            shares=1000,
            dividend_per_share=Decimal("500"),
            residency="non_resident",
            investor_type="individual",
            country="Australia",
        )
        assert result.tax_rate == Decimal("0.15")
        assert result.dta_applied is False

    def test_effective_yield_with_purchase_price(self):
        result = calculate_dividend_tax(
            shares=1000,
            dividend_per_share=Decimal("500"),
            residency="resident",
            investor_type="individual",
            purchase_price=Decimal("5000"),
        )
        # Net = 450,000; Investment = 1000 * 5000 = 5,000,000
        # Yield = 450,000 / 5,000,000 * 100 = 9.00%
        assert result.effective_yield == Decimal("9.00")

    def test_effective_yield_zero_without_purchase_price(self):
        result = calculate_dividend_tax(
            shares=1000,
            dividend_per_share=Decimal("500"),
            residency="resident",
        )
        assert result.effective_yield == Decimal("0")

    def test_unknown_residency_defaults_to_15_percent(self):
        result = calculate_dividend_tax(
            shares=100,
            dividend_per_share=Decimal("100"),
            residency="unknown",
            investor_type="unknown",
        )
        assert result.tax_rate == Decimal("0.15")

    def test_single_share(self):
        result = calculate_dividend_tax(
            shares=1,
            dividend_per_share=Decimal("100.50"),
            residency="resident",
        )
        assert result.gross_dividend == Decimal("100.50")
        assert result.tax_amount == Decimal("10.05")
        assert result.net_dividend == Decimal("90.45")


# ─── Portfolio tax tests ──────────────────────────────────────────

class TestCalculatePortfolioTax:
    def test_single_holding_portfolio(self):
        holdings = [
            {
                "symbol": "TBL",
                "company_name": "Tanzania Breweries",
                "shares": 1000,
                "dividend_per_share": Decimal("818"),
                "purchase_price": Decimal("9000"),
            }
        ]
        result = calculate_portfolio_tax(holdings, residency="resident")

        assert len(result["holdings"]) == 1
        assert result["summary"]["total_gross_dividend"] == "818000"
        assert result["summary"]["total_tax"] == "81800.00"
        assert result["summary"]["total_net_dividend"] == "736200.00"

    def test_multi_holding_portfolio(self):
        holdings = [
            {
                "symbol": "TBL",
                "shares": 1000,
                "dividend_per_share": Decimal("500"),
                "purchase_price": Decimal("5000"),
            },
            {
                "symbol": "CRDB",
                "shares": 2000,
                "dividend_per_share": Decimal("100"),
                "purchase_price": Decimal("500"),
            },
        ]
        result = calculate_portfolio_tax(holdings, residency="resident")

        total_gross = Decimal(result["summary"]["total_gross_dividend"])
        assert total_gross == Decimal("700000")  # 500k + 200k

        total_tax = Decimal(result["summary"]["total_tax"])
        assert total_tax == Decimal("70000.00")  # 10%

    def test_portfolio_yield_calculation(self):
        holdings = [
            {
                "symbol": "TBL",
                "shares": 1000,
                "dividend_per_share": Decimal("500"),
                "purchase_price": Decimal("5000"),
            },
        ]
        result = calculate_portfolio_tax(holdings, residency="resident")

        # Net = 450,000; Invested = 5,000,000; Yield = 9.00%
        assert result["summary"]["portfolio_yield"] == "9.00"

    def test_empty_portfolio(self):
        result = calculate_portfolio_tax([], residency="resident")
        assert result["holdings"] == []
        assert result["summary"]["total_gross_dividend"] == "0"
        assert result["summary"]["portfolio_yield"] == "0"


# ─── Tax rates sanity checks ─────────────────────────────────────

class TestTaxRatesConfig:
    def test_all_resident_rates_are_10_percent(self):
        assert TAX_RATES[("resident", "individual")] == Decimal("0.10")
        assert TAX_RATES[("resident", "company")] == Decimal("0.10")

    def test_all_non_resident_rates_are_15_percent(self):
        assert TAX_RATES[("non_resident", "individual")] == Decimal("0.15")
        assert TAX_RATES[("non_resident", "company")] == Decimal("0.15")

    def test_dta_rates_not_higher_than_base(self):
        """No DTA rate should exceed the non-resident base rate of 15%."""
        for country, rate in DTA_RATES.items():
            assert rate <= Decimal("0.15"), f"DTA rate for {country} exceeds 15%"

    def test_south_africa_dta_is_10_percent(self):
        assert DTA_RATES["South Africa"] == Decimal("0.10")
