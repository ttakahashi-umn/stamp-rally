from __future__ import annotations

import hmac
import math
import os
from datetime import datetime, timezone
from hashlib import sha256

from fastapi import HTTPException, status  # type: ignore[import-not-found]

from .repositories.stamp_record_repo import StampRecordRepository
from .repositories.venue_repo import VenueRepository


class StampService:
    def __init__(
        self, venue_repo: VenueRepository, record_repo: StampRecordRepository
    ) -> None:
        self.venue_repo = venue_repo
        self.record_repo = record_repo
        self.secret = os.environ.get("STAMP_QR_SECRET", "stamp-rally-dev-secret")

    def create_payload(self, venue_code: str, expires_unix: int) -> str:
        payload = f"{venue_code}:{expires_unix}"
        signature = hmac.new(
            self.secret.encode(), payload.encode(), digestmod=sha256
        ).hexdigest()
        return f"{payload}:{signature}"

    def scan(
        self, participant_id: str, qr_payload: str, latitude: float, longitude: float
    ) -> tuple[str, str, str]:
        venue_code = self._verify_payload(qr_payload)
        venue = self.venue_repo.find_by_code(venue_code)
        if venue is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="会場情報が無効です"
            )

        if int(venue["geofence_enabled"]):
            if not self._inside_radius(
                latitude,
                longitude,
                float(venue["lat"]),
                float(venue["lon"]),
                float(venue["radius_m"]),
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="会場付近で再試行してください",
                )

        existing = self.record_repo.find_by_participant_and_venue(
            participant_id, str(venue["id"])
        )
        if existing is not None:
            return "already_stamped", str(existing["id"]), "既に取得済みです"

        record_id = self.record_repo.insert(participant_id, str(venue["id"]), "qr")
        return "stamped", record_id, "スタンプを獲得しました"

    def _verify_payload(self, qr_payload: str) -> str:
        parts = qr_payload.split(":")
        if len(parts) != 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="QR形式が不正です",
            )
        venue_code, expires_raw, signature = parts
        payload = f"{venue_code}:{expires_raw}"
        expected = hmac.new(
            self.secret.encode(), payload.encode(), digestmod=sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="署名が不正です",
            )
        try:
            expires_unix = int(expires_raw)
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="QR期限が不正です",
            ) from error
        if datetime.fromtimestamp(expires_unix, timezone.utc) <= datetime.now(
            timezone.utc
        ):
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="QRの有効期限が切れています",
            )
        return venue_code

    @staticmethod
    def _inside_radius(
        user_lat: float,
        user_lon: float,
        target_lat: float,
        target_lon: float,
        radius_m: float,
    ) -> bool:
        earth_radius = 6371000.0
        lat1 = math.radians(user_lat)
        lat2 = math.radians(target_lat)
        dlat = lat2 - lat1
        dlon = math.radians(target_lon - user_lon)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = earth_radius * c
        return distance <= radius_m
