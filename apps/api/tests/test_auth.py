from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest
from fastapi.testclient import TestClient

from infrawatch_api.auth import (
    ACCESS_TTL,
    check_password,
    hash_password,
    issue_access_token,
    read_access_token,
)
from infrawatch_api.main import create_app

SECRET = "x" * 32


def test_password_round_trip_and_missing_hash() -> None:
    stored = hash_password("correct horse")

    assert check_password(stored, "correct horse")
    assert not check_password(stored, "wrong")
    assert not check_password(None, "anything")


def test_access_token_is_accepted_until_it_expires() -> None:
    user = uuid4()
    fresh = issue_access_token(user, SECRET, now=datetime.now(UTC))
    expired = issue_access_token(
        user, SECRET, now=datetime.now(UTC) - ACCESS_TTL - timedelta(minutes=1)
    )

    assert read_access_token(fresh, SECRET) == user
    with pytest.raises(jwt.ExpiredSignatureError):
        read_access_token(expired, SECRET)


def test_access_token_with_another_secret_or_algorithm_is_refused() -> None:
    user = uuid4()
    forged = jwt.encode(
        {"sub": str(user), "exp": datetime.now(UTC) + ACCESS_TTL}, "y" * 32, "HS256"
    )
    unsigned = jwt.encode({"sub": str(user), "exp": datetime.now(UTC) + ACCESS_TTL}, None, "none")

    with pytest.raises(jwt.PyJWTError):
        read_access_token(forged, SECRET)
    with pytest.raises(jwt.PyJWTError):
        read_access_token(unsigned, SECRET)


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("JWT_SECRET", SECRET)
    return TestClient(create_app())


def test_refresh_and_logout_need_the_csrf_header(client: TestClient) -> None:
    assert client.post("/auth/refresh").status_code == 403
    assert client.post("/auth/logout").status_code == 403


def test_me_needs_a_bearer_token(client: TestClient) -> None:
    assert client.get("/auth/me").status_code == 401
    assert client.get("/auth/me", headers={"Authorization": "Bearer nonsense"}).status_code == 401


def test_app_refuses_to_start_with_a_short_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "too-short")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://unused@localhost/unused")

    with pytest.raises(RuntimeError, match="JWT_SECRET"), TestClient(create_app()):
        pass
