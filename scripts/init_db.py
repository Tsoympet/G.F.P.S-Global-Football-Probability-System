"""
Initialize GFPS database schema
Creates all tables using SQLAlchemy metadata.
"""

from backend.db import Base, engine
from backend import models

def main():
    print("[GFPS] Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("[GFPS] Done.")

if __name__ == "__main__":
    main()
