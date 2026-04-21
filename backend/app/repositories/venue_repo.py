from __future__ import annotations

from datetime import UTC, datetime

import sqlite3


class VenueRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def find_by_code(self, code: str) -> sqlite3.Row | None:
        row = self.connection.execute(
            """
            SELECT
                id, code, name, location, lat, lon, radius_m,
                active_from, active_until, geofence_enabled
            FROM venues
            WHERE code = ?
            """,
            (code,),
        ).fetchone()
        if row is None:
            return None
        now = datetime.now(UTC)
        active_from = datetime.fromisoformat(row["active_from"])
        active_until = datetime.fromisoformat(row["active_until"])
        if now < active_from or now > active_until:
            return None
        return row

    def list_all(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT id, code, name, location, image_url, description
            FROM venues
            ORDER BY code
            """
        ).fetchall()
