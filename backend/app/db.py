from __future__ import annotations

import csv
import hashlib
import os
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent
DEFAULT_DB_PATH = BASE_DIR / "stamp_rally.db"
DB_PATH = Path(os.environ.get("STAMP_RALLY_DB_PATH", str(DEFAULT_DB_PATH)))
FACILITIES_CSV_PATH = Path(
    os.environ.get("STAMP_FACILITIES_CSV_PATH", str(REPO_ROOT / "data" / "facilities.csv"))
)


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
    if not FACILITIES_CSV_PATH.exists():
        return
    with FACILITIES_CSV_PATH.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for index, row in enumerate(reader, start=1):
            name = (row.get("施設名") or row.get("会場名") or "").strip()
            location = (row.get("住所") or "").strip()
            specialty = (row.get("特産品") or "").strip()
            if not name or not location:
                continue
            venue_id = f"venue-csv-{index:04d}"
            code = f"FAC-{index:04d}"
            lat = _parse_float(
                row.get("緯度")
                or row.get("lat")
                or row.get("latitude")
            )
            lon = _parse_float(
                row.get("経度")
                or row.get("lon")
                or row.get("lng")
                or row.get("longitude")
            )
            radius = _parse_float(row.get("半径") or row.get("radius_m")) or 300.0
            geofence_enabled = 1 if lat is not None and lon is not None else 0
            lat_value = lat if lat is not None else 0.0
            lon_value = lon if lon is not None else 0.0
            now = datetime.now(UTC)
            active_until = now + timedelta(days=3650)
            connection.execute(
                """
                INSERT INTO venues (
                    id, code, name, location, lat, lon, radius_m,
                    active_from, active_until, image_url, description, geofence_enabled
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(code) DO UPDATE SET
                    name = excluded.name,
                    location = excluded.location,
                    lat = excluded.lat,
                    lon = excluded.lon,
                    radius_m = excluded.radius_m,
                    image_url = excluded.image_url,
                    description = excluded.description,
                    geofence_enabled = excluded.geofence_enabled
                """,
                (
                    venue_id,
                    code,
                    name,
                    location,
                    lat_value,
                    lon_value,
                    radius,
                    now.isoformat(),
                    active_until.isoformat(),
                    f"/stamps/{code}.png",
                    specialty,
                    geofence_enabled,
                ),
            )


def _seed_demo_stamps(connection: sqlite3.Connection) -> None:
    participant_id = "participant-demo-001"
    participant = connection.execute(
        "SELECT id FROM participants WHERE id = ?",
        (participant_id,),
    ).fetchone()
    if participant is None:
        return

    target_codes = (
        "FAC-0001",
        "FAC-0002",
        "FAC-0003",
        "FAC-0004",
        "FAC-0073",
        "FAC-0074",
    )
    placeholders = ",".join("?" for _ in target_codes)
    venues = connection.execute(
        """
        SELECT id, code
        FROM venues
        WHERE code IN ({placeholders})
        ORDER BY code
        """.format(placeholders=placeholders),
        target_codes,
    ).fetchall()
    if not venues:
        return

    now = datetime.now(UTC).isoformat()
    for row in venues:
        venue_id = str(row["id"])
        stamp_id = f"seed-{participant_id}-{venue_id}"
        connection.execute(
            """
            INSERT OR IGNORE INTO stamp_records (
                id, participant_id, venue_id, stamped_at, source
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (stamp_id, participant_id, venue_id, now, "seed"),
        )


def _parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


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
        venue_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(venues)").fetchall()
        }
        if "image_url" not in venue_columns:
            connection.execute("ALTER TABLE venues ADD COLUMN image_url TEXT")
        if "description" not in venue_columns:
            connection.execute("ALTER TABLE venues ADD COLUMN description TEXT")
        if "geofence_enabled" not in venue_columns:
            connection.execute(
                "ALTER TABLE venues ADD COLUMN geofence_enabled INTEGER NOT NULL DEFAULT 0"
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
        _seed_demo_stamps(connection)
