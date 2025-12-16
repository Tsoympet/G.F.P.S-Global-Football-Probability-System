#!/usr/bin/env bash
set -euo pipefail

BASE_URL=${1:-http://localhost:8000}

endpoints=(
  "/health"
  "/fixtures"
  "/live-odds"
  "/predictions"
  "/value-bets"
)

echo "Checking endpoints against ${BASE_URL}";

for path in "${endpoints[@]}"; do
  url="${BASE_URL}${path}"
  echo -n "- ${path}: "
  if curl -fsS --max-time 5 "$url" >/dev/null; then
    echo "ok"
  else
    echo "failed"
  fi
done
