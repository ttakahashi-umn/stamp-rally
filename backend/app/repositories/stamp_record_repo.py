from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import sqlite3


class StampRecordRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def find_by_participant_and_venue(
        self, participant_id: str, venue_id: str
    ) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT id, participant_id, venue_id, stamped_at
            FROM stamp_records
            WHERE participant_id = ? AND venue_id = ?
            """,
            (participant_id, venue_id),
        ).fetchone()

    def insert(self, participant_id: str, venue_id: str, source: str) -> str:
        record_id = str(uuid4())
        self.connection.execute(
            """
            INSERT INTO stamp_records (id, participant_id, venue_id, stamped_at, source)
            VALUES (?, ?, ?, ?, ?)
            """,
            (record_id, participant_id, venue_id, datetime.now(UTC).isoformat(), source),
        )
        return record_id

    def list_by_participant(self, participant_id: str) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT venue_id
            FROM stamp_records
            WHERE participant_id = ?
            """,
            (participant_id,),
        ).fetchall()
