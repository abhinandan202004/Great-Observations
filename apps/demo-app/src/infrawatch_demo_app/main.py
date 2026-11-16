"""The InfraWatch demo app: a simulated checkout service with fault injection.

A background loop sends checkout requests, each calling a simulated payment-gateway.
Request metrics, logs and change events are posted to the InfraWatch ingest API.
"""

import asyncio
import logging
import os
import random
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Literal
from uuid import uuid4

import httpx2
from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel

from infrawatch_demo_app import __version__
from infrawatch_demo_app.faults import FaultActiveError, Faults
from infrawatch_demo_app.telemetry import Reporter

REQUESTS_PER_SECOND = 5
REPORT_SECONDS = 5.0
ERROR_RATE = {"error-burst": 0.5, "bad-deploy": 0.3}
EXTRA_LATENCY_SECONDS = {"dependency-latency": 0.8, "bad-deploy": 0.3}

log = logging.getLogger("infrawatch_demo_app")


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str


class CheckoutResponse(BaseModel):
    status: Literal["ok"]
    correlation_id: str


class FaultResponse(BaseModel):
    active: str | None


async def checkout(app: FastAPI) -> tuple[bool, str]:
    """Handle one checkout, including its call to the simulated payment-gateway."""
    fault = app.state.faults.active()
    correlation_id = uuid4().hex
    started = time.perf_counter()
    # Simulation only, not security: random is the right tool.
    await asyncio.sleep(random.uniform(0.02, 0.06) + EXTRA_LATENCY_SECONDS.get(fault, 0.0))  # noqa: S311
    ok = random.random() >= ERROR_RATE.get(fault, 0.005)  # noqa: S311
    app.state.reporter.record((time.perf_counter() - started) * 1000, ok, correlation_id)
    return ok, correlation_id


async def generate_traffic(app: FastAPI) -> None:
    requests: set[asyncio.Task[tuple[bool, str]]] = set()  # keeps tasks alive until they finish
    while True:
        request = asyncio.create_task(checkout(app))
        requests.add(request)
        request.add_done_callback(requests.discard)
        await asyncio.sleep(1 / REQUESTS_PER_SECOND)


async def report(app: FastAPI, client: httpx2.AsyncClient) -> None:
    while True:
        await asyncio.sleep(REPORT_SECONDS)
        try:
            await app.state.reporter.flush(client)
        except Exception:
            # One bad window must not silently end reporting for good.
            log.exception("Reporting failed; continuing with the next window")


class _NoHealthFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "/health" not in record.getMessage()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("httpx2").setLevel(logging.WARNING)  # one INFO line per request otherwise
    logging.getLogger("uvicorn.access").addFilter(_NoHealthFilter())
    async with httpx2.AsyncClient(
        base_url=os.environ.get("INGEST_URL", "http://api:8000"),
        headers={"Authorization": f"Bearer {os.environ['INGEST_API_KEY']}"},
        timeout=10,
    ) as client:
        tasks = [
            asyncio.create_task(generate_traffic(app)),
            asyncio.create_task(report(app, client)),
        ]
        yield
        for task in tasks:
            task.cancel()
        app.state.faults.stop()


def create_app() -> FastAPI:
    app = FastAPI(title="InfraWatch demo app", version=__version__, lifespan=lifespan)
    app.state.faults = Faults()
    app.state.reporter = Reporter(os.environ.get("CHANGE_WEBHOOK_SECRET", ""))

    @app.get("/health", tags=["operations"])
    def health() -> HealthResponse:
        return HealthResponse(status="ok", service="demo-app", version=__version__)

    @app.post("/checkout", tags=["demo"])
    async def post_checkout(request: Request) -> CheckoutResponse:
        ok, correlation_id = await checkout(request.app)
        if not ok:
            raise HTTPException(502, f"payment-gateway error (correlation id {correlation_id})")
        return CheckoutResponse(status="ok", correlation_id=correlation_id)

    # Fault control is unauthenticated: Compose publishes this port on 127.0.0.1 only.
    @app.post("/faults/{name}", tags=["faults"])
    def start_fault(
        name: Literal["cpu-spike", "error-burst", "bad-deploy", "dependency-latency"],
        request: Request,
        minutes: Annotated[float, Query(gt=0, le=60)] = 5,
    ) -> FaultResponse:
        try:
            request.app.state.faults.start(name, minutes)
        except FaultActiveError as error:
            raise HTTPException(409, f"Fault already running: {error}. Stop it first.") from error
        if name == "bad-deploy":
            request.app.state.reporter.change(
                "deploy", "Deployed checkout v2.4.1 (injected bad deploy)"
            )
        return FaultResponse(active=name)

    @app.delete("/faults", tags=["faults"])
    def stop_fault(request: Request) -> FaultResponse:
        request.app.state.faults.stop()
        return FaultResponse(active=None)

    return app


app = create_app()
