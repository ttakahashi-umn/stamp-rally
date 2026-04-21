from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, status

from ..auth_service import AuthService
from ..db import get_connection
from ..models import ActivateRequest, ActivateResponse, SessionResponse
from ..repositories.participant_repo import ParticipantRepository

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/activate", response_model=ActivateResponse)
def activate(payload: ActivateRequest) -> ActivateResponse:
    with get_connection() as connection:
        service = AuthService(ParticipantRepository(connection))
        session_token, participant_id = service.activate(payload.token)
    return ActivateResponse(session_token=session_token, participant_id=participant_id)


@router.get("/session", response_model=SessionResponse)
def session(
    authorization: str | None = Header(default=None),
) -> SessionResponse:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header is required"
        )
    with get_connection() as connection:
        service = AuthService(ParticipantRepository(connection))
        participant_id = service.verify_session(authorization)
    return SessionResponse(participant_id=participant_id, active=True)
