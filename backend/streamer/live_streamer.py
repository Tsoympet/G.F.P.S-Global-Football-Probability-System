import asyncio
import os

from ..live_state import live_state


STREAMER_ENABLED = os.getenv("STREAMER_ENABLED", "false").lower() in ("1", "true", "yes")
STREAMER_INTERVAL_SEC = int(os.getenv("STREAMER_INTERVAL_SEC", "15"))


async def live_streamer_loop():
    if not STREAMER_ENABLED:
        print("[streamer] Disabled via STREAMER_ENABLED")
        return

    print("[streamer] Live streamer started")
    while True:
        try:
            await live_state.tick_demo_clock()
        except Exception as e:
            print("[streamer] ERROR:", e)
        await asyncio.sleep(STREAMER_INTERVAL_SEC)


def start_streamer_background(loop: asyncio.AbstractEventLoop):
    if not STREAMER_ENABLED:
        return
    loop.create_task(live_streamer_loop())
