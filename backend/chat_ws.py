from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import select
import json
import time

from .db import SessionLocal
from .models import ChatRoom, ChatMessage, User
from .auth_utils import decode_token

ROOMS: dict[str, list[WebSocket]] = {}


def get_room_list(room_key: str) -> list[WebSocket]:
    ROOMS.setdefault(room_key, [])
    return ROOMS[room_key]


async def chat_ws_handler(ws: WebSocket):
    room = ws.query_params.get("room")
    token = ws.query_params.get("token")

    await ws.accept()

    if not room or not token:
        await ws.close(code=4000)
        return

    payload = decode_token(token)
    if not payload:
        await ws.close(code=4001)
        return

    email = payload["sub"]

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        if not user:
            await ws.close(code=4002)
            return

    conns = get_room_list(room)
    conns.append(ws)

    try:
        while True:
            msg_text = await ws.receive_text()
            with SessionLocal() as db:
                r = db.scalar(select(ChatRoom).where(ChatRoom.key == room))
                if not r:
                    r = ChatRoom(key=room, title=room)
                    db.add(r)
                    db.commit()
                    db.refresh(r)

                m = ChatMessage(
                    room_id=r.id,
                    user_id=user.id,
                    content=msg_text,
                )
                db.add(m)
                db.commit()

            payload_out = json.dumps(
                {
                    "user": user.display_name or user.email,
                    "content": msg_text,
                    "ts": time.time(),
                }
            )

            for s in list(conns):
                try:
                    await s.send_text(payload_out)
                except Exception:
                    pass

    except WebSocketDisconnect:
        if ws in conns:
            conns.remove(ws)
