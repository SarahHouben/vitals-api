"""FastAPI application and routes for the vitals API."""

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlmodel import Session

from vitals_api.db import create_db_and_tables, get_session
from vitals_api.models import Reading, ReadingCreate, ReadingPublic


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the database tables on startup."""
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/health")
async def get_health() -> dict[str, str]:
    """Report whether the API is healthy."""
    return {"status": "ok"}


@app.post("/readings", status_code=201)
def create_reading(reading: ReadingCreate, session: SessionDep) -> ReadingPublic:
    """Store a patient's reading and return it with its new ID."""
    row = Reading.model_validate(reading)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row
