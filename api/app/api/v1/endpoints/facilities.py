"""Facility performance profiles and statistics endpoints."""

from typing import List
from fastapi import APIRouter, Depends, status
from app.api.deps import get_facility_service
from app.services.facility_service import FacilityService
from app.schemas.facility import FacilityRead, FacilityCreate, FacilityUpdate, FacilityStats

router = APIRouter(prefix="/facilities", tags=["Operational Facilities"])


@router.get(
    "",
    response_model=List[FacilityRead],
    summary="List Operational Facilities",
)
async def list_facilities(
    service: FacilityService = Depends(get_facility_service),
) -> List[FacilityRead]:
    """Retrieve all active OIL production, drilling, gathering, and hub installations."""
    return await service.list_facilities()


@router.get(
    "/{facility_id}",
    response_model=FacilityRead,
    summary="Get Facility Details",
)
async def get_facility(
    facility_id: str,
    service: FacilityService = Depends(get_facility_service),
) -> FacilityRead:
    """Retrieve specific facility metadata and classification."""
    return await service.get_facility_by_id(facility_id)


@router.get(
    "/{facility_id}/stats",
    response_model=FacilityStats,
    summary="Get Facility Safety KPI Statistics",
)
async def get_facility_stats(
    facility_id: str,
    service: FacilityService = Depends(get_facility_service),
) -> FacilityStats:
    """Calculate live SIF precursor density, high-urgency volume, and predominant failure modes for facility."""
    return await service.get_facility_stats(facility_id)


@router.post(
    "",
    response_model=FacilityRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register New Operational Facility",
)
async def create_facility(
    payload: FacilityCreate,
    service: FacilityService = Depends(get_facility_service),
) -> FacilityRead:
    """Register a new production site or drilling hub."""
    return await service.create_facility(payload)


@router.patch(
    "/{facility_id}",
    response_model=FacilityRead,
    summary="Update Facility Information",
)
async def update_facility(
    facility_id: str,
    payload: FacilityUpdate,
    service: FacilityService = Depends(get_facility_service),
) -> FacilityRead:
    """Update metadata or active headcount on a facility."""
    return await service.update_facility(facility_id, payload)
