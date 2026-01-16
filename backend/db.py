import os
import shutil
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DEFAULT_DB_URL = "sqlite:///./gfps.db"


def _ensure_writable_sqlite_url(url: str) -> str:
    parsed = make_url(url)
    if not parsed.drivername.startswith("sqlite"):
        return url

    db_path = parsed.database or ""
    if db_path and not os.path.isabs(db_path):
        db_path = os.path.abspath(db_path)

    target_dir = os.path.dirname(db_path) or "."
    writable = (
        os.access(db_path, os.W_OK)
        if os.path.exists(db_path)
        else os.access(target_dir, os.W_OK)
    )
    if writable:
        return url

    tmp_path = os.path.join(tempfile.gettempdir(), os.path.basename(db_path) or "gfps.db")
    if os.path.exists(db_path):
        if os.path.exists(tmp_path):
            try:
                os.chmod(tmp_path, 0o666)
            except Exception:
                pass
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        shutil.copy(db_path, tmp_path)
        os.chmod(tmp_path, 0o666)
    return f"sqlite:///{tmp_path}"


DATABASE_URL = _ensure_writable_sqlite_url(os.getenv("DATABASE_URL", DEFAULT_DB_URL))
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
