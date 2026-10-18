"""MCP server for the vitals API."""

from mcp.server.mcpserver import MCPServer
from sqlmodel import Session

from vitals_api import queries
from vitals_api.db import engine
from vitals_api.models import ReadingPublic

mcp = MCPServer("vitals")


@mcp.tool()
def latest_reading(patient_id: str) -> ReadingPublic | None:
    """Return the patient's most recently recorded reading, or None if there is none."""
    with Session(engine) as session:
        reading = queries.get_latest_reading(session, patient_id)
        if reading is None:
            return None
        return ReadingPublic.model_validate(reading)


if __name__ == "__main__":
    mcp.run()
