from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status  # type: ignore[import-not-found]

from .repositories.participant_repo import ParticipantRepository


class AuthService:
    def __init__(self, participant_repo: ParticipantRepository) -> None:
        self.participant_repo = participant_repo

    def activate(self, auth_token: str) -> tuple[str, str]:
        token_row = self.participant_repo.find_auth_token(auth_token)
        if token_row is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無効な認証トークンです",
            )

        expires_at = datetime.fromisoformat(token_row["expires_at"])
        if expires_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="認証トークンの期限が切れています",
            )

        return self.participant_repo.create_session(token_row["participant_id"])

    def verify_session(self, session_token: str) -> str:
        session_row = self.participant_repo.find_active_session(session_token)
        if session_row is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="認証セッションが無効です",
            )
        return str(session_row["participant_id"])
