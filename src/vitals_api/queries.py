"""Read queries shared by the API and the MCP server."""

from sqlmodel import Session, select

from vitals_api.models import Reading


def get_latest_reading(session: Session, patient_id: str) -> Reading | None:
    """Return the patient's most recently recorded reading, or None if there is none."""
    statement = (
        select(Reading)
        .where(Reading.patient_id == patient_id)
        .order_by(Reading.recorded_at.desc())
    )
    return session.exec(statement).first()
