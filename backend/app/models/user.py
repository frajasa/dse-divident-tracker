from sqlalchemy import Boolean, Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(200))
    name = Column(String(200))
    password_hash = Column(String(200))

    holdings = relationship("UserHolding", back_populates="user")
    tax_profile = relationship("UserTaxProfile", back_populates="user", uselist=False)
    alert_preferences = relationship("AlertPreference", back_populates="user")


class UserHolding(Base):
    __tablename__ = "user_holdings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    shares_held = Column(Integer, nullable=False)
    purchase_price = Column(Numeric(12, 2))
    purchase_date = Column(Date)

    user = relationship("User", back_populates="holdings")
    company = relationship("Company")


class UserTaxProfile(Base):
    __tablename__ = "user_tax_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    residency_status = Column(String(20), default="resident")  # resident, non_resident
    country_of_residence = Column(String(50), default="Tanzania")
    investor_type = Column(String(20), default="individual")  # individual, company, fund

    user = relationship("User", back_populates="tax_profile")


class AlertPreference(Base):
    __tablename__ = "alert_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    alert_type = Column(String(30), nullable=False)  # pre_closure, declared, payment, yield_opportunity
    channel = Column(String(20), default="whatsapp")  # sms, whatsapp, email
    days_before = Column(Integer, default=7)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="alert_preferences")
    company = relationship("Company")
