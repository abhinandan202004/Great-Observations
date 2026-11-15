"""Application factory for the InfraWatch demo app."""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from infrawatch_demo_app import __version__


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str


def create_app() -> FastAPI:
    app = FastAPI(title="InfraWatch demo app", version=__version__)

    @app.get("/health", tags=["operations"])
    def health() -> HealthResponse:
        return HealthResponse(status="ok", service="demo-app", version=__version__)

    return app


app = create_app()
