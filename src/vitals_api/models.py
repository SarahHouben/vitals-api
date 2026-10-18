"""Models for the vitals API."""

import uuid
from typing import Literal

from pydantic import AwareDatetime, ConfigDict
from sqlalchemy import Index
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

    __table_args__ = (
        Index("ix_reading_patient_id_recorded_at", "patient_id", "recorded_at"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid7, primary_key=True)


class ReadingPublic(ReadingBase):
    """Vital signs recorded for a patient as returned by the API."""

    id: uuid.UUID


class VitalAlert(SQLModel):
    """Alert data for vital signs outside of the normal range."""

    field: str
    value: int
    limit: int
    direction: Literal["below", "above"]


class PatientAlert(SQLModel):
    """A patient's latest reading together with its alerts."""

    reading: ReadingPublic
    alerts: list[VitalAlert]
