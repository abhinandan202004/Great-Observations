"""Local accounts: login, short-lived access tokens and rotating refresh tokens."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal
from uuid import UUID, uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

router = APIRouter(tags=["auth"])

ACCESS_TTL = timedelta(minutes=15)
REFRESH_TTL = timedelta(days=14)
REFRESH_COOKIE = "infrawatch_refresh"
# A cross-site form cannot send a custom header without a preflight, so this is the CSRF guard.
CSRF_HEADER = "X-InfraWatch-Request"

hasher = PasswordHasher()
# Checked when the email is unknown, so a wrong email costs the same time as a wrong password.
DUMMY_HASH = hasher.hash("unused")
bearer = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"  # noqa: S105 (OAuth field name, not a secret)
    expires_in: int = int(ACCESS_TTL.total_seconds())


class Me(BaseModel):
    id: UUID
    email: str
    display_name: str


def hash_password(password: str) -> str:
    return hasher.hash(password)


def check_password(stored: str | None, password: str) -> bool:
    try:
        matches = hasher.verify(stored or DUMMY_HASH, password)
    except (VerificationError, InvalidHashError):
        return False
    return matches and stored is not None


def issue_access_token(user_id: UUID, secret: str, now: datetime) -> str:
    claims = {"sub": str(user_id), "iat": now, "exp": now + ACCESS_TTL}
    return jwt.encode(claims, secret, algorithm="HS256")


def read_access_token(token: str, secret: str) -> UUID:
    claims = jwt.decode(token, secret, algorithms=["HS256"], options={"require": ["exp", "sub"]})
    return UUID(claims["sub"])


def _hash_refresh(token: str) -> str:
    # Tokens are random 256-bit values: a fast hash only keeps them out of the database.
    return hashlib.sha256(token.encode()).hexdigest()


async def _start_session(
    conn: AsyncConnection, request: Request, response: Response, user_id: UUID, family: UUID
) -> TokenResponse:
    refresh = secrets.token_urlsafe(32)
    await conn.execute(
        text(
            "INSERT INTO refresh_tokens (user_id, family_id, token_hash, expires_at) "
            "VALUES (:user_id, :family, :hash, :expires_at)"
        ),
        {
            "user_id": user_id,
            "family": family,
            "hash": _hash_refresh(refresh),
            "expires_at": datetime.now(UTC) + REFRESH_TTL,
        },
    )
    response.set_cookie(
        REFRESH_COOKIE,
        refresh,
        max_age=int(REFRESH_TTL.total_seconds()),
        httponly=True,
        secure=True,
        samesite="strict",
        path="/",
    )
    access = issue_access_token(user_id, request.app.state.jwt_secret, datetime.now(UTC))
    return TokenResponse(access_token=access)


def _require_csrf_header(request: Request) -> None:
    if request.headers.get(CSRF_HEADER) != "1":
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"{CSRF_HEADER} header required")


@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request, response: Response) -> TokenResponse:
    engine = request.app.state.engine
    async with engine.begin() as conn:
        row = (
            await conn.execute(
                text("SELECT id, password_hash FROM users WHERE email = :email"),
                {"email": body.email},
            )
        ).first()
        if row is None or not check_password(row.password_hash, body.password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong email or password")
        return await _start_session(conn, request, response, row.id, uuid4())


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh(request: Request, response: Response) -> TokenResponse:
    _require_csrf_header(request)
    token = request.cookies.get(REFRESH_COOKIE)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sign in again")
    engine = request.app.state.engine
    async with engine.begin() as conn:
        row = (
            await conn.execute(
                text(
                    "SELECT user_id, family_id, expires_at, revoked_at FROM refresh_tokens "
                    "WHERE token_hash = :hash FOR UPDATE"
                ),
                {"hash": _hash_refresh(token)},
            )
        ).first()
        if row is None or row.expires_at <= datetime.now(UTC):
            usable = False
        elif row.revoked_at is not None:
            # A rotated token came back: someone else holds a copy, so the whole login ends.
            await conn.execute(
                text(
                    "UPDATE refresh_tokens SET revoked_at = now() "
                    "WHERE family_id = :family AND revoked_at IS NULL"
                ),
                {"family": row.family_id},
            )
            usable = False
        else:
            await conn.execute(
                text("UPDATE refresh_tokens SET revoked_at = now() WHERE token_hash = :hash"),
                {"hash": _hash_refresh(token)},
            )
            usable = True
    # Outside the transaction above: raising inside it would roll the revocations back.
    if not usable:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sign in again")
    async with engine.begin() as conn:
        return await _start_session(conn, request, response, row.user_id, row.family_id)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, response: Response) -> None:
    _require_csrf_header(request)
    token = request.cookies.get(REFRESH_COOKIE)
    if token:
        async with request.app.state.engine.begin() as conn:
            await conn.execute(
                text(
                    "UPDATE refresh_tokens SET revoked_at = now() WHERE family_id = ("
                    "SELECT family_id FROM refresh_tokens WHERE token_hash = :hash) "
                    "AND revoked_at IS NULL"
                ),
                {"hash": _hash_refresh(token)},
            )
    response.delete_cookie(REFRESH_COOKIE, path="/", secure=True, httponly=True, samesite="strict")


def current_user_id(
    request: Request, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]
) -> UUID:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sign in again")
    try:
        return read_access_token(credentials.credentials, request.app.state.jwt_secret)
    except (jwt.PyJWTError, ValueError) as error:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sign in again") from error


@router.get("/auth/me", response_model=Me)
async def me(request: Request, user_id: Annotated[UUID, Depends(current_user_id)]) -> Me:
    async with request.app.state.engine.connect() as conn:
        row = (
            await conn.execute(
                text("SELECT id, email, display_name FROM users WHERE id = :id"), {"id": user_id}
            )
        ).first()
    if row is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sign in again")
    return Me(id=row.id, email=row.email, display_name=row.display_name)
