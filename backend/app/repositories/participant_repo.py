from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import sqlite3


class ParticipantRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def find_auth_token(self, token: str) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT token, participant_id, expires_at
            FROM auth_tokens
            WHERE token = ?
            """,
            (token,),
        ).fetchone()

    def create_session(self, participant_id: str) -> tuple[str, str]:
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        now = datetime.now(UTC)
        expires_at = now + timedelta(days=14)
        session_id = str(uuid4())
        self.connection.execute(
            """
            INSERT INTO device_sessions (
                id, participant_id, session_token_hash, expires_at, revoked_at, created_at
            ) VALUES (?, ?, ?, ?, NULL, ?)
            """,
            (
                session_id,
                participant_id,
                token_hash,
                expires_at.isoformat(),
                now.isoformat(),
            ),
        )
        return raw_token, participant_id

    def find_active_session(self, raw_token: str) -> sqlite3.Row | None:
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        row = self.connection.execute(
            """
            SELECT participant_id, expires_at, revoked_at
            FROM device_sessions
            WHERE session_token_hash = ?
            """,
            (token_hash,),
        ).fetchone()
        if row is None:
            return None
        now = datetime.now(UTC)
        expires_at = datetime.fromisoformat(row["expires_at"])
        if row["revoked_at"] is not None or expires_at <= now:
            return None
        return row
