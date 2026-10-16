"""Test the readings endpoint of the FastAPI application."""

import uuid
from datetime import UTC

import pytest
from sqlmodel import select

from vitals_api.models import Reading

VALID_READING = {
    "patient_id": "p-1",
    "recorded_at": "2026-10-06T10:15:00Z",
    "respiratory_rate_per_min": 16,
    "heart_rate_bpm": 72,
    "spo2_percent": 98,
}


def assert_reading_saved(response, sent):
    assert response.status_code == 201
    body = response.json()
    reading_id = body.pop("id")
    assert uuid.UUID(reading_id).version == 7
    assert body == sent


def test_create_reading_returns_201(client):
    response = client.post(
        "/readings",
        json=VALID_READING,
    )
    assert_reading_saved(response, VALID_READING)


@pytest.mark.parametrize(
    ("payload", "invalid_field"),
    [
        pytest.param(
            {**VALID_READING, "patient_id": None},
            "patient_id",
            id="patient_id_null",
        ),
        pytest.param(
            {k: v for k, v in VALID_READING.items() if k != "patient_id"},
            "patient_id",
            id="patient_id_missing",
        ),
        pytest.param(
            {**VALID_READING, "patient_id": ""},
            "patient_id",
            id="patient_id_empty",
        ),
        pytest.param(
            {**VALID_READING, "patient_id": " "},
            "patient_id",
            id="patient_id_whitespace",
        ),
        pytest.param(
            {**VALID_READING, "recorded_at": "2026-10-06T10:15:00"},
            "recorded_at",
            id="recorded_at_without_offset",
        ),
        pytest.param(
            {**VALID_READING, "respiratory_rate_per_min": -1},
            "respiratory_rate_per_min",
            id="respiratory_rate_too_low",
        ),
        pytest.param(
            {**VALID_READING, "respiratory_rate_per_min": 77},
            "respiratory_rate_per_min",
            id="respiratory_rate_too_high",
        ),
        pytest.param(
            {**VALID_READING, "heart_rate_bpm": -1},
            "heart_rate_bpm",
            id="heart_rate_too_low",
        ),
        pytest.param(
            {**VALID_READING, "heart_rate_bpm": 500},
            "heart_rate_bpm",
            id="heart_rate_too_high",
        ),
        pytest.param(
            {**VALID_READING, "spo2_percent": -1},
            "spo2_percent",
            id="spo2_too_low",
        ),
        pytest.param(
            {**VALID_READING, "spo2_percent": 120},
            "spo2_percent",
            id="spo2_too_high",
        ),
    ],
)
def test_invalid_reading_returns_422(client, payload, invalid_field):
    response = client.post(
        "/readings",
        json=payload,
    )
    assert response.status_code == 422
    assert invalid_field in response.json()["detail"][0]["loc"]


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(
            {**VALID_READING, "respiratory_rate_per_min": 0},
            id="respiratory_rate_valid_lower_bound",
        ),
        pytest.param(
            {**VALID_READING, "respiratory_rate_per_min": 60},
            id="respiratory_rate_valid_upper_bound",
        ),
        pytest.param(
            {**VALID_READING, "heart_rate_bpm": 0},
            id="heart_rate_valid_lower_bound",
        ),
        pytest.param(
            {**VALID_READING, "heart_rate_bpm": 250},
            id="heart_rate_valid_upper_bound",
        ),
        pytest.param(
            {**VALID_READING, "spo2_percent": 0},
            id="spo2_valid_lower_bound",
        ),
        pytest.param(
            {**VALID_READING, "spo2_percent": 100},
            id="spo2_valid_upper_bound",
        ),
    ],
)
def test_boundary_reading_returns_201(client, payload):
    response = client.post(
        "/readings",
        json=payload,
    )
    assert_reading_saved(response, payload)


def test_create_reading_stores_it(client, session):
    response = client.post(
        "/readings",
        json=VALID_READING,
    )
    assert response.status_code == 201
    rows = session.exec(select(Reading)).all()
    assert len(rows) == 1
    assert rows[0].model_dump(mode="json") == response.json()


def test_recorded_at_is_returned_in_utc(client, session):
    response = client.post(
        "/readings",
        json={**VALID_READING, "recorded_at": "2026-10-06T11:15:00+01:00"},
    )
    assert response.status_code == 201
    assert response.json()["recorded_at"] == "2026-10-06T10:15:00Z"
    row = session.exec(select(Reading)).one()
    assert row.recorded_at.tzinfo == UTC
