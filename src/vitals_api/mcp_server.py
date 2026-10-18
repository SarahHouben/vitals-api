"""MCP server for the vitals API."""

from mcp.server.mcpserver import MCPServer
from sqlmodel import Session

from vitals_api import queries
from vitals_api.db import engine
from vitals_api.models import PatientAlert, ReadingPublic

mcp = MCPServer("vitals")


@mcp.tool()
def latest_reading(patient_id: str) -> ReadingPublic | None:
    """Return the patient's most recently recorded reading, or None if there is none."""
    with Session(engine) as session:
        reading = queries.get_latest_reading(session, patient_id)
        if reading is None:
            return None
        return ReadingPublic.model_validate(reading)


@mcp.tool()
def list_readings(patient_id: str, limit: int = 10) -> list[ReadingPublic]:
    """Return the patient's most recent readings, newest first, up to `limit` of them."""
    with Session(engine) as session:
        readings = queries.list_readings(session, patient_id, limit=limit)
        return [ReadingPublic.model_validate(r) for r in readings]


@mcp.tool()
def patients_with_alerts() -> list[PatientAlert]:
    """Return the patients whose latest reading has alerts, with those alerts."""
    with Session(engine) as session:
        return queries.patients_with_alerts(session)


if __name__ == "__main__":
    mcp.run()
