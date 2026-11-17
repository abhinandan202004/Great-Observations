"""Every route is listed here with its capability, and every role is tried on every listed route."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from infrawatch_api import access
from infrawatch_api.auth import current_user_id
from infrawatch_api.main import create_app
from infrawatch_core.policy import Capability, allows
from infrawatch_core.roles import Role

SINCE = "since=2026-01-01T00:00:00Z"
GATED = {
    ("GET", "/services"): Capability.VIEW_TELEMETRY,
    ("GET", "/services/{service}/metrics"): Capability.VIEW_TELEMETRY,
    ("GET", "/services/{service}/changes"): Capability.VIEW_TELEMETRY,
    ("GET", "/services/{service}/metrics/{metric}"): Capability.VIEW_TELEMETRY,
    ("GET", "/logs"): Capability.VIEW_INCIDENT_DETAIL,
    ("GET", "/access-requests"): Capability.MANAGE_USERS_TEAMS_RULES,
    ("POST", "/access-requests/{request_id}/approve"): Capability.MANAGE_USERS_TEAMS_RULES,
    ("POST", "/access-requests/{request_id}/reject"): Capability.MANAGE_USERS_TEAMS_RULES,
    ("POST", "/users"): Capability.MANAGE_USERS_TEAMS_RULES,
}
# Routes that check something other than a role: the caller's sign-in, or the ingest key.
NOT_ROLE_GATED = {
    ("GET", "/health"),
    ("POST", "/auth/login"),
    ("POST", "/auth/refresh"),
    ("POST", "/auth/logout"),
    ("GET", "/auth/me"),
    ("POST", "/access-requests"),
    ("POST", "/ingest/metrics"),
    ("POST", "/ingest/logs"),
    ("POST", "/ingest/changes"),
}


def _path(template: str) -> str:
    return (
        template.replace("{service}", "checkout")
        .replace("{metric}", "cpu_percent")
        .replace("{request_id}", "5f0c3a7e-1b2d-4c5e-9f00-0123456789ab")
    )


def _url(template: str) -> str:
    query = "" if template == "/services" else f"?{SINCE}"
    return _path(template) + query


def test_every_route_is_listed_in_the_matrix() -> None:
    # The OpenAPI schema lists every operation, including routes inside included routers.
    paths = create_app().openapi()["paths"]
    routes = {(method.upper(), path) for path, operations in paths.items() for method in operations}

    assert routes == set(GATED) | NOT_ROLE_GATED


@pytest.mark.parametrize("role", list(Role))
@pytest.mark.parametrize("template", list(GATED))
def test_each_role_gets_the_matrix_answer(
    role: Role, template: tuple[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    method, path_template = template
    app = create_app()
    app.dependency_overrides[current_user_id] = lambda: uuid4()

    async def roles_of(_request: object, _user_id: object) -> frozenset[Role]:
        return frozenset({role})

    monkeypatch.setattr(access, "load_roles", roles_of)
    # Only the status is checked: an allowed request reaches a handler that has no database here.
    response = TestClient(app, raise_server_exceptions=False).request(method, _url(path_template))

    denied = response.status_code == 403
    assert denied != allows([role], GATED[template]), (role, template, response.status_code)


@pytest.mark.parametrize("template", list(GATED))
def test_no_token_is_refused_before_any_role_check(template: tuple[str, str]) -> None:
    method, path_template = template
    response = TestClient(create_app()).request(method, _url(path_template))

    assert response.status_code == 401
