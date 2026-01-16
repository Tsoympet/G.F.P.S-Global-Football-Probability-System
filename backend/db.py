import os
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gfps.db")
DATABASE_URL_PARSED = make_url(DATABASE_URL)

CONNECT_ARGS = (
    {"check_same_thread": False}
    if DATABASE_URL_PARSED.drivername.startswith("sqlite")
    else {}
)


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=CONNECT_ARGS,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)
