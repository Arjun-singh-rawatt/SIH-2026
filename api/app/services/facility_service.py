"""Facility management and performance profile service."""

from typing import List, Optional
from app.db.repositories.facility_repo import FacilityRepository
from app.db.models.facility import Facility
from app.schemas.facility import FacilityRead, FacilityCreate, FacilityUpdate, FacilityStats
from app.core.errors import FacilityNotFoundException


class FacilityService:
    def __init__(self, facility_repo: FacilityRepository):
        self.repo = facility_repo

    async def list_facilities(self) -> List[FacilityRead]:
        facilities = await self.repo.get_all_active()
        return [FacilityRead.model_validate(f) for f in facilities]

    async def get_facility_by_id(self, identifier: str) -> FacilityRead:
        fac = await self.repo.get_by_facility_id(identifier)
        if not fac:
            raise FacilityNotFoundException(identifier)
        return FacilityRead.model_validate(fac)

    async def get_facility_stats(self, identifier: str) -> FacilityStats:
        stats = await self.repo.get_facility_stats(identifier)
        if not stats:
            raise FacilityNotFoundException(identifier)
        return FacilityStats(**stats)

    async def create_facility(self, payload: FacilityCreate) -> FacilityRead:
        fac = Facility(
            facility_id=payload.facility_id,
            name=payload.name,
            short_name=payload.short_name,
            region=payload.region,
            type=payload.type,
            location_description=payload.location_description,
            latitude=payload.latitude,
            longitude=payload.longitude,
            active_personnel=payload.active_personnel,
            manager=payload.manager,
            active=payload.active,
        )
        created = await self.repo.create(fac)
        return FacilityRead.model_validate(created)

    async def update_facility(self, identifier: str, payload: FacilityUpdate) -> FacilityRead:
        fac = await self.repo.get_by_facility_id(identifier)
        if not fac:
            raise FacilityNotFoundException(identifier)

        update_data = payload.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(fac, k, v)

        updated = await self.repo.update(fac)
        return FacilityRead.model_validate(updated)
