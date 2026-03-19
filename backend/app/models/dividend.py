from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Dividend(Base):
    __tablename__ = "dividends"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    financial_year = Column(String(10), nullable=False)
    dividend_per_share = Column(Numeric(10, 2), nullable=False)
    announcement_date = Column(Date)
    books_closure_date = Column(Date)
    payment_date = Column(Date)
    dividend_type = Column(String(20), default="final")  # interim, final, special
    status = Column(String(20), default="announced")  # announced, books_closed, paid
    source_url = Column(Text)

    company = relationship("Company", back_populates="dividends")
