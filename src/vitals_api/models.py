"""Models for the vitals API."""

import uuid

from pydantic import AwareDatetime, ConfigDict
from sqlmodel import Field, SQLModel


class ReadingBase(SQLModel):
    """Fields and validation shared by every reading model."""

    model_config = ConfigDict(str_strip_whitespace=True)
    patient_id: str = Field(min_length=1)
    recorded_at: AwareDatetime
    respiratory_rate_per_min: int = Field(ge=0, le=60)
    heart_rate_bpm: int = Field(ge=0, le=250)
    spo2_percent: int = Field(ge=0, le=100)


class ReadingCreate(ReadingBase):
    """Request body for adding a patient's reading."""


class Reading(ReadingBase, table=True):
    """A reading as stored in the database."""

    id: uuid.UUID = Field(default_factory=uuid.uuid7, primary_key=True)


class ReadingPublic(ReadingBase):
    """Vital signs recorded for a patient as returned by the API."""

    id: uuid.UUID
