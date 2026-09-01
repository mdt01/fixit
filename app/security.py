"""Passwords, login tokens and role checks."""

import hashlib
import hmac
import logging
import secrets
from collections.abc import Callable
from datetime import timedelta

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import TOKEN_HOURS
from app.db import get_db
from app.models import User
from app.rules import Role, utcnow

log = logging.getLogger(__name__)


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${salt.hex()}${digest.hex()}"


def check_password(password: str, stored: str) -> bool:
    _, salt, _digest = stored.split("$")
    return hmac.compare_digest(hash_password(password, bytes.fromhex(salt)), stored)


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def issue_token(db: Session, user: User) -> str:
    """Create a new login token. Only its hash is stored, like a password."""
    token = secrets.token_urlsafe(32)
    user.token_hash = token_digest(token)
    user.token_expires = utcnow() + timedelta(hours=TOKEN_HOURS)
    db.commit()
    return token


def current_user(authorization: str = Header(default=""), db: Session = Depends(get_db)) -> User:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(401, "Log in first: send 'Authorization: Bearer <token>'.")
    user = db.scalar(select(User).where(User.token_hash == token_digest(token)))
    if user is None or user.token_expires is None or user.token_expires < utcnow():
        log.warning("rejected request with an invalid or expired token")
        raise HTTPException(401, "Your login has expired or is invalid. Log in again.")
    return user


def require(*roles: Role) -> Callable[..., User]:
    """Dependency factory: allow only users with one of `roles`."""

    def checker(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            log.warning("user %s (%s) refused: needs %s", user.id, user.role, roles)
            raise HTTPException(403, f"This action needs one of: {', '.join(roles)}.")
        return user

    return checker
