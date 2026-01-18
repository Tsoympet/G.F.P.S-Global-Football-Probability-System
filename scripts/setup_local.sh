#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

if ! command -v python >/dev/null 2>&1; then
  echo "Python is required but was not found in PATH." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required but was not found in PATH." >&2
  exit 1
fi

if [ ! -d ".venv" ]; then
  python -m venv .venv
fi

VENV_PY="$ROOT_DIR/.venv/bin/python"
VENV_PIP="$ROOT_DIR/.venv/bin/pip"

REQ_FILE="backend/requirements.txt"
if [ -f "backend/requirements.lock" ] && rg -q "^[^#\\s]" backend/requirements.lock; then
  REQ_FILE="backend/requirements.lock"
fi

"$VENV_PIP" install -r "$REQ_FILE"

if [ ! -f ".env" ]; then
  cp .env.example .env
fi

"$VENV_PY" - <<'PY'
from pathlib import Path
import secrets

env_path = Path(".env")
lines = env_path.read_text().splitlines()

def set_key(key: str, value: str, replace_if):
    for idx, line in enumerate(lines):
        if line.startswith(f"{key}="):
            current = line.split("=", 1)[1]
            if replace_if(current):
                lines[idx] = f"{key}={value}"
            return
    lines.append(f"{key}={value}")

set_key("SECRET_KEY", secrets.token_hex(32), lambda v: not v.strip())
set_key(
    "FRONTEND_BASE_URL",
    "http://localhost:1420",
    lambda v: not v.strip() or v.strip() == "https://example.com",
)

env_path.write_text("\n".join(lines) + "\n")
PY

if [ "${INSTALL_PLAYWRIGHT:-0}" = "1" ]; then
  "$VENV_PY" -m playwright install
fi

(
  cd GFPS/desktop
  npm install
)

echo "Local setup complete."
if [ "${INSTALL_PLAYWRIGHT:-0}" = "1" ]; then
  echo "Playwright browsers installed."
else
  echo "Optional: run 'INSTALL_PLAYWRIGHT=1 ./scripts/setup_local.sh' if you need the web scraper."
fi
