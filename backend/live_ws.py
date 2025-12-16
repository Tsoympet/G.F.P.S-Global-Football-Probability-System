import asyncio
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from .live_state import live_state

router = APIRouter()


@router.websocket("/ws/live-matches")
async def live_matches_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    queue = await live_state.subscribe()
    try:
        await websocket.send_json({"type": "snapshot", **live_state.snapshot()})
        while True:
            try:
                payload: Any = await asyncio.wait_for(queue.get(), timeout=15)
            except asyncio.TimeoutError:
                payload = {"type": "heartbeat", **live_state.snapshot()}
            await websocket.send_json(payload)
    except WebSocketDisconnect:
        pass
    finally:
        await live_state.unsubscribe(queue)
