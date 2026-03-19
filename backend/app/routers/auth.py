"""
Auth routes — register and login via phone + password.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.services.auth_service import create_access_token, hash_password, verify_password

logger = logging.getLogger("dse.auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ─── Request / response schemas ───────────────────────────────────

class RegisterRequest(BaseModel):
    phone: str
    name: str = ""
    password: str

    @field_validator("phone")
    @classmethod
    def phone_not_empty(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 9:
            raise ValueError("Phone number must be at least 9 characters")
        return v

    @field_validator("password")
    @classmethod
    def password_strong_enough(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    phone: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    phone: str
    name: str


# ─── Routes ───────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with phone + password."""
    existing = db.query(User).filter(User.phone == req.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already registered",
        )

    user = User(
        phone=req.phone,
        name=req.name,
        password_hash=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.phone)
    logger.info("New user registered: id=%s phone=%s***", user.id, user.phone[:6])

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        phone=user.phone,
        name=user.name or "",
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Login with phone + password, returns JWT."""
    user = db.query(User).filter(User.phone == req.phone).first()
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password",
        )

    if not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password",
        )

    token = create_access_token(user.id, user.phone)
    logger.info("User login: id=%s", user.id)

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        phone=user.phone,
        name=user.name or "",
    )


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return {
        "id": current_user.id,
        "phone": current_user.phone,
        "name": current_user.name,
        "email": current_user.email,
    }
