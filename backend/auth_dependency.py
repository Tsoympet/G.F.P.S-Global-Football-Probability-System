from typing import Generator

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from .auth_utils import decode_token
from .db import SessionLocal
from .models import User


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_from_token(token: str, db: Session) -> User:
    if not token:
        raise HTTPException(401, "Missing token")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")

    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "User not found")

    if not user.is_active:
        raise HTTPException(403, "Account disabled")

    if user.token_version != payload.get("tv"):
        raise HTTPException(401, "Token expired")

    return user


def require_user(
    authorization: str = Header(None), db: Session = Depends(get_db)
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header")

    token = authorization.split(" ", 1)[1]
    return get_user_from_token(token, db)
