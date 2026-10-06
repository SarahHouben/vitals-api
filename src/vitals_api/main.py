"""FastAPI application and routes for the vitals API."""

from fastapi import FastAPI
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class Reading(BaseModel):
    """Vital signs recorded for one patient at one point in time."""

    model_config = ConfigDict(str_strip_whitespace=True)

    patient_id: str = Field(min_length=1)
    recorded_at: AwareDatetime
    respiratory_rate_per_min: int = Field(ge=0, le=60)
    heart_rate_bpm: int = Field(ge=0, le=250)
    spo2_percent: int = Field(ge=0, le=100)


app = FastAPI()


@app.get("/health")
async def get_health() -> dict[str, str]:
    """Report whether the API is healthy."""
    return {"status": "ok"}


@app.post("/readings", status_code=201)
async def create_reading(reading: Reading) -> Reading:
    """Submit a patient's reading."""
    return reading
