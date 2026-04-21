from __future__ import annotations

import hashlib
import os
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "stamp_rally.db"
DB_PATH = Path(os.environ.get("STAMP_RALLY_DB_PATH", str(DEFAULT_DB_PATH)))


def set_db_path(path: str) -> None:
    global DB_PATH
    DB_PATH = Path(path)


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def _seed_participant_and_token(connection: sqlite3.Connection) -> None:
    participant_count = connection.execute(
        "SELECT COUNT(*) FROM participants"
    ).fetchone()[0]
    if participant_count > 0:
        return

    now = datetime.now(UTC)
    participant_id = "participant-demo-001"
    email_hash = hashlib.sha256("demo.user@imsgroup.local".encode()).hexdigest()
    connection.execute(
        "INSERT INTO participants (id, email_hash, created_at) VALUES (?, ?, ?)",
        (participant_id, email_hash, now.isoformat()),
    )
    connection.execute(
        """
        INSERT INTO auth_tokens (token, participant_id, expires_at, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            "demo-auth-token",
            participant_id,
            (now + timedelta(days=30)).isoformat(),
            now.isoformat(),
        ),
    )


def _seed_venues(connection: sqlite3.Connection) -> None:
    venue_count = connection.execute("SELECT COUNT(*) FROM venues").fetchone()[0]
    if venue_count > 0:
        return
    now = datetime.now(UTC)
    active_until = now + timedelta(days=60)
    connection.executemany(
        """
        INSERT INTO venues (
            id, code, name, location, lat, lon, radius_m, active_from, active_until
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "venue-tokyo",
                "IMS-TOKYO",
                "東京タワー会場",
                "東京都港区",
                35.6586,
                139.7454,
                300.0,
                now.isoformat(),
                active_until.isoformat(),
            ),
            (
                "venue-osaka",
                "IMS-OSAKA",
                "大阪城会場",
                "大阪府大阪市",
                34.6873,
                135.5262,
                300.0,
                now.isoformat(),
                active_until.isoformat(),
            ),
            (
                "venue-hakodate",
                "IMS-HAKODATE",
                "函館山会場",
                "北海道函館市",
                41.7597,
                140.7042,
                350.0,
                now.isoformat(),
                active_until.isoformat(),
            ),
        ],
    )


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS participants (
                id TEXT PRIMARY KEY,
                email_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS auth_tokens (
                token TEXT PRIMARY KEY,
                participant_id TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (participant_id) REFERENCES participants (id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS device_sessions (
                id TEXT PRIMARY KEY,
                participant_id TEXT NOT NULL,
                session_token_hash TEXT NOT NULL UNIQUE,
                expires_at TEXT NOT NULL,
                revoked_at TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (participant_id) REFERENCES participants (id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS venues (
                id TEXT PRIMARY KEY,
                code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                radius_m REAL NOT NULL,
                active_from TEXT NOT NULL,
                active_until TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS stamp_records (
                id TEXT PRIMARY KEY,
                participant_id TEXT NOT NULL,
                venue_id TEXT NOT NULL,
                stamped_at TEXT NOT NULL,
                source TEXT NOT NULL,
                FOREIGN KEY (participant_id) REFERENCES participants (id),
                FOREIGN KEY (venue_id) REFERENCES venues (id),
                UNIQUE (participant_id, venue_id)
            )
            """
        )

        _seed_participant_and_token(connection)
        _seed_venues(connection)
