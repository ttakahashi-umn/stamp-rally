from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient  # type: ignore[import-not-found]

from app.db import get_connection, init_db, set_db_path  # type: ignore[import-not-found]
from app.main import app  # type: ignore[import-not-found]
from app.repositories.stamp_record_repo import StampRecordRepository  # type: ignore[import-not-found]
from app.repositories.venue_repo import VenueRepository  # type: ignore[import-not-found]
from app.stamp_service import StampService  # type: ignore[import-not-found]


def _prepare_db(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    set_db_path(str(db_file))
    init_db()


def _activate(client: TestClient) -> str:
    response = client.post("/api/auth/activate", json={"token": "demo-auth-token"})
    assert response.status_code == 200
    return response.json()["session_token"]


def _signed_payload(venue_code: str) -> str:
    with get_connection() as connection:
        service = StampService(VenueRepository(connection), StampRecordRepository(connection))
        return service.create_payload(
            venue_code=venue_code,
            expires_unix=int(
                (datetime.now(timezone.utc) + timedelta(minutes=10)).timestamp()
            ),
        )


def test_activate_and_progress(tmp_path: Path) -> None:
    _prepare_db(tmp_path)
    client = TestClient(app)
    session_token = _activate(client)

    progress_response = client.get(
        "/api/stamps/progress", headers={"Authorization": session_token}
    )
    assert progress_response.status_code == 200
    body = progress_response.json()
    assert body["total"] == 3
    assert body["completed"] == 0
    assert len(body["items"]) == 3


def test_scan_success_duplicate_and_geofence_reject(tmp_path: Path) -> None:
    _prepare_db(tmp_path)
    client = TestClient(app)
    session_token = _activate(client)
    payload = _signed_payload("IMS-TOKYO")

    success = client.post(
        "/api/stamps/scan",
        headers={"Authorization": session_token},
        json={
            "qr_payload": payload,
            "latitude": 35.6586,
            "longitude": 139.7454,
        },
    )
    assert success.status_code == 200
    assert success.json()["status"] == "stamped"

    duplicate = client.post(
        "/api/stamps/scan",
        headers={"Authorization": session_token},
        json={
            "qr_payload": payload,
            "latitude": 35.6586,
            "longitude": 139.7454,
        },
    )
    assert duplicate.status_code == 200
    assert duplicate.json()["status"] == "already_stamped"

    osaka_payload = _signed_payload("IMS-OSAKA")
    geofence_error = client.post(
        "/api/stamps/scan",
        headers={"Authorization": session_token},
        json={
            "qr_payload": osaka_payload,
            "latitude": 35.6586,
            "longitude": 139.7454,
        },
    )
    assert geofence_error.status_code == 403
