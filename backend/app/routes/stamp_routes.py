from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, status  # type: ignore[import-not-found]

from ..auth_service import AuthService
from ..db import get_connection
from ..models import ProgressResponse, ScanRequest, ScanResponse
from ..progress_service import ProgressService
from ..repositories.participant_repo import ParticipantRepository
from ..repositories.stamp_record_repo import StampRecordRepository
from ..repositories.venue_repo import VenueRepository
from ..stamp_service import StampService

router = APIRouter(prefix="/api/stamps", tags=["stamps"])


def _participant_id_from_header(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
        )
    with get_connection() as connection:
        auth_service = AuthService(ParticipantRepository(connection))
        return auth_service.verify_session(authorization)


@router.post("/scan", response_model=ScanResponse)
def scan(
    payload: ScanRequest,
    authorization: str | None = Header(default=None),
) -> ScanResponse:
    participant_id = _participant_id_from_header(authorization)
    with get_connection() as connection:
        stamp_service = StampService(
            VenueRepository(connection),
            StampRecordRepository(connection),
        )
        status_value, stamp_id, message = stamp_service.scan(
            participant_id, payload.qr_payload, payload.latitude, payload.longitude
        )
    return ScanResponse(status=status_value, stamp_id=stamp_id, message=message)


@router.get("/progress", response_model=ProgressResponse)
def progress(authorization: str | None = Header(default=None)) -> ProgressResponse:
    participant_id = _participant_id_from_header(authorization)
    with get_connection() as connection:
        service = ProgressService(
            VenueRepository(connection), StampRecordRepository(connection)
        )
        return service.get_progress(participant_id)
