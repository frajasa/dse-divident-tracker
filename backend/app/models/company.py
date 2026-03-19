from sqlalchemy import Column, Integer, String, BigInteger, Numeric
from sqlalchemy.orm import relationship

from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    sector = Column(String(50))
    total_shares = Column(BigInteger)
    current_price = Column(Numeric(12, 2))

    dividends = relationship("Dividend", back_populates="company")
