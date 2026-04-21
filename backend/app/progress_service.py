from __future__ import annotations

from .models import ProgressItem, ProgressResponse
from .repositories.stamp_record_repo import StampRecordRepository
from .repositories.venue_repo import VenueRepository


class ProgressService:
    def __init__(
        self, venue_repo: VenueRepository, record_repo: StampRecordRepository
    ) -> None:
        self.venue_repo = venue_repo
        self.record_repo = record_repo

    def get_progress(self, participant_id: str) -> ProgressResponse:
        venues = self.venue_repo.list_all()
        stamped_rows = self.record_repo.list_by_participant(participant_id)
        stamped_set = {str(row["venue_id"]) for row in stamped_rows}
        items = [
            ProgressItem(
                venue_id=str(venue["id"]),
                code=str(venue["code"]),
                name=str(venue["name"]),
                location=str(venue["location"]),
                completed=str(venue["id"]) in stamped_set,
            )
            for venue in venues
        ]
        completed = len([item for item in items if item.completed])
        return ProgressResponse(total=len(items), completed=completed, items=items)
