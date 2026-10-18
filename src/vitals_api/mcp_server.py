"""MCP server for the vitals API."""

from typing import Annotated

from mcp.server.mcpserver import MCPServer
from pydantic import Field
from sqlmodel import Session

from vitals_api import queries
from vitals_api.db import engine
from vitals_api.models import PatientAlert, ReadingPublic

mcp = MCPServer("vitals")


@mcp.tool()
def latest_reading(
    patient_id: Annotated[str, Field(description="The patient's id, e.g. 'p-1'.")],
) -> ReadingPublic | None:
    """Return the patient's most recently recorded reading, or null if there is none.

    The reading has an id, patient_id, recorded_at (UTC, ISO 8601),
    respiratory_rate_per_min (breaths per minute), heart_rate_bpm (beats per minute)
    and spo2_percent (oxygen saturation, %).
    All data is made up.
    """
    with Session(engine) as session:
        reading = queries.get_latest_reading(session, patient_id)
        if reading is None:
            return None
        return ReadingPublic.model_validate(reading)


@mcp.tool()
def list_readings(
    patient_id: Annotated[str, Field(description="The patient's id, e.g. 'p-1'.")],
    limit: Annotated[
        int,
        Field(
            ge=1, le=100, description="Maximum number of readings to return, 1 to 100."
        ),
    ] = 10,
) -> list[ReadingPublic]:
    """List a patient's most recent readings, newest first, up to `limit` of them.

    Each reading has an id, patient_id, recorded_at (UTC, ISO 8601),
    respiratory_rate_per_min (breaths per minute), heart_rate_bpm (beats per minute)
    and spo2_percent (oxygen saturation, %).
    Returns an empty list if the patient has no readings. All data is made up.
    """
    with Session(engine) as session:
        readings = queries.list_readings(session, patient_id, limit=limit)
        return [ReadingPublic.model_validate(r) for r in readings]


@mcp.tool()
def patients_with_alerts() -> list[PatientAlert]:
    """List the patients whose latest reading is outside of the normal range.

    Each result has a reading and a list of alerts for the reading.
    Each reading has an id, patient_id, recorded_at (UTC, ISO 8601),
    respiratory_rate_per_min (breaths per minute), heart_rate_bpm (beats per minute)
    and spo2_percent (oxygen saturation, %).
    Each alert has a field name, the value, the limit it crossed, and the direction
    ("below" or "above").
    Returns one entry per patient, sorted by patient_id.
    Returns an empty list if no patient's latest reading is out of the normal range.
    All data is made up. The thresholds are illustrative, not clinical advice.
    """
    with Session(engine) as session:
        return queries.patients_with_alerts(session)


if __name__ == "__main__":
    mcp.run()
