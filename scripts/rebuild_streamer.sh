#!/bin/bash
echo "[GFPS] Restarting live streamer engine..."
docker compose restart backend
sleep 2
echo "[GFPS] Streamer reloaded."
