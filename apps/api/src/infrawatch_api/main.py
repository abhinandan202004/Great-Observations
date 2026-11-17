"""Application factory for the InfraWatch API."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine

from infrawatch_api import __version__, auth, telemetry


class HealthResponse(BaseModel):
    """Liveness report returned by ``GET /health``."""

    status: Literal["ok"]
    service: str
    version: str


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if len(app.state.jwt_secret) < 32:
        raise RuntimeError("JWT_SECRET must be at least 32 characters")
    app.state.engine = create_async_engine(os.environ["DATABASE_URL"])
    yield
    await app.state.engine.dispose()


def create_app() -> FastAPI:
    """Build and return the FastAPI application."""
    app = FastAPI(title="InfraWatch API", version=__version__, lifespan=lifespan)
    app.state.ingest_keys = tuple(
        key for key in os.environ.get("INGEST_API_KEYS", "").split(",") if key
    )
    app.state.change_webhook_secret = os.environ.get("CHANGE_WEBHOOK_SECRET", "")
    app.state.jwt_secret = os.environ.get("JWT_SECRET", "")
    app.include_router(telemetry.router)
    app.include_router(auth.router)

    @app.get("/health", tags=["operations"])
    def health() -> HealthResponse:
        """Report that the process is running."""
        return HealthResponse(status="ok", service="api", version=__version__)

    return app


app = create_app()
