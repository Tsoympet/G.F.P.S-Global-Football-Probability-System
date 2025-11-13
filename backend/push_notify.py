import os
from typing import List, Optional

import httpx

FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY", "")


async def send_fcm_push(tokens: List[str], title: str, body: str, data: Optional[dict] = None) -> bool:
    if not FCM_SERVER_KEY or not tokens:
        return False

    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "registration_ids": tokens,
        "notification": {
            "title": title,
            "body": body,
        },
        "data": data or {},
    }

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            return True
        except Exception as e:
            print("[FCM ERROR]", e)
            return False
