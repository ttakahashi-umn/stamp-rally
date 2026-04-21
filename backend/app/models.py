from __future__ import annotations

from pydantic import BaseModel, Field  # type: ignore[import-not-found]


class ActivateRequest(BaseModel):
    token: str = Field(min_length=1)
    device_label: str | None = None


class ActivateResponse(BaseModel):
    session_token: str
    participant_id: str


class SessionResponse(BaseModel):
    participant_id: str
    active: bool


class ScanRequest(BaseModel):
    qr_payload: str = Field(min_length=1)
    latitude: float
    longitude: float


class ScanResponse(BaseModel):
    status: str
    stamp_id: str | None = None
    message: str


class ProgressItem(BaseModel):
    venue_id: str
    code: str
    name: str
    location: str
    completed: bool


class ProgressResponse(BaseModel):
    total: int
    completed: int
    items: list[ProgressItem]
