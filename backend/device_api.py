from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import SessionLocal
from .models import User, Device
from .auth_utils import decode_token

router = APIRouter(prefix="/devices", tags=["devices"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(token: str, db: Session) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")
    email = payload.get("sub")
    u = db.scalar(select(User).where(User.email == email))
    if not u:
        raise HTTPException(404, "User not found")
    return u


class DeviceIn(BaseModel):
    token: str
    platform: str  # android / ios / web
    push_token: str


@router.post("/register")
def register_device(p: DeviceIn, db: Session = Depends(get_db)):
    user = get_user(p.token, db)
    d = db.scalar(
        select(Device).where(
            Device.user_id == user.id,
            Device.token == p.push_token,
            Device.platform == p.platform,
        )
    )
    if not d:
        d = Device(
            user_id=user.id,
            platform=p.platform,
            token=p.push_token,
        )
        db.add(d)
        db.commit()
        db.refresh(d)
    return {"ok": True, "id": d.id}


@router.get("")
def list_devices(token: str, db: Session = Depends(get_db)):
    user = get_user(token, db)
    rows = db.scalars(select(Device).where(Device.user_id == user.id)).all()
    return {
        "ok": True,
        "items": [
            {"id": r.id, "platform": r.platform, "token": r.token, "created_at": str(r.created_at)}
            for r in rows
        ],
    }


@router.delete("/{device_id}")
def delete_device(device_id: int, token: str, db: Session = Depends(get_db)):
    user = get_user(token, db)
    d = db.scalar(select(Device).where(Device.id == device_id, Device.user_id == user.id))
    if not d:
        raise HTTPException(404, "Not found")
    db.delete(d)
    db.commit()
    return {"ok": True}
