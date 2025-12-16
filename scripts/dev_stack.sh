#!/usr/bin/env bash
set -euo pipefail

# Simple helper to boot backend and desktop together for local smoke testing.

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)

cd "$ROOT_DIR"

echo "Starting backend on :8000"
python -m uvicorn backend.main:app --reload --port 8000 --host 0.0.0.0 &
BACKEND_PID=$!

cleanup() {
  echo "Stopping backend (pid: $BACKEND_PID)"
  kill "$BACKEND_PID" 2>/dev/null || true
}

trap cleanup EXIT

echo "Starting desktop (npm run dev)"
cd GFPS/desktop
npm install
npm run dev -- --host 0.0.0.0 --port 1420
