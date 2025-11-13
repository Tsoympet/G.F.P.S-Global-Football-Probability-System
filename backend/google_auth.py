import os
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import select

from google.oauth2 import id_token
from google.auth.transport import requests as g_requests

from .db import SessionLocal
from .models import User
from .auth_utils import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Signup(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None


class Login(BaseModel):
    email: EmailStr
    password: str


class GoogleLogin(BaseModel):
    id_token: str


@router.post("/signup")
def signup(p: Signup, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == p.email))
    if existing:
        raise HTTPException(400, "Email already registered")

    u = User(
        email=p.email,
        password_hash=hash_password(p.password),
        display_name=p.display_name or p.email.split("@")[0],
        role="free",
        is_active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)

    token = create_token(u.email, u.token_version, u.role)
    return {
        "ok": True,
        "token": token,
        "profile": {
            "email": u.email,
            "display_name": u.display_name,
            "avatar_url": u.avatar_url,
            "role": u.role,
        },
        "provider": "local",
    }


@router.post("/login")
def login(p: Login, db: Session = Depends(get_db)):
    u = db.scalar(select(User).where(User.email == p.email))
    if not u or not verify_password(p.password, u.password_hash):
        raise HTTPException(401, "Invalid credentials")

    if not u.is_active:
        raise HTTPException(403, "Account disabled")

    token = create_token(u.email, u.token_version, u.role)
    return {
        "ok": True,
        "token": token,
        "profile": {
            "email": u.email,
            "display_name": u.display_name,
            "avatar_url": u.avatar_url,
            "role": u.role,
        },
        "provider": "local",
    }


def verify_google_id_token(google_id_token: str) -> dict:
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(500, "GOOGLE_CLIENT_ID not configured")

    try:
        payload = id_token.verify_oauth2_token(
            google_id_token,
            g_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
        if payload.get("aud") != GOOGLE_CLIENT_ID:
            raise HTTPException(401, "Invalid audience")
        if not payload.get("email_verified", False):
            raise HTTPException(401, "Email not verified by Google")
        return payload
    except Exception as e:
        raise HTTPException(401, f"Invalid Google token: {e}")


@router.post("/google")
def google_login(p: GoogleLogin, db: Session = Depends(get_db)):
    payload = verify_google_id_token(p.id_token)
    email = payload.get("email")
    if not email:
        raise HTTPException(400, "Google token missing email")

    name = payload.get("name") or email.split("@")[0]
    picture = payload.get("picture")

    u = db.scalar(select(User).where(User.email == email))
    if not u:
        rnd_pwd = secrets.token_hex(16)
        u = User(
            email=email,
            password_hash=hash_password(rnd_pwd),
            display_name=name,
            avatar_url=picture,
            role="free",
            is_active=True,
        )
        db.add(u)
        db.commit()
        db.refresh(u)

    token = create_token(u.email, u.token_version, u.role)
    return {
        "ok": True,
        "token": token,
        "profile": {
            "email": u.email,
            "display_name": u.display_name,
            "avatar_url": u.avatar_url,
            "role": u.role,
        },
        "provider": "google",
    }
