from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, constr
from typing import Literal
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import SessionLocal
from .models import User, Device
from .auth_dependency import require_user

router = APIRouter(prefix="/devices", tags=["devices"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DeviceIn(BaseModel):
    platform: Literal["android", "ios", "web"]
    push_token: constr(min_length=8, pattern=r"^[A-Za-z0-9:_\-.]+$")


@router.post("/register")
def register_device(p: DeviceIn, user: User = Depends(require_user), db: Session = Depends(get_db)):
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
def list_devices(user: User = Depends(require_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Device).where(Device.user_id == user.id)).all()
    return {
        "ok": True,
        "items": [
            {"id": r.id, "platform": r.platform, "token": r.token, "created_at": str(r.created_at)}
            for r in rows
        ],
    }


@router.delete("/{device_id}")
def delete_device(device_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    d = db.scalar(select(Device).where(Device.id == device_id, Device.user_id == user.id))
    if not d:
        raise HTTPException(404, "Not found")
    db.delete(d)
    db.commit()
    return {"ok": True}
