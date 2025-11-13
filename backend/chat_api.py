from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import SessionLocal
from .models import ChatRoom, ChatMessage, User
from .auth_utils import decode_token

router = APIRouter(prefix="/chat", tags=["chat"])


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


@router.get("/rooms")
def list_rooms(db: Session = Depends(get_db)):
    rooms = db.scalars(select(ChatRoom)).all()
    return {
        "ok": True,
        "rooms": [{"id": r.id, "key": r.key, "title": r.title} for r in rooms],
    }


@router.get("/history")
def room_history(token: str, room: str, limit: int = 50, db: Session = Depends(get_db)):
    user = get_user(token, db)
    r = db.scalar(select(ChatRoom).where(ChatRoom.key == room))
    if not r:
        return {"ok": True, "messages": []}

    msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.room_id == r.id)
        .order_by(ChatMessage.id.desc())
        .limit(limit)
        .all()
    )

    return {
        "ok": True,
        "messages": [
            {
                "user_id": m.user_id,
                "content": m.content,
                "ts": str(m.created_at),
            }
            for m in msgs
        ],
    }
