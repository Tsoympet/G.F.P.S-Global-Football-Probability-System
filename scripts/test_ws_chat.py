"""
Test GFPS global chat WebSocket from terminal.
"""

import asyncio
import websockets
import json

TOKEN = "PUT_YOUR_JWT_HERE"

async def main():
    url = f"ws://localhost:8000/ws/chat?token={TOKEN}"
    print("[GFPS] Connecting to:", url)

    async with websockets.connect(url) as ws:
        print("[GFPS] Connected. Sending test message...")
        await ws.send(json.dumps({
            "type": "chat_message",
            "room": "global",
            "text": "Test message from admin script",
            "author": "AdminScript",
            "ts": "now"
        }))
        print("Sent. Listening...")

        while True:
            msg = await ws.recv()
            print("[CHAT]", msg)

if __name__ == "__main__":
    asyncio.run(main())
