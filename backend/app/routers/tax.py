from decimal import Decimal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from app.services.tax_calculator import calculate_dividend_tax, calculate_portfolio_tax

router = APIRouter(prefix="/api/tax", tags=["tax"])


class SingleTaxRequest(BaseModel):
    shares: int
    dividend_per_share: float
    residency: str = "resident"  # resident | non_resident
    investor_type: str = "individual"  # individual | company
    country: str | None = None
    purchase_price: float | None = None

    @field_validator("shares")
    @classmethod
    def shares_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("shares must be positive")
        return v

    @field_validator("dividend_per_share")
    @classmethod
    def dps_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("dividend_per_share must be positive")
        return v

    @field_validator("residency")
    @classmethod
    def valid_residency(cls, v: str) -> str:
        if v not in ("resident", "non_resident"):
            raise ValueError("residency must be 'resident' or 'non_resident'")
        return v

    @field_validator("investor_type")
    @classmethod
    def valid_investor_type(cls, v: str) -> str:
        if v not in ("individual", "company"):
            raise ValueError("investor_type must be 'individual' or 'company'")
        return v


class HoldingInput(BaseModel):
    symbol: str
    company_name: str = ""
    shares: int
    dividend_per_share: float
    purchase_price: float | None = None


class PortfolioTaxRequest(BaseModel):
    holdings: list[HoldingInput]
    residency: str = "resident"
    investor_type: str = "individual"
    country: str | None = None


@router.post("/calculate")
def calculate_tax(req: SingleTaxRequest):
    """Calculate dividend tax for a single stock holding."""
    result = calculate_dividend_tax(
        shares=req.shares,
        dividend_per_share=Decimal(str(req.dividend_per_share)),
        residency=req.residency,
        investor_type=req.investor_type,
        country=req.country,
        purchase_price=Decimal(str(req.purchase_price)) if req.purchase_price else None,
    )
    return {
        "gross_dividend": str(result.gross_dividend),
        "tax_rate": str(result.tax_rate),
        "tax_amount": str(result.tax_amount),
        "net_dividend": str(result.net_dividend),
        "effective_yield": str(result.effective_yield),
        "dta_applied": result.dta_applied,
        "dta_country": result.dta_country,
    }


@router.post("/portfolio")
def calculate_portfolio(req: PortfolioTaxRequest):
    """Calculate dividend tax across an entire portfolio."""
    holdings = [
        {
            "symbol": h.symbol,
            "company_name": h.company_name,
            "shares": h.shares,
            "dividend_per_share": Decimal(str(h.dividend_per_share)),
            "purchase_price": Decimal(str(h.purchase_price)) if h.purchase_price else None,
        }
        for h in req.holdings
    ]
    return calculate_portfolio_tax(
        holdings=holdings,
        residency=req.residency,
        investor_type=req.investor_type,
        country=req.country,
    )
