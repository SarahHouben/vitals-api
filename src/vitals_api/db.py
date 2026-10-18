"""Database engine and session setup for the vitals API."""

import os
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine


def database_path() -> Path:
    """Return the SQLite file's path: $VITALS_DB_PATH if set, else vitals.db in the project folder."""
    value = os.environ.get("VITALS_DB_PATH")
    if value:
        return Path(value)
    return Path(__file__).resolve().parents[2] / "vitals.db"


SQLITE_URL = f"sqlite:///{database_path()}"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})


def create_db_and_tables():
    """Create any tables that don't exist yet."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Yield a database session for one request, then close it."""
    with Session(engine) as session:
        yield session
