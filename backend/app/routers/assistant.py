from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.assistant_service import process_question
from app.services.auth_service import decode_access_token

router = APIRouter(prefix="/api/assistant", tags=["assistant"])
optional_auth = HTTPBearer(auto_error=False)


class AskRequest(BaseModel):
    question: str


def _get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_auth),
    db: Session = Depends(get_db),
) -> User | None:
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload:
        return None
    user_id = int(payload["sub"])
    return db.query(User).filter(User.id == user_id).first()


@router.post("/ask")
def ask_assistant(
    req: AskRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(_get_optional_user),
):
    user_id = current_user.id if current_user else None
    return process_question(db, req.question, user_id=user_id)
