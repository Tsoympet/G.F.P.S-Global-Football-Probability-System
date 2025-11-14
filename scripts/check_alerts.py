"""
Admin tool: print all alert rules + last triggered events
"""

from backend.db import SessionLocal
from backend.models import AlertRule, AlertEvent

def main():
    db = SessionLocal()
    print("\n=== GFPS Alert Rules ===")

    rules = db.query(AlertRule).all()
    for r in rules:
        print(f"- [{r.id}] {r.name} | Active: {r.is_active}")
    
    print("\n=== Last Alert Events ===")
    events = db.query(AlertEvent).order_by(AlertEvent.id.desc()).limit(20).all()
    for e in events:
        print(f"{e.id} | Fixture {e.fixture_id} | {e.market}/{e.outcome} | EV: {e.ev}")

if __name__ == "__main__":
    main()
