"""Test the read queries."""

from vitals_api.models import Reading
from vitals_api.queries import get_latest_reading

BASE_READING = {
    "patient_id": "p-1",
    "respiratory_rate_per_min": 16,
    "heart_rate_bpm": 72,
    "spo2_percent": 98,
}

OLD_RECORDED_AT = "2026-10-06T10:15:00Z"
NEW_RECORDED_AT = "2026-10-07T11:00:00Z"


def add_reading(session, recorded_at):
    reading = {**BASE_READING, "recorded_at": recorded_at}
    row = Reading.model_validate(reading)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def test_get_latest_reading_returns_none_for_unknown_patient(session):
    reading = get_latest_reading(session, "nobody")
    assert reading is None


def test_get_latest_reading_returns_newest_reading(session):
    newer_reading = add_reading(session, NEW_RECORDED_AT)
    add_reading(session, OLD_RECORDED_AT)

    data = get_latest_reading(session, BASE_READING["patient_id"])
    assert data.id == newer_reading.id
    assert data.recorded_at == newer_reading.recorded_at
