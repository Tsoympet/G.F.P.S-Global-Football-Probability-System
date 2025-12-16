import os
import secrets
import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import select

from google.oauth2 import id_token
from google.auth.transport import requests as g_requests

import pyotp
import aiosmtplib

from .db import SessionLocal
from .models import User
from .auth_utils import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER or "no-reply@gfps.app")

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "https://example.com")

TOTP_ISSUER = "GFPS"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def get_user_by_email(email: str, db: Session) -> Optional[User]:
    return db.scalar(select(User).where(User.email == email))


def create_totp_secret() -> str:
    return pyotp.random_base32()


def build_totp_uri(secret: str, email: str) -> str:
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=TOTP_ISSUER)


def verify_totp(secret: str, code: str) -> bool:
    if not secret or not code:
        return False
    totp = pyotp.TOTP(secret)
    try:
        return totp.verify(code, valid_window=1)
    except Exception:
        return False


async def send_email(to_email: str, subject: str, body: str):
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        # Fallback: print to console if SMTP is not configured
        print("=== EMAIL (SIMULATED) ===")
        print("To:", to_email)
        print("Subject:", subject)
        print(body)
        print("=========================")
        return

    msg = f"From: {SMTP_FROM}\r\nTo: {to_email}\r\nSubject: {subject}\r\n\r\n{body}"

    await aiosmtplib.send(
        message=msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASS,
        start_tls=True,
    )


def get_user_from_token(token: str, db: Session) -> User:
    from .auth_utils import decode_token

    payload = decode_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")
    email = payload.get("sub")
    u = get_user_by_email(email, db)
    if not u:
        raise HTTPException(404, "User not found")
    return u


# -------------------------------------------------------------------
# Models
# -------------------------------------------------------------------

class Signup(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None


class Login(BaseModel):
    email: EmailStr
    password: str
    code: Optional[str] = None  # 2FA code if enabled


class GoogleLogin(BaseModel):
    id_token: str


class ResetRequest(BaseModel):
    email: EmailStr


class ResetConfirm(BaseModel):
    token: str
    new_password: str


class TwoFASetupRequest(BaseModel):
    token: str


class TwoFAEnable(BaseModel):
    token: str
    code: str


# -------------------------------------------------------------------
# Signup / Login
# -------------------------------------------------------------------

@router.post("/signup")
def signup(p: Signup, db: Session = Depends(get_db)):
    existing = get_user_by_email(p.email, db)
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
    u = get_user_by_email(p.email, db)
    if not u or not verify_password(p.password, u.password_hash):
        raise HTTPException(401, "Invalid credentials")

    if not u.is_active:
        raise HTTPException(403, "Account disabled")

    # If 2FA enabled, require TOTP code
    if u.totp_enabled:
        if not p.code or not verify_totp(u.totp_secret, p.code):
            raise HTTPException(401, "Invalid 2FA code")

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


# -------------------------------------------------------------------
# Google Login
# -------------------------------------------------------------------

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

    u = get_user_by_email(email, db)
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


# -------------------------------------------------------------------
# Password Reset
# -------------------------------------------------------------------

@router.post("/request-reset")
async def request_reset(p: ResetRequest, db: Session = Depends(get_db)):
    u = get_user_by_email(p.email, db)
    if not u:
        # Don't reveal if email exists
        return {"ok": True}

    token = secrets.token_urlsafe(32)
    exp = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    u.reset_token = token
    u.reset_token_exp = exp
    db.add(u)
    db.commit()

    reset_link = f"{FRONTEND_BASE_URL.rstrip('/')}/reset-password?token={token}"

    subject = "GFPS – Password Reset"
    body = (
        f"Hello,\n\n"
        f"You requested a password reset for your GFPS account.\n"
        f"Use the following link to set a new password (valid for 1 hour):\n\n"
        f"{reset_link}\n\n"
        f"If you did not request this, please ignore this email.\n"
    )

    await send_email(u.email, subject, body)
    return {"ok": True}


@router.post("/confirm-reset")
def confirm_reset(p: ResetConfirm, db: Session = Depends(get_db)):
    now = datetime.datetime.utcnow()
    u = db.scalar(select(User).where(User.reset_token == p.token))
    if not u or not u.reset_token_exp or u.reset_token_exp < now:
        raise HTTPException(400, "Invalid or expired reset token")

    u.password_hash = hash_password(p.new_password)
    u.reset_token = None
    u.reset_token_exp = None
    u.token_version += 1  # invalidate old JWTs

    db.add(u)
    db.commit()

    return {"ok": True}


# -------------------------------------------------------------------
# 2FA (TOTP)
# -------------------------------------------------------------------

@router.post("/2fa/setup")
def twofa_setup(p: TwoFASetupRequest, db: Session = Depends(get_db)):
    user = get_user_from_token(p.token, db)

    if not user.totp_secret:
        user.totp_secret = create_totp_secret()
        db.add(user)
        db.commit()
        db.refresh(user)

    uri = build_totp_uri(user.totp_secret, user.email)
    return {"ok": True, "secret": user.totp_secret, "otpauth_url": uri}


@router.post("/2fa/enable")
def twofa_enable(p: TwoFAEnable, db: Session = Depends(get_db)):
    user = get_user_from_token(p.token, db)

    if not user.totp_secret:
        raise HTTPException(400, "2FA not set up")

    if not verify_totp(user.totp_secret, p.code):
        raise HTTPException(400, "Invalid 2FA code")

    user.totp_enabled = True
    db.add(user)
    db.commit()

    return {"ok": True}


@router.post("/2fa/disable")
def twofa_disable(p: TwoFAEnable, db: Session = Depends(get_db)):
    user = get_user_from_token(p.token, db)

    if user.totp_enabled and not verify_totp(user.totp_secret, p.code):
        raise HTTPException(400, "Invalid 2FA code")

    user.totp_enabled = False
    user.totp_secret = None
    db.add(user)
    db.commit()

    return {"ok": True}


