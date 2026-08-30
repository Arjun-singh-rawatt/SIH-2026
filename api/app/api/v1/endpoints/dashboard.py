"""Executive Dashboard analytics endpoints."""

from fastapi import APIRouter, Depends
from app.api.deps import get_dashboard_service
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardOverview

router = APIRouter(prefix="/dashboard", tags=["Executive Dashboard"])


@router.get(
    "/overview",
    response_model=DashboardOverview,
    summary="Get Executive Safety Dashboard Overview",
)
async def get_dashboard_overview(
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardOverview:
    """Retrieve full multidimensional safety metrics including SIF density, trends,
    facility risk rankings, precursor distributions, and barrier failure modes.
    """
    return await service.get_overview()
