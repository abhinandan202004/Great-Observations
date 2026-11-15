"""Application factory for the InfraWatch API."""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from infrawatch_api import __version__


class HealthResponse(BaseModel):
    """Liveness report returned by ``GET /health``."""

    status: Literal["ok"]
    service: str
    version: str


def create_app() -> FastAPI:
    """Build and return the FastAPI application."""
    app = FastAPI(title="InfraWatch API", version=__version__)

    @app.get("/health", tags=["operations"])
    def health() -> HealthResponse:
        """Report that the process is running."""
        return HealthResponse(status="ok", service="api", version=__version__)

    return app


app = create_app()
