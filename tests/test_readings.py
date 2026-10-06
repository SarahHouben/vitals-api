"""Test the readings endpoint of the FastAPI application."""

import pytest
from fastapi.testclient import TestClient

from vitals_api.main import app

VALID_READING = {
    "patient_id": "p-1",
    "recorded_at": "2026-10-06T10:15:00Z",
    "respiratory_rate_per_min": 16,
    "heart_rate_bpm": 72,
    "spo2_percent": 98,
}


def test_create_reading_returns_201():
    response = TestClient(app).post(
        "/readings",
        json=VALID_READING,
    )
    assert response.status_code == 201
    assert response.json() == VALID_READING


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
def test_invalid_reading_returns_422(payload, invalid_field):
    response = TestClient(app).post(
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
def test_boundary_reading_returns_201(payload):
    response = TestClient(app).post(
        "/readings",
        json=payload,
    )
    assert response.status_code == 201
    assert response.json() == payload
