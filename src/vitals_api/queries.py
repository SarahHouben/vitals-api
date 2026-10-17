"""Read queries shared by the API and the MCP server."""

from sqlmodel import Session, select

from vitals_api.models import Reading, ReadingBase, VitalAlert


def get_latest_reading(session: Session, patient_id: str) -> Reading | None:
    """Return the patient's most recently recorded reading, or None if there is none."""
    statement = (
        select(Reading)
        .where(Reading.patient_id == patient_id)
        .order_by(Reading.recorded_at.desc())
    )
    return session.exec(statement).first()


def list_readings(session: Session, patient_id: str, limit: int = 10) -> list[Reading]:
    """Return the patient's most recent readings, newest first, up to `limit` of them."""
    statement = (
        select(Reading)
        .where(Reading.patient_id == patient_id)
        .order_by(Reading.recorded_at.desc())
        .limit(limit)
    )
    return session.exec(statement).all()


# Illustrative thresholds for made-up data, not clinical advice.
NORMAL_RANGES = {
    "respiratory_rate_per_min": (12, 20),
    "heart_rate_bpm": (50, 100),
    "spo2_percent": (94, None),
}


def alerts_for_reading(reading: ReadingBase) -> list[VitalAlert]:
    """Return the vital signs in the reading that are outside the normal range; empty if all are normal."""
    alerts = []
    for field, (low, high) in NORMAL_RANGES.items():
        value = getattr(reading, field)
        if low is not None and value < low:
            alerts.append(
                VitalAlert(
                    field=field,
                    value=value,
                    limit=low,
                    direction="below",
                )
            )
        if high is not None and value > high:
            alerts.append(
                VitalAlert(
                    field=field,
                    value=value,
                    limit=high,
                    direction="above",
                )
            )
    return alerts
