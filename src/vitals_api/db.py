"""Database engine and session setup for the vitals API."""

from sqlmodel import Session, SQLModel, create_engine

SQLITE_FILE_NAME = "vitals.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})


def create_db_and_tables():
    """Create any tables that don't exist yet."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Yield a database session for one request, then close it."""
    with Session(engine) as session:
        yield session
