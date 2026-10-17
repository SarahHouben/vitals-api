"""Test the read queries."""

import pytest

from vitals_api.models import Reading, VitalAlert
from vitals_api.queries import alerts_for_reading, get_latest_reading, list_readings

BASE_READING = {
    "patient_id": "p-1",
    "respiratory_rate_per_min": 16,
    "heart_rate_bpm": 72,
    "spo2_percent": 98,
}

OLD_RECORDED_AT = "2026-10-06T10:15:00Z"
MIDDLE_RECORDED_AT = "2026-10-06T12:15:00Z"
NEW_RECORDED_AT = "2026-10-07T11:00:00Z"


def add_reading(session, recorded_at):
    data = {**BASE_READING, "recorded_at": recorded_at}
    row = Reading.model_validate(data)
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

    reading = get_latest_reading(session, BASE_READING["patient_id"])
    assert reading.id == newer_reading.id


def test_list_readings_returns_empty_list_for_unknown_patient(session):
    readings = list_readings(session, "nobody")
    assert readings == []


def test_list_readings_returns_newest_readings_first(session):
    newest_reading = add_reading(session, NEW_RECORDED_AT)
    oldest_reading = add_reading(session, OLD_RECORDED_AT)
    middle_reading = add_reading(session, MIDDLE_RECORDED_AT)

    readings = list_readings(session, BASE_READING["patient_id"])
    assert [r.id for r in readings] == [
        newest_reading.id,
        middle_reading.id,
        oldest_reading.id,
    ]


def test_list_readings_returns_only_newest_up_to_limit(session):
    newest_reading = add_reading(session, NEW_RECORDED_AT)
    add_reading(session, OLD_RECORDED_AT)
    middle_reading = add_reading(session, MIDDLE_RECORDED_AT)

    readings = list_readings(session, BASE_READING["patient_id"], limit=2)
    assert [r.id for r in readings] == [newest_reading.id, middle_reading.id]


def test_alerts_for_reading_returns_empty_list_for_normal_reading():
    data = {**BASE_READING, "recorded_at": NEW_RECORDED_AT}
    reading = Reading.model_validate(data)
    alerts = alerts_for_reading(reading)
    assert alerts == []


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        pytest.param("heart_rate_bpm", 100, [], id="heart_rate_100_is_normal"),
        pytest.param(
            "heart_rate_bpm",
            101,
            [
                VitalAlert(
                    field="heart_rate_bpm", value=101, limit=100, direction="above"
                )
            ],
            id="heart_rate_101_is_high",
        ),
        pytest.param(
            "heart_rate_bpm",
            50,
            [],
            id="heart_rate_50_is_normal",
        ),
        pytest.param(
            "heart_rate_bpm",
            49,
            [VitalAlert(field="heart_rate_bpm", value=49, limit=50, direction="below")],
            id="heart_rate_49_is_low",
        ),
        pytest.param(
            "respiratory_rate_per_min", 12, [], id="respiratory_rate_12_is_normal"
        ),
        pytest.param(
            "respiratory_rate_per_min",
            11,
            [
                VitalAlert(
                    field="respiratory_rate_per_min",
                    value=11,
                    limit=12,
                    direction="below",
                )
            ],
            id="respiratory_rate_11_is_low",
        ),
        pytest.param(
            "respiratory_rate_per_min", 20, [], id="respiratory_rate_20_is_normal"
        ),
        pytest.param(
            "respiratory_rate_per_min",
            21,
            [
                VitalAlert(
                    field="respiratory_rate_per_min",
                    value=21,
                    limit=20,
                    direction="above",
                )
            ],
            id="respiratory_rate_21_is_high",
        ),
        pytest.param("spo2_percent", 94, [], id="spo2_94_is_normal"),
        pytest.param(
            "spo2_percent",
            93,
            [VitalAlert(field="spo2_percent", value=93, limit=94, direction="below")],
            id="spo2_93_is_low",
        ),
    ],
)
def test_alerts_for_reading_limits(field, value, expected):
    data = {
        **BASE_READING,
        "recorded_at": NEW_RECORDED_AT,
        field: value,
    }
    reading = Reading.model_validate(data)
    assert alerts_for_reading(reading) == expected
