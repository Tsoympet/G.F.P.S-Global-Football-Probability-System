"""
Fetch fixtures from API-Football and save them to DB.
"""

import requests
from backend.db import SessionLocal
from backend.models import Fixture
from backend.config import API_FOOTBALL_KEY

API_URL = "https://v3.football.api-sports.io/fixtures"

HEADERS = {
    "x-rapidapi-key": API_FOOTBALL_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io"
}

def main():
    db = SessionLocal()
    
    print("[GFPS] Downloading today's fixtures...")
    params = {"date": "2025-11-14"}  # example, replace with runtime date
    r = requests.get(API_URL, params=params, headers=HEADERS)
    data = r.json()["response"]

    print(f"[GFPS] Loaded {len(data)} fixtures")

    for f in data:
        fixture = Fixture(
            api_id=f["fixture"]["id"],
            league=f["league"]["name"],
            league_id=f["league"]["id"],
            home=f["teams"]["home"]["name"],
            away=f["teams"]["away"]["name"],
            kickoff=f["fixture"]["date"]
        )
        db.add(fixture)
    db.commit()
    print("[GFPS] Fixtures saved.")

if __name__ == "__main__":
    main()
