import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.schemas import LoginIn, TokenOut, UserOut
from app.security import check_password, current_user, issue_token

router = APIRouter(tags=["auth"])
log = logging.getLogger(__name__)


@router.post("/auth/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if user is None or not check_password(data.password, user.password_hash):
        log.warning("failed login")  # never log the e-mail or password
        raise HTTPException(401, "Wrong email or password.")  # never say which
    return TokenOut(token=issue_token(db, user), name=user.name, role=user.role)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)) -> User:
    return user
