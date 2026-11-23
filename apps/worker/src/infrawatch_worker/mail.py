"""Deliver queued email from the outbox over SMTP, retrying failures with backoff."""

import asyncio
import hashlib
import os
import smtplib
from collections.abc import Callable
from datetime import timedelta
from email.message import EmailMessage
from typing import Any

from sqlalchemy import Row, text
from sqlalchemy.ext.asyncio import AsyncConnection

Send = Callable[[EmailMessage], None]
BATCH = 20


def retry_delay(attempts: int) -> timedelta:
    """30 s after the first failure, doubling each time, at most an hour."""
    return timedelta(seconds=min(30 * 2 ** (attempts - 1), 3600))


def message(row: Row[Any], sender: str) -> EmailMessage:
    email = EmailMessage()
    email["From"] = sender
    email["To"] = ", ".join(row.to_addresses)
    if row.cc_addresses:
        email["Cc"] = ", ".join(row.cc_addresses)
    email["Subject"] = row.subject
    # The same outbox row always gets the same Message-ID, so a resend is recognisably a repeat.
    email["Message-ID"] = (
        f"<{hashlib.sha256(row.idempotency_key.encode()).hexdigest()[:32]}@infrawatch>"
    )
    email.set_content(row.body)
    return email


def smtp_sender() -> Send:
    """SMTP from the environment: Mailpit by default; a real provider needs only settings."""
    host = os.environ.get("SMTP_HOST", "mailpit")
    port = int(os.environ.get("SMTP_PORT", "1025"))
    username = os.environ.get("SMTP_USERNAME")
    password = os.environ.get("SMTP_PASSWORD", "")

    def send(email: EmailMessage) -> None:
        with smtplib.SMTP(host, port, timeout=10) as smtp:
            if username:
                smtp.starttls()
                smtp.login(username, password)
            smtp.send_message(email)

    return send


async def deliver(conn: AsyncConnection, send: Send, sender: str) -> int:
    """Send what is due; return how many went out. Rows stay locked until this transaction ends."""
    rows = await conn.execute(
        text(
            "SELECT * FROM outbox WHERE sent_at IS NULL AND next_attempt_at <= now() "
            "ORDER BY id LIMIT :batch FOR UPDATE SKIP LOCKED"
        ),
        {"batch": BATCH},
    )
    sent = 0
    for row in rows.all():
        try:
            await asyncio.to_thread(send, message(row, sender))
        except (OSError, smtplib.SMTPException) as error:
            await conn.execute(
                text(
                    "UPDATE outbox SET attempts = attempts + 1, last_error = :error, "
                    "next_attempt_at = now() + :delay WHERE id = :id"
                ),
                {"id": row.id, "error": str(error)[:500], "delay": retry_delay(row.attempts + 1)},
            )
            continue
        await conn.execute(
            text(
                "UPDATE outbox SET attempts = attempts + 1, sent_at = now(), last_error = NULL "
                "WHERE id = :id"
            ),
            {"id": row.id},
        )
        sent += 1
    return sent
