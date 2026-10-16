"""FastAPI application and routes for the vitals API."""

from fastapi import FastAPI

from .models import Reading

app = FastAPI()


@app.get("/health")
async def get_health() -> dict[str, str]:
    """Report whether the API is healthy."""
    return {"status": "ok"}


@app.post("/readings", status_code=201)
async def create_reading(reading: Reading) -> Reading:
    """Submit a patient's reading."""
    return reading
