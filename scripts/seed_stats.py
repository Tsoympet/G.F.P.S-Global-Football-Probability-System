"""
Seed base statistical weights for GFPS.
Used for Poisson, EV engine, league strength, etc.
"""

import json
from backend.db import SessionLocal
from backend.models import LeagueStrength

seed_data = [
    {"league": "Premier League", "attack": 1.12, "defense": 0.88},
    {"league": "La Liga", "attack": 1.05, "defense": 0.93},
    {"league": "Serie A", "attack": 1.03, "defense": 0.95},
    {"league": "Bundesliga", "attack": 1.15, "defense": 0.90},
    {"league": "Ligue 1", "attack": 1.00, "defense": 1.00}
]

def main():
    db = SessionLocal()
    print("[GFPS] Seeding league strength coefficients...")
    for row in seed_data:
        item = LeagueStrength(**row)
        db.add(item)
    db.commit()
    print("[GFPS] Completed seeding.")

if __name__ == "__main__":
    main()
