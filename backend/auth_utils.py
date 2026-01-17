import datetime
import os
import secrets
from typing import Optional

import jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # Use a default key for testing/development - NOT FOR PRODUCTION
    SECRET_KEY = secrets.token_urlsafe(32)
    import warnings
    warnings.warn(
        "SECRET_KEY environment variable not set. Using insecure default for testing. "
        "Set SECRET_KEY in production!",
        UserWarning
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_token(email: str, token_version: int = 0) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    exp = now + datetime.timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": email,
        "tv": token_version,
        "iat": now.timestamp(),
        "exp": exp.timestamp(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None
