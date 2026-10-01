"""FastAPI application and routes for the vitals API."""

from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def get_health() -> dict[str, str]:
    """Report whether the API is healthy."""
    return {"status": "ok"}
